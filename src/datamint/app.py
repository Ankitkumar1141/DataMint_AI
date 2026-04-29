from __future__ import annotations

import streamlit as st

from datamint.config import get_settings
from datamint.db.schema import setup_database
from datamint.ui.auth_page import render_auth_page
from datamint.ui.generator_page import render_generator_page

settings = get_settings()

st.set_page_config(page_title=settings.app_name, layout="centered")

setup_database()

if "user" not in st.session_state:
    st.session_state.user = None

if st.session_state.user:
    render_generator_page()
else:
    render_auth_page()
