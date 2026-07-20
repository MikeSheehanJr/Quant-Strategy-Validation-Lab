"""Shared Streamlit presentation helpers and the research visual system."""

from __future__ import annotations

from typing import Any

import streamlit as st


def visual_css() -> str:
    """Build the light, information-first visual system used by every app page."""

    return """
<style>
:root {
    --qsvl-charcoal: #2D3436;
    --qsvl-navy: #0A3D62;
    --qsvl-gold: #D4AF37;
    --qsvl-gold-ink: #806710;
    --qsvl-ivory: #F9F9F9;
    --qsvl-white: #FFFFFF;
    --qsvl-panel: #F0F3F4;
    --qsvl-border: #D8DEE1;
    --qsvl-muted: #657179;
    --qsvl-space: clamp(0.9rem, 1.45vw, 1.25rem);
}

html {
    scroll-behavior: smooth;
}

html,
body,
[data-testid="stApp"],
[data-testid="stAppViewContainer"] {
    background: var(--qsvl-ivory);
    color: var(--qsvl-charcoal);
}

[data-testid="stMain"] {
    background: transparent;
}

header[data-testid="stHeader"] {
    min-height: 4.6rem;
    height: 4.6rem;
    background: rgba(249, 249, 249, 0.98);
    border-bottom: 1px solid var(--qsvl-border);
    box-shadow: none;
}

[data-testid="stToolbar"] {
    min-height: 4.6rem;
    padding-inline: clamp(0.8rem, 2.4vw, 2.25rem);
}

header button[data-testid="stBaseButton-header"]:has(
    [data-testid="stToolbarActionButtonLabel"]
) {
    display: none;
}

[data-testid="stTopNavLinkContainer"] {
    padding-block: 0.7rem;
    overflow-x: auto;
    scrollbar-width: none;
    white-space: nowrap;
}

[data-testid="stTopNavLinkContainer"]::-webkit-scrollbar {
    display: none;
}

[data-testid="stExpandSidebarButton"] {
    display: none !important;
}

.st-key-mobile_nav_menu {
    display: none;
}

[data-testid="stTopNavLink"] {
    min-height: 2.75rem;
    padding: 0.6rem 0.9rem;
    gap: 0.45rem;
    border: 0;
    border-bottom: 2px solid transparent;
    border-radius: 0;
    color: var(--qsvl-muted);
    background: transparent;
    transition: color 120ms ease, border-color 120ms ease;
}

[data-testid="stTopNavLink"] p {
    font-size: 0.94rem;
    font-weight: 600;
    letter-spacing: 0.005em;
}

[data-testid="stTopNavLink"] [data-testid="stIconMaterial"] {
    font-size: 1.08rem;
}

[data-testid="stTopNavLink"]:hover {
    color: var(--qsvl-navy);
    border-bottom-color: rgba(212, 175, 55, 0.48);
    background: transparent;
}

[data-testid="stTopNavLink"][aria-current="page"] {
    color: var(--qsvl-navy);
    border-bottom-color: var(--qsvl-gold);
    background: transparent;
}

[data-testid="stMainBlockContainer"] {
    max-width: 94rem;
    padding-top: 5.7rem;
    padding-right: clamp(1rem, 3.25vw, 3.5rem);
    padding-bottom: 4.5rem;
    padding-left: clamp(1rem, 3.25vw, 3.5rem);
}

[data-testid="stMainBlockContainer"] > [data-testid="stVerticalBlock"] {
    gap: var(--qsvl-space);
}

[data-testid="stHorizontalBlock"] {
    gap: var(--qsvl-space);
}

.st-key-page_header,
.st-key-page_header[data-testid="stVerticalBlock"],
.st-key-page_header[data-testid="stVerticalBlock"]:hover {
    position: relative;
    margin-bottom: 0.55rem;
    padding: 1rem 4rem 1.05rem 1.2rem !important;
    border: 0 !important;
    border-left: 3px solid var(--qsvl-gold) !important;
    background: transparent !important;
    box-shadow: none !important;
}

.st-key-page_header > [data-testid="stVerticalBlock"] {
    padding: 0 !important;
    border: 0 !important;
    background: transparent !important;
    box-shadow: none !important;
}

.st-key-page_header h1 {
    max-width: 20ch;
    color: var(--qsvl-charcoal);
    letter-spacing: -0.038em;
    line-height: 1.02;
    text-wrap: balance;
}

.st-key-page_header [data-testid="stCaptionContainer"] p {
    color: var(--qsvl-gold-ink);
    letter-spacing: 0.13em;
}

.st-key-page_header > [data-testid="stVerticalBlock"] > [data-testid="stElementContainer"]:last-child {
    max-width: 78ch;
}

[data-testid="stCaptionContainer"] p {
    color: var(--qsvl-muted);
}

h2,
h3 {
    color: var(--qsvl-charcoal);
    letter-spacing: -0.02em;
}

.st-key-page_status {
    position: absolute;
    z-index: 3;
    top: 0.9rem;
    right: 0.8rem;
    display: grid;
    width: 2.5rem !important;
    min-width: 2.5rem;
    height: 2.5rem;
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
    color: var(--qsvl-gold-ink);
    font-size: 1.8rem !important;
}

.st-key-research_context,
.st-key-research_context[data-testid="stVerticalBlock"] {
    min-height: 2.9rem;
    display: flex;
    flex-direction: column;
    justify-content: center !important;
    padding: 0 !important;
    border: 0 !important;
    border-bottom: 1px solid var(--qsvl-border) !important;
    background: transparent !important;
    box-shadow: none !important;
}

.st-key-research_context [data-testid="stVerticalBlock"] {
    padding: 0.55rem 0 0.75rem !important;
    border: 0 !important;
    background: transparent !important;
}

.st-key-research_context [data-testid="stMarkdownContainer"] p,
.st-key-app_footer [data-testid="stCaptionContainer"] p {
    margin: 0;
}

.st-key-app_footer,
.st-key-app_footer[data-testid="stVerticalBlock"] {
    margin-top: 0.4rem;
    padding: 0.85rem 0 0 !important;
    border: 0 !important;
    border-top: 1px solid var(--qsvl-border) !important;
    background: transparent !important;
    box-shadow: none !important;
}

.st-key-app_footer > [data-testid="stVerticalBlock"] {
    padding: 0 !important;
    border: 0 !important;
    background: transparent !important;
}

[class*="st-key-section_"],
[class*="st-key-section_"][data-testid="stVerticalBlock"],
[class*="st-key-section_"][data-testid="stVerticalBlock"]:hover {
    position: sticky;
    z-index: 5;
    top: 4.6rem;
    margin-top: 1.2rem;
    padding: 0.65rem 0 !important;
    border: 0 !important;
    border-bottom: 1px solid var(--qsvl-border) !important;
    background: rgba(249, 249, 249, 0.98) !important;
    box-shadow: none !important;
}

[class*="st-key-section_"] > [data-testid="stVerticalBlock"] {
    gap: 0.08rem !important;
    padding: 0 !important;
    border: 0 !important;
    background: transparent !important;
    box-shadow: none !important;
}

[class*="st-key-section_"] h3,
[class*="st-key-section_"] [data-testid="stCaptionContainer"] p {
    margin: 0;
}

/* Containers are layout first. Only named controls and callouts regain a surface. */
[data-testid="stLayoutWrapper"] > [data-testid="stVerticalBlock"] {
    padding: 0.25rem 0 !important;
    border: 0 !important;
    border-radius: 0 !important;
    background: transparent !important;
    box-shadow: none !important;
}

.st-key-forward_status,
.st-key-risk_caveat,
.st-key-implementation_review_boundary,
.st-key-research_disclosure {
    padding: 1.05rem 1.15rem !important;
    border: 0 !important;
    border-left: 3px solid var(--qsvl-navy) !important;
    background: var(--qsvl-panel) !important;
}

.st-key-brief_research_read[data-testid="stVerticalBlock"],
.st-key-brief_research_read[data-testid="stVerticalBlock"]:hover {
    position: relative;
    padding: clamp(1.25rem, 2.3vw, 2rem) !important;
    border: 0 !important;
    border-top: 5px solid var(--qsvl-gold) !important;
    background: var(--qsvl-navy) !important;
    box-shadow: none !important;
}

.st-key-brief_research_read h3,
.st-key-brief_research_read p,
.st-key-brief_research_read strong,
.st-key-brief_research_read [data-testid="stIconMaterial"] {
    color: var(--qsvl-white) !important;
}

.st-key-brief_research_read > [data-testid="stElementContainer"]:first-child p {
    color: #F0D87A !important;
    letter-spacing: 0.13em;
}

.st-key-brief_gate[data-testid="stVerticalBlock"] {
    min-height: 9.5rem;
    justify-content: center;
    padding: 1rem 1.1rem !important;
    border: 1px solid rgba(255, 255, 255, 0.28) !important;
    background: rgba(255, 255, 255, 0.08) !important;
}

.st-key-brief_gate [data-testid="stCaptionContainer"] p {
    color: #F0D87A !important;
    letter-spacing: 0.11em;
}

.st-key-robustness_switcher,
.st-key-monte_carlo_controls,
.st-key-parameter_controls,
.st-key-version_picker {
    padding: 0.9rem 1rem !important;
    border: 1px solid var(--qsvl-border) !important;
    background: var(--qsvl-white) !important;
}

[data-testid="stLayoutWrapper"]:has([data-testid="stVegaLiteChart"]) > [data-testid="stVerticalBlock"] {
    padding: 0.35rem 0 0.7rem !important;
    border: 0 !important;
    background: transparent !important;
    scroll-margin-top: 7rem;
}

.st-key-page_header .st-key-page_status,
.st-key-page_header .st-key-page_status:hover,
.st-key-brief_metrics > [data-testid="stVerticalBlock"] {
    padding: 0 !important;
    border: 0 !important;
    background: transparent !important;
    box-shadow: none !important;
}

[data-testid="stMetric"] {
    min-height: 6.4rem;
    justify-content: center;
    padding: 0.8rem 1rem;
    border: 0 !important;
    border-left: 1px solid var(--qsvl-border) !important;
    border-radius: 0 !important;
    background: transparent !important;
    box-shadow: none !important;
}

[data-testid="stMetric"]:hover {
    border-left-color: var(--qsvl-gold) !important;
    background: rgba(212, 175, 55, 0.06) !important;
}

.st-key-brief_metrics [data-testid="stMetric"] {
    min-width: min(100%, 13rem);
}

.st-key-brief_metrics > [data-testid="stVerticalBlock"] {
    align-items: stretch;
}

.st-key-brief_metrics [class*="st-key-brief_metric_"][data-testid="stVerticalBlock"] {
    min-width: min(100%, 13rem);
    min-height: 7.25rem;
    justify-content: center;
    padding: 0.2rem !important;
    border: 1px solid var(--qsvl-border) !important;
    background: var(--qsvl-white) !important;
}

.st-key-brief_metrics [class*="st-key-brief_metric_"] [data-testid="stMetric"] {
    min-height: 6.75rem;
    padding: 0.85rem 1rem;
    border: 0 !important;
    background: transparent !important;
}

.st-key-brief_metrics .st-key-brief_metric_pnl[data-testid="stVerticalBlock"] {
    border-color: var(--qsvl-navy) !important;
    background: var(--qsvl-navy) !important;
}

.st-key-brief_metrics .st-key-brief_metric_pnl [data-testid="stMetricLabel"] p,
.st-key-brief_metrics .st-key-brief_metric_pnl [data-testid="stMetricValue"] {
    color: var(--qsvl-white) !important;
}

.st-key-brief_metrics .st-key-brief_metric_trades[data-testid="stVerticalBlock"] {
    border-color: var(--qsvl-navy) !important;
    background: var(--qsvl-panel) !important;
}

.st-key-brief_metrics .st-key-brief_metric_win_rate[data-testid="stVerticalBlock"] {
    border-top: 5px solid var(--qsvl-gold) !important;
}

.st-key-brief_metrics .st-key-brief_metric_profit_factor[data-testid="stVerticalBlock"] {
    border-color: var(--qsvl-gold) !important;
    background: var(--qsvl-gold) !important;
}

.st-key-brief_metrics .st-key-brief_metric_profit_factor [data-testid="stMetricLabel"] p,
.st-key-brief_metrics .st-key-brief_metric_profit_factor [data-testid="stMetricValue"] {
    color: var(--qsvl-charcoal) !important;
}

[data-testid="stMetricLabel"] p {
    color: var(--qsvl-muted);
    font-size: 0.8rem;
    font-weight: 600;
    letter-spacing: 0.02em;
}

[data-testid="stMetricValue"] {
    color: var(--qsvl-navy);
    font-variant-numeric: tabular-nums;
    letter-spacing: -0.04em;
}

[data-testid="stVegaLiteChart"] {
    border-radius: 0;
    animation: qsvl-chart-arrive 180ms ease-out both;
    scroll-margin-top: 7rem;
}

[data-testid="stDataFrame"],
[data-testid="stTable"] {
    overflow: hidden;
    border: 1px solid var(--qsvl-border);
    border-radius: 0;
    background: var(--qsvl-white);
}

[data-testid="stAlert"] {
    border: 0;
    border-left: 3px solid var(--qsvl-gold);
    border-radius: 0;
    background: var(--qsvl-panel);
}

[data-testid="stExpander"],
[data-testid="stSegmentedControl"],
[data-testid="stSelectbox"] > div {
    border: 1px solid var(--qsvl-border);
    border-radius: 0;
    background: var(--qsvl-white);
    box-shadow: none;
}

[data-testid="stSegmentedControl"] label:has(input:checked) p,
[data-testid="stSegmentedControl"] label:has([aria-checked="true"]) p,
[role="radiogroup"] [role="radio"] p {
    color: var(--qsvl-charcoal) !important;
    -webkit-text-fill-color: var(--qsvl-charcoal) !important;
    opacity: 1 !important;
}

[role="radiogroup"] [role="radio"][aria-checked="true"],
[role="radiogroup"] label:has(input:checked) {
    border: 1px solid var(--qsvl-navy) !important;
    background: var(--qsvl-navy) !important;
}

[role="radiogroup"] [role="radio"][aria-checked="true"] p,
[role="radiogroup"] label:has(input:checked) p {
    color: var(--qsvl-white) !important;
    -webkit-text-fill-color: var(--qsvl-white) !important;
    font-weight: 700 !important;
}

[data-testid^="stBaseButton"],
[data-testid="stDownloadButton"] button {
    border-radius: 0 !important;
    box-shadow: none !important;
    transition: border-color 120ms ease, background-color 120ms ease;
}

[data-testid^="stBaseButton"]:hover,
[data-testid="stDownloadButton"] button:hover {
    border-color: var(--qsvl-navy);
    box-shadow: none !important;
}

[data-testid="stMainBlockContainer"] > [data-testid="stVerticalBlock"] {
    animation: qsvl-page-arrive 140ms ease-out both;
}

@keyframes qsvl-page-arrive {
    from { opacity: 0; }
    to { opacity: 1; }
}

@keyframes qsvl-chart-arrive {
    from { opacity: 0; transform: translateY(4px); }
    to { opacity: 1; transform: translateY(0); }
}

@media (max-width: 800px) {
    header[data-testid="stHeader"],
    [data-testid="stToolbar"] {
        min-height: 4.1rem;
        height: 4.1rem;
    }

    [data-testid="stTopNavLinkContainer"] {
        display: none;
    }

    [data-testid="stMainBlockContainer"] > [data-testid="stVerticalBlock"] {
        animation: none;
    }

    .st-key-mobile_nav_menu,
    .st-key-mobile_nav_menu[data-testid="stPopover"] {
        position: fixed;
        z-index: 1000001;
        top: 0.62rem;
        left: 0.72rem;
        display: block !important;
        width: 2.8rem;
        padding: 0 !important;
    }

    .st-key-mobile_nav_menu [data-testid="stPopover"] {
        width: 2.8rem;
    }

    .st-key-mobile_nav_menu [data-testid="stPopoverButton"] {
        width: 2.8rem;
        min-width: 2.8rem;
        height: 2.8rem;
        min-height: 2.8rem;
        padding: 0 !important;
        border: 1px solid var(--qsvl-border) !important;
        background: var(--qsvl-white) !important;
    }

    .st-key-mobile_nav_menu [data-testid="stPopoverButton"] p,
    .st-key-mobile_nav_menu [data-testid="stPopoverButton"] [aria-hidden="true"] {
        display: none;
    }

    .st-key-mobile_nav_menu [data-testid="stIconMaterial"] {
        margin: 0 !important;
        color: var(--qsvl-navy);
        font-size: 1.45rem !important;
    }

    .st-key-page_header,
    .st-key-page_header[data-testid="stVerticalBlock"] {
        padding: 0.85rem 3rem 0.85rem 0.9rem !important;
    }

    .st-key-page_header h1 {
        max-width: 14ch;
        font-size: 2.05rem;
    }

    .st-key-page_status {
        top: 0.65rem;
        right: 0.55rem;
        width: 2.15rem !important;
        min-width: 2.15rem;
        height: 2.15rem;
    }

    .st-key-page_status [data-testid="stMarkdownContainer"] span[role="img"] {
        font-size: 1.5rem !important;
    }

    [data-testid="stMainBlockContainer"] {
        padding-top: 5.1rem;
        padding-right: 1rem;
        padding-left: 1rem;
    }

    [data-testid="stMainBlockContainer"] > [data-testid="stVerticalBlock"],
    [data-testid="stHorizontalBlock"] {
        gap: 0.8rem;
    }

    [class*="st-key-section_"] {
        top: 4.1rem;
    }

    [data-testid="stMetric"] {
        min-height: 5.8rem;
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


def render_mobile_navigation(pages: list[Any]) -> None:
    """Render a compact page menu that is visible only on narrow screens."""

    with st.popover(
        "Navigation",
        icon=":material/menu:",
        type="tertiary",
        width="content",
        key="mobile_nav_menu",
    ):
        st.caption("PAGES")
        for nav_page in pages:
            st.page_link(nav_page, width="stretch")


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
        border=False,
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
    """Render a quiet section marker that keeps context visible while scrolling."""

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
