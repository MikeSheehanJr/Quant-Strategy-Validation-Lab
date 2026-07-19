"""Public entry point for the Quant strategy validation lab."""

from __future__ import annotations

import streamlit as st

from src.data import load_snapshot
from src.ui import inject_visual_system, render_app_footer


st.set_page_config(
    page_title="Quant strategy validation lab",
    page_icon=":material/query_stats:",
    layout="wide",
    initial_sidebar_state="collapsed",
)

inject_visual_system()


page = st.navigation(
    [
        st.Page(
            "app_pages/research_brief.py",
            title="Research brief",
            icon=":material/description:",
            default=True,
        ),
        st.Page(
            "app_pages/robustness.py",
            title="Robustness",
            icon=":material/query_stats:",
        ),
        st.Page(
            "app_pages/implementation.py",
            title="Implementation",
            icon=":material/code:",
        ),
        st.Page(
            "app_pages/forward_validation.py",
            title="Forward validation",
            icon=":material/schedule:",
        ),
    ],
    position="top",
)
page.run()

meta = load_snapshot()["meta"]
render_app_footer(meta)
