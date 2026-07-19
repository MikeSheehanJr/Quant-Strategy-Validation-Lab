"""Default, summary-first research page."""

from __future__ import annotations

import pandas as pd
import streamlit as st

from src.charts import annual_pnl, equity_curve
from src.data import load_snapshot, monthly_frame, snapshot_sha256, yearly_frame
from src.metrics import profitable_year_count
from src.ui import render_page_header, render_research_boundary, render_section_header


snapshot = load_snapshot()
headline = snapshot["headline"]
meta = snapshot["meta"]
monthly = monthly_frame(snapshot)
yearly = yearly_frame(snapshot)
profitable, periods = profitable_year_count(yearly)

render_page_header(
    "Public quant research · portfolio build",
    "Quant strategy validation lab",
    "**Research question:** Can a deliberately simple intraday strategy survive costs, "
    "out-of-sample testing, parameter perturbation, and adversarial review?",
)
render_research_boundary(meta)

conclusion_col, metrics_col = st.columns([1.35, 1], gap="small")
with conclusion_col:
    with st.container(
        border=True,
        height="stretch",
        gap="small",
        vertical_alignment="distribute",
    ):
        st.subheader("Research decision")
        st.badge(
            "Advance to paper validation",
            icon=":material/arrow_forward:",
            color="blue",
        )
        st.markdown(
            ":material/check_circle: **Historical gate** · :blue-badge[Reviewed positive]  \n"
            ":material/schedule: **Forward gate** · :gray-badge[Not started]  \n"
            ":material/block: **Deployment claim** · :gray-badge[None]"
        )
        st.caption(
            "The result supports continued testing—not a live or forward-performance claim."
        )
with metrics_col:
    metric_row_one = st.columns(2, gap="small")
    metric_row_one[0].metric(
        "Cost-adjusted trades", f"{headline['trade_count']:,}", border=True, height="stretch"
    )
    metric_row_one[1].metric(
        "Win rate", f"{headline['win_rate_pct']:.1f}%", border=True, height="stretch"
    )
    metric_row_two = st.columns(2, gap="small")
    metric_row_two[0].metric(
        "Profit factor", f"{headline['profit_factor']:.3f}", border=True, height="stretch"
    )
    metric_row_two[1].metric(
        "Calendar-honest Sharpe",
        f"{headline['daily_sharpe']:.2f}",
        border=True,
        height="stretch",
    )

render_section_header(
    "Strategy in plain English",
    "A low-dimensional MNQ opening-range breakout designed for transparent stress testing.",
    key="strategy_sequence",
)
market_col, signal_col, risk_col = st.columns(3, gap="small")
with market_col:
    with st.container(border=True, height="stretch", gap="xxsmall"):
        st.caption("01 / REFERENCE")
        st.subheader("30-minute range")
        st.write("09:30–10:00 ET session high and low")
with signal_col:
    with st.container(border=True, height="stretch", gap="xxsmall"):
        st.caption("02 / ENTRY")
        st.subheader("Completed-bar break")
        st.write("Prior information only · one trade per session")
with risk_col:
    with st.container(border=True, height="stretch", gap="xxsmall"):
        st.caption("03 / EXECUTION")
        st.subheader("1R stop · 1R target")
        st.write("$1.20 round turn · 0.5-tick modeled slippage")

path_col, year_col = st.columns([1.65, 1], gap="small")
with path_col:
    with st.container(border=True):
        st.subheader("Historical research path")
        st.caption(
            "Monthly aggregates, one MNQ contract, after $1.20 round-turn commission and "
            "0.5-tick modeled slippage."
        )
        st.altair_chart(equity_curve(monthly))
with year_col:
    with st.container(border=True):
        st.subheader("Calendar-year outcomes")
        st.caption(
            f"{profitable}/{periods} displayed periods are positive. 2021 begins in June; "
            "2026 ends in June and is partial."
        )
        st.altair_chart(annual_pnl(yearly))

evidence_register = pd.DataFrame(
    [
        {
            "Review": "Lookahead and prior-input audit",
            "State": ":blue-badge[Reviewed]",
            "Interpretation": "No future information found in the reviewed path",
        },
        {
            "Review": "Costs, slippage, and fill resolution",
            "State": ":blue-badge[Reviewed]",
            "Interpretation": "Headline result remains positive in the displayed battery",
        },
        {
            "Review": "CPCV, permutation, regime, and parameter stress",
            "State": ":blue-badge[Reviewed]",
            "Interpretation": "Historical fragility challenged from multiple angles",
        },
        {
            "Review": "Paper forward test",
            "State": ":gray-badge[Missing]",
            "Interpretation": "No prospective performance conclusion",
        },
        {
            "Review": "Pre-2021 and broader provider coverage",
            "State": ":gray-badge[Missing]",
            "Interpretation": "Time and source coverage remain bounded",
        },
        {
            "Review": "Persistence of historical performance",
            "State": ":gray-badge[Unknowable]",
            "Interpretation": "Historical evidence is not a forecast",
        },
    ]
)
with st.container(border=True, key="brief_evidence_register"):
    st.subheader("Evidence register")
    st.caption("Reviewed support and unresolved limits in one decision surface.")
    st.dataframe(
        evidence_register,
        hide_index=True,
        column_config={
            "Review": st.column_config.TextColumn("Review", pinned=True, width="medium"),
            "State": st.column_config.MarkdownColumn("State", width="small"),
            "Interpretation": st.column_config.TextColumn(
                "What it establishes", width="large"
            ),
        },
    )

with st.container(border=True, key="research_disclosure", gap="xxsmall"):
    st.caption(
        "Historical research only—not a trading recommendation or signal service. "
        f"Snapshot digest: `{snapshot_sha256()}`"
    )
