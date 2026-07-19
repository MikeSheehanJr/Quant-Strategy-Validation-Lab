"""Shared Streamlit presentation helpers and the public visual system."""

from __future__ import annotations

import base64
from functools import lru_cache
from pathlib import Path
from typing import Any

import streamlit as st


PROJECT_ROOT = Path(__file__).resolve().parents[1]
BACKGROUND_ASSET = PROJECT_ROOT / "assets" / "research-glass-grain-v2.png"


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
    --qsvl-orange: #F77F00;
    --qsvl-gold: #FCBF49;
    --qsvl-cream: #EAE2B7;
    --qsvl-text-bright: #F4EED6;
    --qsvl-text-muted: #B8C6C4;
    --qsvl-space: clamp(0.78rem, 1.25vw, 1rem);
    --qsvl-radius: 0.4rem;
    --qsvl-glass: rgba(0, 31, 46, 0.44);
    --qsvl-glass-hover: rgba(0, 31, 46, 0.62);
    --qsvl-glass-strong: rgba(0, 32, 47, 0.78);
    --qsvl-border: rgba(234, 226, 183, 0.12);
    --qsvl-border-hover: rgba(234, 226, 183, 0.24);
    --qsvl-shadow: 0 8px 24px rgba(0, 8, 14, 0.18);
}

html,
body,
[data-testid="stApp"] {
    background: var(--qsvl-navy-deep);
}

[data-testid="stAppViewContainer"] {
    background-color: var(--qsvl-navy-deep);
    background-image:
        linear-gradient(180deg, rgba(0, 12, 19, 0.30), rgba(0, 16, 25, 0.66)),
        linear-gradient(90deg, rgba(0, 48, 73, 0.12), rgba(0, 16, 25, 0.18)),
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
    border-radius: var(--qsvl-radius);
    color: rgba(234, 226, 183, 0.78);
    transition:
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
}

[data-testid="stTopNavLink"][aria-current="page"] {
    color: var(--qsvl-cream);
    background: rgba(234, 226, 183, 0.08);
    border-color: rgba(234, 226, 183, 0.26);
    box-shadow:
        inset 0 1px 0 rgba(255, 255, 255, 0.10),
        0 4px 14px rgba(0, 8, 14, 0.18);
}

[data-testid="stMainBlockContainer"] {
    max-width: 96rem;
    padding-top: 6.4rem;
    padding-right: clamp(1rem, 2.6vw, 2.75rem);
    padding-bottom: 4.5rem;
    padding-left: clamp(1rem, 2.6vw, 2.75rem);
}

[data-testid="stMainBlockContainer"] > [data-testid="stVerticalBlock"] {
    gap: var(--qsvl-space);
}

[data-testid="stHorizontalBlock"] {
    gap: var(--qsvl-space);
}

.st-key-page_header {
    position: relative;
    overflow: hidden;
    margin-bottom: 0.3rem;
    border-radius: var(--qsvl-radius);
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
        rgba(247, 127, 0, 0.42),
        rgba(234, 226, 183, 0.28),
        transparent
    );
    pointer-events: none;
}

.st-key-page_header h1 {
    max-width: 16ch;
    color: var(--qsvl-text-bright);
    letter-spacing: -0.035em;
    line-height: 1.04;
    text-wrap: balance;
}

.st-key-page_header [data-testid="stCaptionContainer"] p {
    letter-spacing: 0.14em;
    color: rgba(234, 226, 183, 0.68);
}

[data-testid="stCaptionContainer"] p {
    color: var(--qsvl-text-muted);
}

h2,
h3 {
    color: var(--qsvl-text-bright);
    letter-spacing: -0.018em;
}

.qsvl-status-symbol {
    display: grid;
    width: 2.35rem;
    height: 2.35rem;
    place-items: center;
    color: var(--qsvl-gold);
    border: 1px solid rgba(252, 191, 73, 0.28);
    border-radius: var(--qsvl-radius);
    background: rgba(252, 191, 73, 0.08);
    box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.08);
    font-size: 1rem;
    line-height: 1;
}

.st-key-research_context [data-testid="stMarkdownContainer"] p,
.st-key-app_footer [data-testid="stCaptionContainer"] p {
    margin: 0;
}

.st-key-app_footer {
    margin-top: 0.15rem;
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
    -webkit-backdrop-filter: blur(10px) saturate(108%);
    backdrop-filter: blur(10px) saturate(108%);
    transition:
        border-color 160ms ease,
        box-shadow 160ms ease,
        background 160ms ease,
        -webkit-backdrop-filter 160ms ease,
        backdrop-filter 160ms ease;
}

[data-testid="stLayoutWrapper"] > [data-testid="stVerticalBlock"] {
    padding: clamp(0.95rem, 1.4vw, 1.2rem) !important;
    border-radius: var(--qsvl-radius) !important;
}

[data-testid="stLayoutWrapper"] > [data-testid="stVerticalBlock"]:hover {
    z-index: 2;
    border-color: var(--qsvl-border-hover) !important;
    background:
        linear-gradient(145deg, rgba(255, 255, 255, 0.075), transparent 46%),
        var(--qsvl-glass-hover) !important;
    box-shadow:
        inset 0 1px 0 rgba(255, 255, 255, 0.075),
        0 10px 28px rgba(0, 8, 14, 0.24);
    -webkit-backdrop-filter: blur(16px) saturate(118%);
    backdrop-filter: blur(16px) saturate(118%);
}

[data-testid="stMetric"] {
    min-height: 7.1rem;
    justify-content: center;
    padding: 1.05rem 1.15rem;
    border-radius: var(--qsvl-radius) !important;
}

[data-testid="stMetric"]:hover {
    z-index: 3;
    border-color: var(--qsvl-border-hover) !important;
    background:
        linear-gradient(145deg, rgba(255, 255, 255, 0.08), transparent 46%),
        var(--qsvl-glass-hover) !important;
    box-shadow:
        inset 0 1px 0 rgba(255, 255, 255, 0.08),
        0 10px 28px rgba(0, 8, 14, 0.24);
    -webkit-backdrop-filter: blur(16px) saturate(118%);
    backdrop-filter: blur(16px) saturate(118%);
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
    border-radius: var(--qsvl-radius);
    animation: qsvl-chart-arrive 240ms ease-out both;
    transition: filter 160ms ease;
}

[data-testid="stVegaLiteChart"]:hover {
    filter: drop-shadow(0 10px 22px rgba(252, 191, 73, 0.08));
}

[data-testid="stDataFrame"],
[data-testid="stTable"],
[data-testid="stAlert"],
[data-testid="stExpander"],
[data-testid="stSegmentedControl"],
[data-testid="stSelectbox"] > div {
    border: 1px solid rgba(234, 226, 183, 0.10);
    border-radius: var(--qsvl-radius);
    background: rgba(0, 36, 52, 0.26);
    -webkit-backdrop-filter: blur(6px) saturate(110%);
    backdrop-filter: blur(6px) saturate(110%);
    transition:
        border-color 220ms ease,
        background 240ms ease,
        -webkit-backdrop-filter 240ms ease,
        backdrop-filter 240ms ease;
}

[data-testid="stDataFrame"]:hover,
[data-testid="stTable"]:hover,
[data-testid="stAlert"]:hover,
[data-testid="stExpander"]:hover,
[data-testid="stSegmentedControl"]:hover,
[data-testid="stSelectbox"] > div:hover {
    border-color: rgba(252, 191, 73, 0.24);
    background: rgba(0, 31, 46, 0.70);
    -webkit-backdrop-filter: blur(18px) saturate(132%);
    backdrop-filter: blur(18px) saturate(132%);
}

[data-testid="stAlert"] {
    border-color: rgba(234, 226, 183, 0.16);
    background: rgba(0, 38, 55, 0.62);
}

[data-testid="stDataFrame"],
[data-testid="stTable"],
[data-testid="stAlert"] {
    overflow: hidden;
}

[data-testid^="stBaseButton"],
[data-testid="stDownloadButton"] button {
    border-radius: var(--qsvl-radius) !important;
    transition:
        border-color 150ms ease,
        box-shadow 170ms ease,
        background-color 170ms ease;
}

[data-testid^="stBaseButton"]:hover,
[data-testid="stDownloadButton"] button:hover {
    border-color: rgba(252, 191, 73, 0.36);
    box-shadow: 0 6px 18px rgba(0, 8, 14, 0.22);
}

[data-testid="stMainBlockContainer"] > [data-testid="stVerticalBlock"] {
    animation: qsvl-page-arrive 180ms ease-out both;
}

@keyframes qsvl-page-arrive {
    from {
        opacity: 0;
    }
    to {
        opacity: 1;
    }
}

@keyframes qsvl-chart-arrive {
    from {
        opacity: 0;
    }
    to {
        opacity: 1;
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
        border-radius: var(--qsvl-radius);
        background: rgba(0, 36, 52, 0.44);
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

    [data-testid="stMainBlockContainer"] > [data-testid="stVerticalBlock"],
    [data-testid="stHorizontalBlock"] {
        gap: 0.75rem;
    }

    [data-testid="stLayoutWrapper"] > [data-testid="stVerticalBlock"] {
        padding: 1rem !important;
        border-radius: var(--qsvl-radius) !important;
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
    status_style: str = "symbol",
) -> None:
    """Render a prominent page heading with one full status label site-wide."""

    if status_style not in {"full", "symbol"}:
        raise ValueError("status_style must be 'full' or 'symbol'")

    with st.container(key="page_header", gap="xsmall"):
        st.caption(eyebrow.upper())
        with st.container(
            horizontal=True,
            horizontal_alignment="distribute",
            vertical_alignment="center",
        ):
            st.title(title)
            if status_style == "full":
                st.badge(
                    "Work in progress",
                    icon=":material/handyman:",
                    color="yellow",
                )
            else:
                st.html(
                    '<span class="qsvl-status-symbol" role="img" '
                    'aria-label="Work in progress" title="Work in progress">🛠</span>'
                )
        st.markdown(description)


def render_research_boundary(meta: dict[str, Any]) -> None:
    """Show the full research context once, on the canonical brief."""

    with st.container(border=True, key="research_context", gap="xxsmall"):
        st.markdown(
            f":material/candlestick_chart: **{meta['instrument']}** · "
            f"{meta['research_window']} · snapshot {meta['snapshot_date']} · "
            "reviewed aggregates only"
        )


def render_section_header(title: str, description: str, *, key: str) -> None:
    """Render section copy inside a compact glass tile instead of floating text."""

    with st.container(border=True, key=f"section_{key}", gap="xxsmall"):
        st.subheader(title)
        st.caption(description)


def render_app_footer(meta: dict[str, Any]) -> None:
    """Render a concise global artifact footer in its own glass tile."""

    with st.container(border=True, key="app_footer", gap="xxsmall"):
        st.caption(
            f"Public aggregate artifact · schema {meta['schema_version']} · "
            "raw market data excluded"
        )
