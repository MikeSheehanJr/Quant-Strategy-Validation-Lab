"""Shared Streamlit presentation helpers and the research visual system."""

from __future__ import annotations

from functools import lru_cache
from typing import Any

import streamlit as st


@lru_cache(maxsize=1)
def visual_css() -> str:
    """Build the flat, four-color visual system used by every routed app page."""

    return """
<style>
:root {
    --qsvl-charcoal: #2D3436;
    --qsvl-navy: #0A3D62;
    --qsvl-gold: #D4AF37;
    --qsvl-ivory: #F9F9F9;
    --qsvl-space: clamp(0.78rem, 1.25vw, 1rem);
    --qsvl-glass: rgba(10, 61, 98, 0.26);
    --qsvl-glass-strong: rgba(10, 61, 98, 0.44);
    --qsvl-border: rgba(249, 249, 249, 0.15);
    --qsvl-border-focus: rgba(212, 175, 55, 0.58);
    --qsvl-muted: rgba(249, 249, 249, 0.66);
}

html {
    scroll-behavior: smooth;
}

html,
body,
[data-testid="stApp"],
[data-testid="stAppViewContainer"] {
    background: var(--qsvl-charcoal);
}

[data-testid="stMain"] {
    background: transparent;
}

header[data-testid="stHeader"] {
    min-height: 4.75rem;
    height: 4.75rem;
    background: rgba(45, 52, 54, 0.90);
    border-bottom: 1px solid rgba(212, 175, 55, 0.42);
    box-shadow: none;
    -webkit-backdrop-filter: blur(14px);
    backdrop-filter: blur(14px);
}

[data-testid="stToolbar"] {
    min-height: 4.75rem;
    padding-inline: clamp(0.8rem, 2.4vw, 2.25rem);
}

header button[data-testid="stBaseButton-header"]:has(
    [data-testid="stToolbarActionButtonLabel"]
) {
    display: none;
}

[data-testid="stTopNavLinkContainer"] {
    padding-block: 0.72rem;
}

[data-testid="stTopNavLink"] {
    min-height: 2.85rem;
    padding: 0.62rem 0.95rem;
    gap: 0.48rem;
    border: 1px solid transparent;
    border-radius: 0;
    color: rgba(249, 249, 249, 0.72);
    transition: color 140ms ease, background-color 140ms ease, border-color 140ms ease;
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
    color: var(--qsvl-ivory);
    background: rgba(10, 61, 98, 0.46);
    border-color: rgba(249, 249, 249, 0.16);
}

[data-testid="stTopNavLink"][aria-current="page"] {
    color: var(--qsvl-ivory);
    background: var(--qsvl-navy);
    border-color: var(--qsvl-gold);
}

[data-testid="stMainBlockContainer"] {
    max-width: 96rem;
    padding-top: 5.8rem;
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
    margin-bottom: 0.5rem;
    padding: 1.1rem 4.25rem 1.15rem 1.25rem;
    border: 0 !important;
    border-left: 3px solid var(--qsvl-gold);
    background: transparent !important;
    box-shadow: none !important;
    -webkit-backdrop-filter: none !important;
    backdrop-filter: none !important;
}

.st-key-page_header:hover {
    border-color: transparent !important;
    border-left-color: var(--qsvl-gold) !important;
    background: transparent !important;
}

.st-key-page_header > [data-testid="stVerticalBlock"] {
    padding: 0 !important;
    border: 0 !important;
    background: transparent !important;
    box-shadow: none !important;
    -webkit-backdrop-filter: none !important;
    backdrop-filter: none !important;
}

.st-key-page_header h1 {
    max-width: 20ch;
    color: var(--qsvl-ivory);
    letter-spacing: -0.035em;
    line-height: 1.04;
    text-wrap: balance;
}

.st-key-page_header [data-testid="stCaptionContainer"] p {
    color: var(--qsvl-gold);
    letter-spacing: 0.14em;
}

.st-key-page_header > [data-testid="stVerticalBlock"] > [data-testid="stElementContainer"]:last-child {
    max-width: 76ch;
}

[data-testid="stCaptionContainer"] p {
    color: var(--qsvl-muted);
}

h2,
h3 {
    color: var(--qsvl-ivory);
    letter-spacing: -0.018em;
}

.st-key-page_status {
    position: absolute;
    z-index: 3;
    top: 1rem;
    right: 1rem;
    display: grid;
    width: 2.75rem !important;
    min-width: 2.75rem;
    height: 2.75rem;
    place-items: center;
    border: 0 !important;
    background: transparent !important;
    box-shadow: none !important;
}

.st-key-page_status [data-testid="stVerticalBlock"] {
    display: grid;
    height: 100%;
    place-items: center;
    gap: 0 !important;
}

.st-key-page_status [data-testid="stMarkdownContainer"] p {
    margin: 0;
    line-height: 1;
}

.st-key-page_status [data-testid="stMarkdownContainer"] span[role="img"] {
    color: var(--qsvl-gold);
    font-size: 2rem !important;
}

.st-key-research_context [data-testid="stMarkdownContainer"] p,
.st-key-app_footer [data-testid="stCaptionContainer"] p {
    margin: 0;
}

.st-key-research_context {
    min-height: 3.25rem;
    display: flex;
    flex-direction: column;
    justify-content: center !important;
    border-left: 3px solid var(--qsvl-gold) !important;
}

.st-key-research_context [data-testid="stVerticalBlock"] {
    padding: 0.75rem 1rem !important;
}

.st-key-research_context [data-testid="stMarkdownContainer"] p {
    line-height: 1.35;
}

.st-key-app_footer {
    margin-top: 0.3rem;
    border-top: 1px solid rgba(249, 249, 249, 0.14);
}

.st-key-app_footer > [data-testid="stVerticalBlock"] {
    padding: 0.85rem 0 0 !important;
    border: 0 !important;
    background: transparent !important;
    -webkit-backdrop-filter: none !important;
    backdrop-filter: none !important;
}

[class*="st-key-section_"] {
    position: sticky;
    z-index: 5;
    top: 4.8rem;
    margin-top: 0.6rem;
    border-left: 3px solid var(--qsvl-gold);
    background: rgba(45, 52, 54, 0.92);
    -webkit-backdrop-filter: blur(12px);
    backdrop-filter: blur(12px);
}

[class*="st-key-section_"] > [data-testid="stVerticalBlock"] {
    gap: 0.1rem !important;
    padding: 0.72rem 1rem !important;
    border: 0 !important;
    background: transparent !important;
    box-shadow: none !important;
    -webkit-backdrop-filter: none !important;
    backdrop-filter: none !important;
}

[class*="st-key-section_"] h3,
[class*="st-key-section_"] [data-testid="stCaptionContainer"] p {
    margin: 0;
}

[data-testid="stLayoutWrapper"] > [data-testid="stVerticalBlock"],
[data-testid="stMetric"] {
    border: 1px solid var(--qsvl-border) !important;
    border-radius: 0 !important;
    background: var(--qsvl-glass) !important;
    box-shadow: none !important;
    -webkit-backdrop-filter: blur(8px);
    backdrop-filter: blur(8px);
    transition: border-color 140ms ease, background-color 140ms ease;
}

[data-testid="stLayoutWrapper"] > [data-testid="stVerticalBlock"] {
    padding: clamp(0.95rem, 1.4vw, 1.2rem) !important;
}

[data-testid="stLayoutWrapper"]:has([data-testid="stVegaLiteChart"]) > [data-testid="stVerticalBlock"] {
    border-left: 3px solid var(--qsvl-gold) !important;
    background: rgba(10, 61, 98, 0.34) !important;
    scroll-margin-top: 7rem;
}

[data-testid="stLayoutWrapper"] > [data-testid="stVerticalBlock"]:hover {
    z-index: 2;
    border-color: var(--qsvl-border-focus) !important;
    background: var(--qsvl-glass-strong) !important;
}

.st-key-page_header[data-testid="stVerticalBlock"],
.st-key-page_header[data-testid="stVerticalBlock"]:hover {
    padding: 1.1rem 4.25rem 1.15rem 1.25rem !important;
    border: 0 !important;
    border-left: 3px solid var(--qsvl-gold) !important;
    background: transparent !important;
    box-shadow: none !important;
    -webkit-backdrop-filter: none !important;
    backdrop-filter: none !important;
}

[class*="st-key-section_"][data-testid="stVerticalBlock"],
[class*="st-key-section_"][data-testid="stVerticalBlock"]:hover {
    padding: 0.72rem 1rem !important;
    border: 0 !important;
    border-left: 3px solid var(--qsvl-gold) !important;
    background: rgba(45, 52, 54, 0.92) !important;
    box-shadow: none !important;
}

.st-key-app_footer[data-testid="stVerticalBlock"],
.st-key-app_footer[data-testid="stVerticalBlock"]:hover {
    padding: 0.85rem 0 0 !important;
    border: 0 !important;
    border-top: 1px solid rgba(249, 249, 249, 0.14) !important;
    background: transparent !important;
    box-shadow: none !important;
    -webkit-backdrop-filter: none !important;
    backdrop-filter: none !important;
}

[data-testid="stMetric"] {
    min-height: 7.1rem;
    justify-content: center;
    padding: 1.05rem 1.15rem;
    border-top: 2px solid rgba(212, 175, 55, 0.72) !important;
}

[data-testid="stMetric"]:hover {
    z-index: 3;
    border-color: var(--qsvl-border-focus) !important;
    background: rgba(10, 61, 98, 0.56) !important;
}

.st-key-page_header .st-key-page_status,
.st-key-page_header .st-key-page_status:hover {
    border: 0 !important;
    background: transparent !important;
    box-shadow: none !important;
    -webkit-backdrop-filter: none !important;
    backdrop-filter: none !important;
}

.st-key-brief_metrics > [data-testid="stVerticalBlock"] {
    padding: 0 !important;
    border: 0 !important;
    background: transparent !important;
    box-shadow: none !important;
    -webkit-backdrop-filter: none !important;
    backdrop-filter: none !important;
}

.st-key-brief_metrics [data-testid="stMetric"] {
    min-width: min(100%, 13rem);
}

[data-testid="stMetricLabel"] p {
    color: rgba(249, 249, 249, 0.68);
    font-size: 0.82rem;
    font-weight: 600;
    letter-spacing: 0.025em;
}

[data-testid="stMetricValue"] {
    color: var(--qsvl-ivory);
    font-variant-numeric: tabular-nums;
    letter-spacing: -0.035em;
}

[data-testid="stVegaLiteChart"] {
    border-radius: 0;
    animation: qsvl-chart-arrive 200ms ease-out both;
    scroll-margin-top: 7rem;
}

[data-testid="stDataFrame"],
[data-testid="stTable"],
[data-testid="stAlert"],
[data-testid="stExpander"],
[data-testid="stSegmentedControl"],
[data-testid="stSelectbox"] > div {
    border: 1px solid rgba(249, 249, 249, 0.14);
    border-radius: 0;
    background: rgba(10, 61, 98, 0.24);
    -webkit-backdrop-filter: blur(6px);
    backdrop-filter: blur(6px);
    transition: border-color 140ms ease, background-color 140ms ease;
}

[data-testid="stDataFrame"]:hover,
[data-testid="stTable"]:hover,
[data-testid="stAlert"]:hover,
[data-testid="stExpander"]:hover,
[data-testid="stSegmentedControl"]:hover,
[data-testid="stSelectbox"] > div:hover {
    border-color: var(--qsvl-border-focus);
    background: rgba(10, 61, 98, 0.44);
}

[data-testid="stSegmentedControl"] label:has(input:checked) p,
[data-testid="stSegmentedControl"] label:has([aria-checked="true"]) p,
[role="radiogroup"] [role="radio"] p {
    color: var(--qsvl-ivory) !important;
    -webkit-text-fill-color: var(--qsvl-ivory) !important;
    opacity: 1 !important;
}

[role="radiogroup"] [role="radio"][aria-checked="true"],
[role="radiogroup"] label:has(input:checked) {
    border: 1px solid var(--qsvl-gold) !important;
    background: var(--qsvl-navy) !important;
}

[role="radiogroup"] [role="radio"][aria-checked="true"] p,
[role="radiogroup"] label:has(input:checked) p {
    font-weight: 700 !important;
}

[data-testid="stAlert"] {
    border-left: 3px solid var(--qsvl-gold);
}

[data-testid="stDataFrame"],
[data-testid="stTable"],
[data-testid="stAlert"] {
    overflow: hidden;
}

[data-testid^="stBaseButton"],
[data-testid="stDownloadButton"] button {
    border-radius: 0 !important;
    box-shadow: none !important;
    transition: border-color 140ms ease, background-color 140ms ease;
}

[data-testid^="stBaseButton"]:hover,
[data-testid="stDownloadButton"] button:hover {
    border-color: var(--qsvl-gold);
    box-shadow: none !important;
}

[data-testid="stMainBlockContainer"] > [data-testid="stVerticalBlock"] {
    animation: qsvl-page-arrive 160ms ease-out both;
}

@keyframes qsvl-page-arrive {
    from { opacity: 0; }
    to { opacity: 1; }
}

@keyframes qsvl-chart-arrive {
    from { opacity: 0; transform: translateY(5px); }
    to { opacity: 1; transform: translateY(0); }
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

    .st-key-page_header {
        padding: 0.9rem 3.25rem 0.9rem 1rem;
    }

    .st-key-page_header h1 {
        max-width: 13ch;
        font-size: 2.1rem;
    }

    .st-key-page_status {
        top: 0.75rem;
        right: 0.75rem;
        width: 2.25rem !important;
        min-width: 2.25rem;
        height: 2.25rem;
    }

    .st-key-page_status [data-testid="stMarkdownContainer"] span[role="img"] {
        font-size: 1.6rem !important;
    }

    [data-testid="stExpandSidebarButton"] {
        width: auto;
        min-width: 4.75rem;
        gap: 0.3rem;
        color: var(--qsvl-ivory);
        border: 1px solid rgba(249, 249, 249, 0.16);
        border-radius: 0;
        background: var(--qsvl-navy);
    }

    [data-testid="stExpandSidebarButton"]::after {
        content: "Pages";
        font-size: 0.8rem;
        font-weight: 600;
        letter-spacing: 0.02em;
    }

    [data-testid="stMainBlockContainer"] {
        padding-top: 5.2rem;
        padding-right: 1rem;
        padding-left: 1rem;
    }

    [data-testid="stMainBlockContainer"] > [data-testid="stVerticalBlock"],
    [data-testid="stHorizontalBlock"] {
        gap: 0.75rem;
    }

    [data-testid="stLayoutWrapper"] > [data-testid="stVerticalBlock"] {
        padding: 1rem !important;
    }

    [class*="st-key-section_"] {
        top: 4.15rem;
    }

    .st-key-research_context {
        min-height: 3.5rem;
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
}
</style>
"""


def inject_visual_system() -> None:
    """Inject static CSS only; no script or untrusted input reaches the page."""

    st.html(visual_css())


def render_page_header(
    eyebrow: str,
    title: str,
    description: str,
) -> None:
    """Render a prominent, unboxed page heading with a Material status mark."""

    with st.container(key="page_header", gap="xsmall"):
        with st.container(
            border=False,
            key="page_status",
            width="content",
            height="content",
            horizontal_alignment="center",
            vertical_alignment="center",
            gap=None,
        ):
            st.markdown(":material/handyman:", width="content")
        st.caption(eyebrow.upper())
        st.title(title, width="content")
        st.markdown(description)


def render_research_boundary(meta: dict[str, Any]) -> None:
    """Show the full research context once, on the canonical brief."""

    with st.container(
        border=True,
        key="research_context",
        vertical_alignment="center",
        gap="xxsmall",
    ):
        st.markdown(
            f":material/candlestick_chart: **{meta['instrument']}** · "
            f"{meta['research_window']} · snapshot {meta['snapshot_date']} · "
            "reviewed aggregates only",
            text_alignment="left",
        )


def render_section_header(title: str, description: str, *, key: str) -> None:
    """Render a sticky, unboxed section marker that preserves context while scrolling."""

    with st.container(border=False, key=f"section_{key}", gap="xxsmall"):
        st.subheader(title)
        st.caption(description)


def render_app_footer(meta: dict[str, Any]) -> None:
    """Render a concise global artifact footer without a card treatment."""

    with st.container(border=False, key="app_footer", gap="xxsmall"):
        st.caption(
            f"Research snapshot · schema {meta['schema_version']} · "
            "aggregate evidence only · raw market data excluded"
        )
