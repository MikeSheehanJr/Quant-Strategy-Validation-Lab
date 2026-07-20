"""Entry point for the Quant strategy validation lab."""

from __future__ import annotations

import importlib

import streamlit as st

from src import charts as charts_module
from src import simulations as simulations_module
from src import ui as ui_module
from src.data import load_snapshot


# Streamlit can keep imported helpers alive across a hot deployment. Reload the small modules
# changed by this app so page scripts, simulations, charts, and shared styling stay in sync.
for current_module in (simulations_module, charts_module, ui_module):
    importlib.reload(current_module)


st.set_page_config(
    page_title="Quant strategy validation lab",
    page_icon=":material/query_stats:",
    layout="wide",
    initial_sidebar_state="collapsed",
)

ui_module.inject_visual_system()


pages = [
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
]

page = st.navigation(pages, position="top")
ui_module.render_mobile_navigation(pages)
page.run()

meta = load_snapshot()["meta"]
ui_module.render_app_footer(meta)
