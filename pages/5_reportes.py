import streamlit as st
from core.database import init_db, get_all_posts, load_config, delete_all_posts
from core.models import ComplianceStatus
from reports.charts import (
    generate_compliance_pie,
    generate_error_bar_chart,
    generate_hashtag_usage_chart,
    generate_platform_breakdown,
)
from reports.pdf_export import generate_pdf_report
from reports.excel_export import generate_excel_report

init_db()

st.header("Reportes de Cumplimiento")

posts = get_all_posts()
config = load_config()

if not posts:
    st.info("No hay publicaciones analizadas para generar reportes.")
    st.stop()

# --- Resumen General ---
st.subheader("Resumen General")

total = len(posts)
cumple = sum(1 for p in posts if p.status == ComplianceStatus.CUMPLE)
no_cumple = sum(1 for p in posts if p.status == ComplianceStatus.NO_CUMPLE)

col1, col2 = st.columns(2)

with col1:
    fig_pie = generate_compliance_pie(posts)
    st.pyplot(fig_pie)

with col2:
    fig_platform = generate_platform_breakdown(posts)
    st.pyplot(fig_platform)

st.markdown("---")

# Errores mas comunes
st.subheader("Errores Mas Comunes")
fig_errors = generate_error_bar_chart(posts)
st.pyplot(fig_errors)

st.markdown("---")

# Uso de hashtags
st.subheader("Uso de Hashtags Obligatorios")
fig_hashtags = generate_hashtag_usage_chart(posts, config.required_hashtags)
st.pyplot(fig_hashtags)

st.markdown("---")

# --- Exportar ---
st.subheader("Exportar Reportes")

col_pdf, col_excel, col_clear = st.columns(3)

with col_pdf:
    pdf_bytes = generate_pdf_report(posts, config)
    st.download_button(
        "Descargar Reporte PDF",
        data=pdf_bytes,
        file_name="reporte_cumplimiento.pdf",
        mime="application/pdf",
        use_container_width=True,
    )

with col_excel:
    excel_bytes = generate_excel_report(posts)
    st.download_button(
        "Descargar Reporte Excel",
        data=excel_bytes,
        file_name="reporte_cumplimiento.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True,
    )

with col_clear:
    if st.button("Limpiar Todos los Datos", use_container_width=True, type="secondary"):
        delete_all_posts()
        st.session_state.posts = []
        st.success("Todos los datos han sido eliminados.")
        st.rerun()
