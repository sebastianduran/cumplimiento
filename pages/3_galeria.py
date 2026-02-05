import streamlit as st
from pathlib import Path
from core.database import init_db, get_all_posts
from core.models import ComplianceStatus

init_db()

st.header("Galeria de Publicaciones")

posts = get_all_posts()

if not posts:
    st.info("No hay publicaciones analizadas. Ve a 'Carga de URLs' para comenzar.")
    st.stop()

# Filtro rapido
filter_status = st.selectbox(
    "Filtrar por estado",
    ["Todos", "cumple", "no-cumple", "error"],
    key="gallery_filter",
)

filtered = posts
if filter_status != "Todos":
    filtered = [p for p in filtered if p.status.value == filter_status]

if not filtered:
    st.warning("No hay publicaciones que coincidan con el filtro.")
    st.stop()

# Grid de tarjetas (3 por fila)
for row_start in range(0, len(filtered), 3):
    cols = st.columns(3)
    for col_idx, col in enumerate(cols):
        post_idx = row_start + col_idx
        if post_idx >= len(filtered):
            break

        post = filtered[post_idx]

        with col:
            with st.container(border=True):
                # Screenshot
                img_path = post.screenshot_path
                if img_path and Path(img_path).exists():
                    st.image(img_path, use_container_width=True)
                else:
                    st.markdown("*Sin imagen disponible*")

                # Badges
                platform_icons = {
                    "instagram": "🟣 Instagram", "facebook": "🔵 Facebook",
                    "twitter": "🔵 X/Twitter", "tiktok": "⚫ TikTok",
                    "unknown": "⚪ Otro",
                }
                status_html = {
                    ComplianceStatus.CUMPLE: '<span style="background:#22c55e;color:white;padding:3px 10px;border-radius:10px;font-size:0.8em;">Cumple</span>',
                    ComplianceStatus.NO_CUMPLE: '<span style="background:#ef4444;color:white;padding:3px 10px;border-radius:10px;font-size:0.8em;">No Cumple</span>',
                    ComplianceStatus.ERROR: '<span style="background:#6b7280;color:white;padding:3px 10px;border-radius:10px;font-size:0.8em;">Error</span>',
                    ComplianceStatus.PENDIENTE: '<span style="background:#f59e0b;color:white;padding:3px 10px;border-radius:10px;font-size:0.8em;">Pendiente</span>',
                }

                plat_label = platform_icons.get(post.platform.value, "⚪ Otro")
                stat_html = status_html.get(post.status, "")
                st.markdown(f"{plat_label} &nbsp; {stat_html}", unsafe_allow_html=True)

                # Texto extraido
                if post.extracted_text:
                    with st.expander("Texto extraido"):
                        st.write(post.extracted_text)

                # Analisis detallado
                if post.analysis:
                    a = post.analysis

                    # Hashtags
                    if a.hashtags_present or a.hashtags_missing:
                        st.markdown("**Hashtags:**")
                        for h in a.hashtags_present:
                            st.markdown(f"&nbsp;&nbsp; ✅ `{h}`")
                        for h in a.hashtags_missing:
                            st.markdown(f"&nbsp;&nbsp; ❌ `{h}` (faltante)")

                    # Logo/Marca
                    logo_icon = "✅" if a.brand_identity else "❌"
                    st.markdown(f"**Logo oficial:** {logo_icon}")

                    # Tono
                    tone_pct = f"{a.emotional_score * 100:.0f}%"
                    st.markdown(f"**Tono:** {a.tone_label.capitalize()} ({tone_pct} emotivo)")

                    # Errores de diseno
                    if a.design_errors:
                        with st.expander(f"Errores de diseno ({len(a.design_errors)})"):
                            for err in a.design_errors:
                                st.markdown(f"- {err}")

                    # Errores comunes
                    if a.common_errors:
                        with st.expander(f"Errores comunes ({len(a.common_errors)})"):
                            for err in a.common_errors:
                                st.markdown(f"- {err}")

                    # Correcciones sugeridas
                    if a.suggested_corrections:
                        with st.expander("Correcciones sugeridas"):
                            for corr in a.suggested_corrections:
                                st.markdown(f"- {corr}")

                elif post.error_message:
                    st.error(post.error_message)

                # Link al post original
                st.markdown(f"[Ver publicacion original]({post.url})")
