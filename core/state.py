import streamlit as st


def init_session_state():
    defaults = {
        "authenticated": False,
        "current_batch_id": None,
        "processing": False,
        "progress": 0.0,
        "progress_message": "",
        "posts": [],
        "config": None,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value
