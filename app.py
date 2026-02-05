import streamlit as st
from pathlib import Path
from core.state import init_session_state
from auth.login import render_login

st.set_page_config(
    page_title="Monitor de Cumplimiento Social",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Cargar CSS personalizado
css_path = Path(__file__).parent / "assets" / "styles.css"
if css_path.exists():
    st.markdown(f"<style>{css_path.read_text()}</style>", unsafe_allow_html=True)

# Inicializar session state
init_session_state()

# Gate de autenticacion
if not st.session_state.authenticated:
    render_login()
    st.stop()

# Navegacion multi-pagina
pages = {
    "Principal": [
        st.Page("pages/1_carga_urls.py", title="Carga de URLs", icon="📥"),
        st.Page("pages/2_dashboard.py", title="Dashboard", icon="📊"),
        st.Page("pages/3_galeria.py", title="Galeria", icon="🖼️"),
    ],
    "Administracion": [
        st.Page("pages/4_configuracion.py", title="Configuracion", icon="⚙️"),
        st.Page("pages/5_reportes.py", title="Reportes", icon="📄"),
    ],
}

nav = st.navigation(pages)

# Sidebar: info de usuario y logout
with st.sidebar:
    st.markdown("---")
    st.caption("Sesion activa")
    if st.button("Cerrar Sesion", use_container_width=True):
        st.session_state.authenticated = False
        st.rerun()

nav.run()
