import streamlit as st
from config.credentials import verify_credentials


def render_login():
    st.markdown(
        "<h1 style='text-align:center;'>Monitor de Cumplimiento Social</h1>",
        unsafe_allow_html=True,
    )
    st.markdown(
        "<p style='text-align:center;color:#888;'>Inicia sesion para acceder al sistema</p>",
        unsafe_allow_html=True,
    )

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        with st.form("login_form"):
            username = st.text_input("Usuario")
            password = st.text_input("Contrasena", type="password")
            submitted = st.form_submit_button("Iniciar Sesion", use_container_width=True)

            if submitted:
                if verify_credentials(username, password):
                    st.session_state.authenticated = True
                    st.rerun()
                else:
                    st.error("Credenciales incorrectas. Intenta de nuevo.")
