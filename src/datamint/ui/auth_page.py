from __future__ import annotations

import streamlit as st

from datamint.services.auth import authenticate_user, register_user


def render_auth_page() -> None:
    st.title("DataMint AI")
    st.caption("Generate realistic synthetic datasets for ML experiments.")

    login_tab, register_tab = st.tabs(["Login", "Register"])

    with login_tab:
        username = st.text_input("Username", key="login_username")
        password = st.text_input("Password", type="password", key="login_password")
        if st.button("Login", type="primary"):
            user = authenticate_user(username, password)
            if user:
                st.session_state.user = user
                st.rerun()
            st.error("Invalid username or password.")

    with register_tab:
        username = st.text_input("Username", key="register_username")
        password = st.text_input("Password", type="password", key="register_password")
        if st.button("Create account"):
            ok, message = register_user(username, password)
            if ok:
                st.success(message)
            else:
                st.error(message)
