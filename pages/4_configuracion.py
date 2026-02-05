import streamlit as st
from core.database import init_db, save_config, load_config
from core.models import ComplianceConfig, AIBackend
from config.settings import DEFAULT_HASHTAGS, DEFAULT_TONE_KEYWORDS_EMOTIVO, DEFAULT_TONE_KEYWORDS_INFORMATIVO

init_db()

st.header("Configuracion de Cumplimiento")
st.caption("Define los lineamientos que se usaran para evaluar las publicaciones.")

# Cargar configuracion actual
config = load_config()

# Si no hay config guardada, usar defaults
if not config.required_hashtags and not config.emotional_keywords:
    config = ComplianceConfig(
        required_hashtags=DEFAULT_HASHTAGS,
        emotional_keywords=DEFAULT_TONE_KEYWORDS_EMOTIVO,
        informational_keywords=DEFAULT_TONE_KEYWORDS_INFORMATIVO,
    )

# === Seccion: Motor de IA (fuera del form para permitir interactividad) ===
st.subheader("Motor de Analisis IA")

backend_options = {"Gemini (API Cloud)": "gemini", "Ollama (Local)": "ollama"}
backend_labels = {v: k for k, v in backend_options.items()}
current_backend_label = backend_labels.get(config.ai_backend.value, "Gemini (API Cloud)")

selected_backend_label = st.radio(
    "Selecciona el motor de vision",
    options=list(backend_options.keys()),
    index=list(backend_options.keys()).index(current_backend_label),
    horizontal=True,
)
selected_backend = backend_options[selected_backend_label]

# Opciones segun backend
if selected_backend == "ollama":
    col_url, col_model = st.columns(2)
    with col_url:
        ollama_url = st.text_input(
            "URL de Ollama",
            value=config.ollama_url,
            help="URL donde corre Ollama (por defecto http://localhost:11434)",
        )
    with col_model:
        # Intentar listar modelos disponibles
        from analysis.ollama_client import OllamaClient

        available_models = OllamaClient.list_models(ollama_url)
        if available_models:
            # Filtrar modelos con capacidad de vision
            vision_hint = [m for m in available_models if any(
                v in m.lower() for v in ["vision", "llava", "moondream", "bakllava"]
            )]
            all_options = vision_hint + [m for m in available_models if m not in vision_hint]

            default_idx = 0
            if config.ollama_model in all_options:
                default_idx = all_options.index(config.ollama_model)

            ollama_model = st.selectbox(
                "Modelo de Ollama",
                options=all_options,
                index=default_idx,
                help="Modelos con vision aparecen primero",
            )
        else:
            ollama_model = st.text_input(
                "Modelo de Ollama",
                value=config.ollama_model,
                help="Ej: llama3.2-vision, llava, moondream",
            )

    # Verificar conexion
    is_connected = OllamaClient.check_connection(ollama_url)
    if is_connected:
        st.success(f"Ollama conectado en {ollama_url}")
    else:
        st.error(
            f"No se pudo conectar a Ollama en {ollama_url}. "
            "Asegurate de que Ollama este corriendo (`ollama serve`)."
        )
    gemini_model = config.gemini_model
else:
    ollama_url = config.ollama_url
    ollama_model = config.ollama_model
    gemini_model = st.text_input(
        "Modelo de Gemini",
        value=config.gemini_model,
        help="Ej: gemini-2.0-flash, gemini-1.5-pro",
    )
    import os
    if os.getenv("GEMINI_API_KEY"):
        st.success("GEMINI_API_KEY configurada")
    else:
        st.warning("GEMINI_API_KEY no encontrada en el archivo .env")

st.markdown("---")

# === Form de lineamientos ===
with st.form("config_form"):
    st.subheader("Hashtags Obligatorios")
    st.caption("Los hashtags que todas las publicaciones deben incluir. Uno por linea.")
    hashtags_text = st.text_area(
        "Hashtags",
        value="\n".join(config.required_hashtags),
        height=120,
        label_visibility="collapsed",
    )

    st.markdown("---")

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Palabras Clave - Tono Emotivo")
        st.caption("Palabras que indican un tono emotivo en la comunicacion.")
        emotivo_text = st.text_area(
            "Emotivo",
            value="\n".join(config.emotional_keywords),
            height=150,
            label_visibility="collapsed",
        )

    with col2:
        st.subheader("Palabras Clave - Tono Informativo")
        st.caption("Palabras que indican un tono informativo.")
        informativo_text = st.text_area(
            "Informativo",
            value="\n".join(config.informational_keywords),
            height=150,
            label_visibility="collapsed",
        )

    st.markdown("---")

    st.subheader("Notas del Manual de Marca")
    st.caption("Instrucciones adicionales para el analisis de cumplimiento de marca.")
    brand_notes = st.text_area(
        "Notas",
        value=config.brand_guidelines_notes,
        height=120,
        placeholder="Ej: El logo debe estar en la esquina superior derecha. Usar colores institucionales azul (#003DA5) y blanco.",
        label_visibility="collapsed",
    )

    submitted = st.form_submit_button("Guardar Configuracion", use_container_width=True, type="primary")

    if submitted:
        new_config = ComplianceConfig(
            required_hashtags=[
                h.strip() for h in hashtags_text.strip().split("\n") if h.strip()
            ],
            emotional_keywords=[
                k.strip() for k in emotivo_text.strip().split("\n") if k.strip()
            ],
            informational_keywords=[
                k.strip() for k in informativo_text.strip().split("\n") if k.strip()
            ],
            brand_guidelines_notes=brand_notes.strip(),
            ai_backend=AIBackend(selected_backend),
            ollama_model=ollama_model,
            ollama_url=ollama_url,
            gemini_model=gemini_model,
        )
        save_config(new_config)
        st.session_state.config = new_config
        st.success("Configuracion guardada exitosamente.")
