"""Shared Streamlit presentation helpers and the public visual system."""

from __future__ import annotations

import base64
from functools import lru_cache
from pathlib import Path
from typing import Any

import streamlit as st


PROJECT_ROOT = Path(__file__).resolve().parents[1]
BACKGROUND_ASSET = PROJECT_ROOT / "assets" / "research-glass-grain.png"


@lru_cache(maxsize=1)
def background_data_uri() -> str:
    """Return the reviewed local background as an inline, network-free asset."""

    encoded = base64.b64encode(BACKGROUND_ASSET.read_bytes()).decode("ascii")
    return f"data:image/png;base64,{encoded}"


@lru_cache(maxsize=1)
def visual_css() -> str:
    """Build the static liquid-glass CSS used by every routed app page."""

    css = """
<style>
:root {
    --qsvl-navy: #003049;
    --qsvl-navy-deep: #001722;
    --qsvl-red: #D62828;
    --qsvl-gold: #FCBF49;
    --qsvl-cream: #EAE2B7;
    --qsvl-glass: rgba(0, 40, 58, 0.58);
    --qsvl-glass-strong: rgba(0, 32, 47, 0.76);
    --qsvl-border: rgba(234, 226, 183, 0.18);
    --qsvl-border-hover: rgba(252, 191, 73, 0.34);
    --qsvl-shadow: 0 18px 50px rgba(0, 8, 14, 0.28);
}

html,
body,
[data-testid="stApp"] {
    background: var(--qsvl-navy-deep);
}

[data-testid="stAppViewContainer"] {
    background-color: var(--qsvl-navy-deep);
    background-image:
        linear-gradient(180deg, rgba(0, 12, 19, 0.22), rgba(0, 16, 25, 0.70)),
        linear-gradient(90deg, rgba(0, 48, 73, 0.28), rgba(0, 16, 25, 0.16)),
        url("__BACKGROUND_DATA_URI__");
    background-position: center, center, center top;
    background-repeat: no-repeat;
    background-size: cover;
    background-attachment: fixed;
}

[data-testid="stMain"] {
    background: transparent;
}

header[data-testid="stHeader"] {
    min-height: 4.75rem;
    height: 4.75rem;
    background: rgba(0, 20, 31, 0.72);
    border-bottom: 1px solid rgba(234, 226, 183, 0.13);
    box-shadow: 0 12px 34px rgba(0, 8, 14, 0.24);
    -webkit-backdrop-filter: blur(24px) saturate(135%);
    backdrop-filter: blur(24px) saturate(135%);
}

[data-testid="stToolbar"] {
    min-height: 4.75rem;
    padding-inline: clamp(0.8rem, 2.4vw, 2.25rem);
}

[data-testid="stTopNavLinkContainer"] {
    padding-block: 0.72rem;
}

[data-testid="stTopNavLink"] {
    min-height: 2.85rem;
    padding: 0.62rem 0.95rem;
    gap: 0.48rem;
    border: 1px solid transparent;
    border-radius: 999px;
    color: rgba(234, 226, 183, 0.78);
    transition:
        transform 180ms ease,
        color 180ms ease,
        background-color 180ms ease,
        border-color 180ms ease,
        box-shadow 180ms ease;
}

[data-testid="stTopNavLink"] p {
    font-size: 0.96rem;
    font-weight: 600;
    letter-spacing: 0.005em;
}

[data-testid="stTopNavLink"] [data-testid="stIconMaterial"] {
    font-size: 1.12rem;
}

[data-testid="stTopNavLink"]:hover {
    color: var(--qsvl-cream);
    background: rgba(234, 226, 183, 0.07);
    border-color: rgba(234, 226, 183, 0.15);
    transform: translateY(-1px);
}

[data-testid="stTopNavLink"][aria-current="page"] {
    color: var(--qsvl-cream);
    background: linear-gradient(
        135deg,
        rgba(252, 191, 73, 0.18),
        rgba(234, 226, 183, 0.07)
    );
    border-color: rgba(252, 191, 73, 0.30);
    box-shadow:
        inset 0 1px 0 rgba(255, 255, 255, 0.10),
        0 8px 22px rgba(0, 8, 14, 0.20);
}

[data-testid="stMainBlockContainer"] {
    max-width: 88rem;
    padding-top: 6.4rem;
    padding-right: clamp(1.1rem, 3vw, 3rem);
    padding-bottom: 4.5rem;
    padding-left: clamp(1.1rem, 3vw, 3rem);
}

.st-key-page_header {
    position: relative;
    overflow: hidden;
    margin-bottom: 0.3rem;
    border-radius: 1.5rem;
}

.st-key-page_header::before {
    position: absolute;
    z-index: 1;
    top: 0;
    right: 1.5rem;
    left: 1.5rem;
    height: 1px;
    content: "";
    background: linear-gradient(
        90deg,
        transparent,
        rgba(252, 191, 73, 0.62),
        rgba(234, 226, 183, 0.28),
        transparent
    );
    pointer-events: none;
}

.st-key-page_header h1 {
    max-width: 16ch;
    letter-spacing: -0.035em;
    line-height: 1.04;
    text-wrap: balance;
}

.st-key-page_header [data-testid="stCaptionContainer"] p {
    letter-spacing: 0.14em;
    color: rgba(234, 226, 183, 0.68);
}

[data-testid="stLayoutWrapper"] > [data-testid="stVerticalBlock"],
[data-testid="stMetric"] {
    border: 1px solid var(--qsvl-border) !important;
    background:
        linear-gradient(145deg, rgba(255, 255, 255, 0.045), transparent 42%),
        var(--qsvl-glass) !important;
    box-shadow:
        inset 0 1px 0 rgba(255, 255, 255, 0.055),
        var(--qsvl-shadow);
    -webkit-backdrop-filter: blur(18px) saturate(128%);
    backdrop-filter: blur(18px) saturate(128%);
    transition:
        transform 190ms cubic-bezier(0.2, 0.72, 0.2, 1),
        border-color 190ms ease,
        box-shadow 190ms ease,
        background-color 190ms ease;
}

[data-testid="stLayoutWrapper"] > [data-testid="stVerticalBlock"] {
    padding: 1.2rem !important;
    border-radius: 1.25rem !important;
}

[data-testid="stLayoutWrapper"] > [data-testid="stVerticalBlock"]:hover {
    z-index: 2;
    border-color: var(--qsvl-border-hover) !important;
    box-shadow:
        inset 0 1px 0 rgba(255, 255, 255, 0.075),
        0 22px 58px rgba(0, 8, 14, 0.34);
    transform: translateY(-2px) scale(1.005);
}

[data-testid="stMetric"] {
    min-height: 7.1rem;
    justify-content: center;
    padding: 1.05rem 1.15rem;
    border-radius: 1.15rem !important;
}

[data-testid="stMetric"]:hover {
    z-index: 3;
    border-color: var(--qsvl-border-hover) !important;
    box-shadow:
        inset 0 1px 0 rgba(255, 255, 255, 0.08),
        0 18px 44px rgba(0, 8, 14, 0.34);
    transform: translateY(-2px) scale(1.012);
}

[data-testid="stMetricLabel"] p {
    color: rgba(234, 226, 183, 0.72);
    font-size: 0.82rem;
    font-weight: 600;
    letter-spacing: 0.025em;
}

[data-testid="stMetricValue"] {
    color: var(--qsvl-cream);
    font-variant-numeric: tabular-nums;
    letter-spacing: -0.035em;
}

[data-testid="stVegaLiteChart"] {
    border-radius: 0.9rem;
    animation: qsvl-chart-arrive 560ms cubic-bezier(0.2, 0.72, 0.2, 1) both;
    transition: filter 200ms ease, transform 200ms ease;
}

[data-testid="stVegaLiteChart"]:hover {
    filter: drop-shadow(0 10px 22px rgba(252, 191, 73, 0.08));
    transform: translateY(-1px);
}

[data-testid="stDataFrame"],
[data-testid="stTable"],
[data-testid="stAlert"],
[data-testid="stExpander"],
[data-testid="stSegmentedControl"],
[data-testid="stSelectbox"] > div {
    border-radius: 1rem;
    -webkit-backdrop-filter: blur(14px) saturate(120%);
    backdrop-filter: blur(14px) saturate(120%);
}

[data-testid="stAlert"] {
    border-color: rgba(234, 226, 183, 0.16);
    background: rgba(0, 38, 55, 0.62);
}

[data-testid^="stBaseButton"],
[data-testid="stDownloadButton"] button {
    transition:
        transform 170ms ease,
        border-color 170ms ease,
        box-shadow 170ms ease,
        background-color 170ms ease;
}

[data-testid^="stBaseButton"]:hover,
[data-testid="stDownloadButton"] button:hover {
    border-color: rgba(252, 191, 73, 0.36);
    box-shadow: 0 10px 24px rgba(0, 8, 14, 0.25);
    transform: translateY(-1px) scale(1.01);
}

[data-testid="stMainBlockContainer"] > [data-testid="stVerticalBlock"] {
    animation: qsvl-page-arrive 390ms ease-out both;
}

@keyframes qsvl-page-arrive {
    from {
        opacity: 0;
        transform: translateY(7px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

@keyframes qsvl-chart-arrive {
    from {
        opacity: 0;
        transform: translateY(5px) scale(0.995);
    }
    to {
        opacity: 1;
        transform: translateY(0) scale(1);
    }
}

@media (max-width: 800px) {
    header[data-testid="stHeader"],
    [data-testid="stToolbar"] {
        min-height: 4.15rem;
        height: 4.15rem;
    }

    [data-testid="stTopNavLinkContainer"] {
        padding-block: 0.52rem;
    }

    [data-testid="stTopNavLink"] {
        min-height: 2.65rem;
        padding: 0.52rem 0.72rem;
    }

    [data-testid="stTopNavLink"] p {
        font-size: 0.84rem;
    }

    [data-testid="stExpandSidebarButton"] {
        width: auto;
        min-width: 4.75rem;
        gap: 0.3rem;
        color: var(--qsvl-cream);
        border: 1px solid rgba(234, 226, 183, 0.14);
        border-radius: 999px;
        background: rgba(0, 40, 58, 0.58);
    }

    [data-testid="stExpandSidebarButton"]::after {
        content: "Pages";
        font-size: 0.8rem;
        font-weight: 600;
        letter-spacing: 0.02em;
    }

    [data-testid="stMainBlockContainer"] {
        padding-top: 5.45rem;
        padding-right: 1rem;
        padding-left: 1rem;
    }

    [data-testid="stLayoutWrapper"] > [data-testid="stVerticalBlock"] {
        padding: 1rem !important;
        border-radius: 1.05rem !important;
    }

    [data-testid="stMetric"] {
        min-height: 6.4rem;
    }
}

@media (prefers-reduced-motion: reduce) {
    *,
    *::before,
    *::after {
        scroll-behavior: auto !important;
        animation-duration: 0.01ms !important;
        animation-iteration-count: 1 !important;
        transition-duration: 0.01ms !important;
    }

    [data-testid="stLayoutWrapper"] > [data-testid="stVerticalBlock"]:hover,
    [data-testid="stMetric"]:hover,
    [data-testid="stVegaLiteChart"]:hover,
    [data-testid^="stBaseButton"]:hover,
    [data-testid="stDownloadButton"] button:hover {
        transform: none;
    }
}
</style>
"""
    return css.replace("__BACKGROUND_DATA_URI__", background_data_uri())


def inject_visual_system() -> None:
    """Inject static CSS only; no script or untrusted input reaches the page."""

    st.html(visual_css())


def render_page_header(
    eyebrow: str,
    title: str,
    description: str,
    *,
    work_in_progress: bool = True,
) -> None:
    """Render a consistent, prominent page heading."""

    with st.container(key="page_header", gap="xsmall"):
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
                    color="yellow",
                )
        st.markdown(description)


def render_research_boundary(meta: dict[str, Any]) -> None:
    """Show the public evidence boundary without occupying a sidebar."""

    st.caption(
        f"{meta['instrument']} · {meta['research_window']} · snapshot "
        f"{meta['snapshot_date']} · reviewed aggregates only"
    )
