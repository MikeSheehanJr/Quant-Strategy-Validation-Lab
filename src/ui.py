"""Small, native Streamlit presentation helpers shared across app pages."""

from __future__ import annotations

from typing import Any

import streamlit as st


def render_page_header(
    eyebrow: str,
    title: str,
    description: str,
    *,
    work_in_progress: bool = True,
) -> None:
    """Render a consistent, restrained page heading."""

    st.caption(eyebrow.upper())
    with st.container(
        horizontal=True,
        horizontal_alignment="distribute",
        vertical_alignment="center",
    ):
        st.title(title)
        if work_in_progress:
            st.badge(
                "Work in progress",
                icon=":material/construction:",
                color="blue",
            )
    st.markdown(description)


def render_research_boundary(meta: dict[str, Any]) -> None:
    """Show the public evidence boundary without occupying a sidebar."""

    st.caption(
        f"{meta['instrument']} · {meta['research_window']} · snapshot "
        f"{meta['snapshot_date']} · reviewed aggregates only"
    )
