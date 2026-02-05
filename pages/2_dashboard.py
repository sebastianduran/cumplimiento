import streamlit as st
from pathlib import Path
from core.database import init_db, get_all_posts
from core.models import ComplianceStatus

init_db()

st.header("Dashboard de Cumplimiento")

# Cargar posts
posts = get_all_posts()

if not posts:
    st.info("No hay publicaciones analizadas. Ve a 'Carga de URLs' para comenzar.")
    st.stop()

# --- Metricas resumen ---
total = len(posts)
cumple = sum(1 for p in posts if p.status == ComplianceStatus.CUMPLE)
no_cumple = sum(1 for p in posts if p.status == ComplianceStatus.NO_CUMPLE)
errores = sum(1 for p in posts if p.status == ComplianceStatus.ERROR)

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Total Posts", total)
with col2:
    pct_cumple = f"{(cumple / total * 100):.0f}%" if total > 0 else "0%"
    st.metric("Cumple", f"{cumple} ({pct_cumple})")
with col3:
    pct_no = f"{(no_cumple / total * 100):.0f}%" if total > 0 else "0%"
    st.metric("No Cumple", f"{no_cumple} ({pct_no})")
with col4:
    st.metric("Errores", errores)

st.markdown("---")

# --- Filtros ---
col_f1, col_f2, _ = st.columns([2, 2, 6])
with col_f1:
    filter_platform = st.selectbox(
        "Filtrar por plataforma",
        ["Todas", "instagram", "facebook", "twitter", "tiktok"],
    )
with col_f2:
    filter_status = st.selectbox(
        "Filtrar por estado",
        ["Todos", "cumple", "no-cumple", "error", "pendiente"],
    )

# Aplicar filtros
filtered = posts
if filter_platform != "Todas":
    filtered = [p for p in filtered if p.platform.value == filter_platform]
if filter_status != "Todos":
    filtered = [p for p in filtered if p.status.value == filter_status]

st.caption(f"Mostrando {len(filtered)} de {total} publicaciones")

# --- Tabla de resultados ---
if not filtered:
    st.warning("No hay publicaciones que coincidan con los filtros seleccionados.")
    st.stop()

for post in filtered:
    col_img, col_info, col_status = st.columns([2, 6, 2])

    with col_img:
        thumb = post.thumbnail_path or post.screenshot_path
        if thumb and Path(thumb).exists():
            st.image(thumb, use_container_width=True)
        else:
            st.markdown("*Sin imagen*")

    with col_info:
        platform_icons = {
            "instagram": "🟣", "facebook": "🔵",
            "twitter": "🔵", "tiktok": "⚫", "unknown": "⚪",
        }
        icon = platform_icons.get(post.platform.value, "⚪")
        st.markdown(f"{icon} **{post.platform.value.capitalize()}**")
        if len(post.url) > 60:
            st.markdown(f"[{post.url[:60]}...]({post.url})")
        else:
            st.markdown(f"[{post.url}]({post.url})")

        if post.extracted_text:
            text_preview = post.extracted_text[:150]
            if len(post.extracted_text) > 150:
                text_preview += "..."
            st.caption(text_preview)

        if post.analysis and post.analysis.hashtags_missing:
            missing = "`, `".join(post.analysis.hashtags_missing)
            st.markdown(f"Hashtags faltantes: `{missing}`")

        if post.error_message:
            st.caption(f"Error: {post.error_message}")

    with col_status:
        status_styles = {
            ComplianceStatus.CUMPLE: ("Cumple", "#22c55e"),
            ComplianceStatus.NO_CUMPLE: ("No Cumple", "#ef4444"),
            ComplianceStatus.ERROR: ("Error", "#6b7280"),
            ComplianceStatus.PENDIENTE: ("Pendiente", "#f59e0b"),
        }
        label, color = status_styles.get(post.status, ("?", "#999"))
        st.markdown(
            f'<span style="background:{color};color:white;padding:6px 16px;border-radius:12px;font-weight:600;">{label}</span>',
            unsafe_allow_html=True,
        )

    st.markdown("---")
