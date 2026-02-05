import streamlit as st
from uuid import uuid4
from utils.url_parser import validate_url, detect_platform, parse_url_file, clean_url
from core.models import Platform

st.header("Carga de URLs para Analisis")

# Inicializar cola de URLs en session state
if "url_queue" not in st.session_state:
    st.session_state.url_queue = []

# --- Seccion de entrada ---
col_single, col_bulk = st.columns(2)

with col_single:
    st.subheader("URL Individual")
    with st.form("single_url_form", clear_on_submit=True):
        single_url = st.text_input(
            "Pega la URL de la publicacion",
            placeholder="https://www.instagram.com/p/...",
        )
        add_single = st.form_submit_button("Agregar URL", use_container_width=True)

    if add_single and single_url:
        url = clean_url(single_url)
        if validate_url(url):
            platform = detect_platform(url)
            st.session_state.url_queue.append({
                "id": str(uuid4())[:8],
                "url": url,
                "platform": platform.value,
            })
            st.toast(f"URL agregada: {platform.value}")
        else:
            st.error("URL no valida. Verifica el formato.")

with col_bulk:
    st.subheader("Carga Masiva")
    uploaded_file = st.file_uploader(
        "Sube un archivo CSV o Excel con URLs",
        type=["csv", "xlsx", "xls"],
        help="El archivo debe tener las URLs en la primera columna.",
    )
    if uploaded_file is not None:
        if st.button("Procesar Archivo", use_container_width=True):
            urls = parse_url_file(uploaded_file)
            if urls:
                added = 0
                for url in urls:
                    platform = detect_platform(url)
                    st.session_state.url_queue.append({
                        "id": str(uuid4())[:8],
                        "url": url,
                        "platform": platform.value,
                    })
                    added += 1
                st.toast(f"{added} URLs agregadas desde el archivo.")
            else:
                st.warning("No se encontraron URLs validas en el archivo.")

# --- Cola de URLs ---
st.markdown("---")
st.subheader(f"Cola de URLs ({len(st.session_state.url_queue)})")

if st.session_state.url_queue:
    # Botones de accion
    col_action1, col_action2, col_action3 = st.columns([2, 2, 6])
    with col_action1:
        start_processing = st.button(
            "Iniciar Captura y Analisis",
            type="primary",
            use_container_width=True,
            disabled=st.session_state.get("processing", False),
        )
    with col_action2:
        if st.button("Limpiar Cola", use_container_width=True):
            st.session_state.url_queue = []
            st.rerun()

    # Mostrar tabla de URLs
    st.markdown("")
    for i, item in enumerate(st.session_state.url_queue):
        col_idx, col_url, col_plat, col_del = st.columns([1, 7, 2, 1])
        with col_idx:
            st.markdown(f"**{i + 1}**")
        with col_url:
            st.text(item["url"][:80])
        with col_plat:
            platform_colors = {
                "instagram": "🟣 Instagram",
                "facebook": "🔵 Facebook",
                "twitter": "🔵 X/Twitter",
                "tiktok": "⚫ TikTok",
                "unknown": "⚪ Otro",
            }
            st.markdown(platform_colors.get(item["platform"], "⚪ Otro"))
        with col_del:
            if st.button("✕", key=f"del_{item['id']}"):
                st.session_state.url_queue = [
                    q for q in st.session_state.url_queue if q["id"] != item["id"]
                ]
                st.rerun()

    # --- Procesamiento ---
    if start_processing:
        from core.database import init_db, save_post, load_config
        from capture.capture_service import CaptureService
        from analysis.analyzer import ComplianceAnalyzer, create_vision_client
        from core.models import ComplianceStatus

        init_db()
        config = load_config()
        batch_id = str(uuid4())
        st.session_state.current_batch_id = batch_id
        st.session_state.processing = True

        total = len(st.session_state.url_queue)
        progress_bar = st.progress(0, text="Iniciando captura...")
        status_text = st.empty()

        # Fase 1: Captura (ejecutada en thread separado por compatibilidad Windows)
        capture_service = CaptureService()
        url_list = [
            (item["url"], Platform(item["platform"]))
            for item in st.session_state.url_queue
        ]

        progress_bar.progress(0.1, text=f"Capturando {total} publicaciones (esto puede tardar)...")
        captured_posts = capture_service.capture_batch(url_list)
        progress_bar.progress(0.5, text="Captura completada. Iniciando analisis...")

        # Asignar batch_id
        for post in captured_posts:
            post.batch_id = batch_id

        # Fase 2: Analisis IA (usa el backend configurado: Gemini o Ollama)
        try:
            vision_client = create_vision_client(config)
            backend_name = config.ai_backend.value.capitalize()
            model_name = config.ollama_model if config.ai_backend.value == "ollama" else config.gemini_model
            status_text.info(f"Usando {backend_name} ({model_name}) para el analisis...")

            analyzer = ComplianceAnalyzer(vision_client)

            def analysis_progress(pct, msg):
                progress_bar.progress(0.5 + pct * 0.5, text=msg)

            analyzed_posts = analyzer.analyze_batch(
                captured_posts, config, progress_callback=analysis_progress
            )
        except Exception as e:
            st.warning(f"No se pudo inicializar el motor de IA: {e}. Se omite el analisis.")
            analyzed_posts = captured_posts

        # Guardar en DB
        for post in analyzed_posts:
            save_post(post)

        st.session_state.posts = analyzed_posts
        st.session_state.processing = False
        st.session_state.url_queue = []

        progress_bar.progress(1.0, text="Procesamiento completado")

        # Mostrar resumen rapido
        ok = sum(1 for p in analyzed_posts if p.status == ComplianceStatus.CUMPLE)
        fail = sum(1 for p in analyzed_posts if p.status == ComplianceStatus.NO_CUMPLE)
        err = sum(1 for p in analyzed_posts if p.status == ComplianceStatus.ERROR)
        st.success(
            f"Se procesaron {len(analyzed_posts)} publicaciones: "
            f"{ok} cumplen, {fail} no cumplen, {err} con error. "
            "Ve al Dashboard o la Galeria para ver los resultados."
        )
        st.balloons()

else:
    st.info("Agrega URLs usando el campo individual o cargando un archivo CSV/Excel.")
