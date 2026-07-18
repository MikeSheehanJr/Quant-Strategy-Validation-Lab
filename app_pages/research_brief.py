"""Default, summary-first research page."""

from __future__ import annotations

import streamlit as st

from src.charts import annual_pnl, equity_curve
from src.data import load_snapshot, monthly_frame, snapshot_sha256, yearly_frame
from src.metrics import profitable_year_count
from src.ui import render_page_header, render_research_boundary


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

with st.container(border=True):
    st.markdown("**Current conclusion**")
    st.write(
        "The historical result is positive across the reviewed robustness battery, but it is "
        "not accepted as forward evidence. Paper validation has not started, and the project "
        "makes no live-performance or deployment claim."
    )
    st.markdown(
        ":blue-badge[Historical evidence reviewed] "
        ":gray-badge[Forward evidence not started]"
    )

with st.container(horizontal=True):
    st.metric("Cost-adjusted trades", f"{headline['trade_count']:,}", border=True)
    st.metric("Win rate", f"{headline['win_rate_pct']:.1f}%", border=True)
    st.metric("Profit factor", f"{headline['profit_factor']:.3f}", border=True)
    st.metric("Calendar-honest Sharpe", f"{headline['daily_sharpe']:.2f}", border=True)

with st.container(border=True):
    st.subheader("Strategy in plain English")
    st.write(
        "The headline case study is a rules-based opening-range breakout on the Micro "
        "E-mini Nasdaq-100 futures contract (MNQ). It tests whether expansion beyond the "
        "regular-session opening range remains positive after implementation costs and "
        "adversarial validation."
    )
    market_col, signal_col, risk_col = st.columns(3, gap="large")
    with market_col:
        st.markdown("**1 · Define the range**")
        st.write("The first 30 minutes of the regular session set the reference high and low.")
    with signal_col:
        st.markdown("**2 · Test the break**")
        st.write(
            "A completed bar must close outside the range. Only prior information may determine "
            "eligibility, and the model allows at most one trade per session."
        )
    with risk_col:
        st.markdown("**3 · Model execution**")
        st.write(
            "The frozen design uses a 1:1 stop and target, explicit commission, modeled "
            "slippage, and worse-fill stress tests."
        )
    st.caption(
        "The low-dimensional rule is intentional: it makes bias, parameter sensitivity, and "
        "failure modes easier to inspect than a black-box model."
    )

path_col, year_col = st.columns([1.65, 1], gap="large")
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

st.subheader("Evidence boundary")
evidence_col, missing_col = st.columns(2, gap="large")
with evidence_col:
    with st.container(border=True):
        st.markdown("**Reviewed evidence**")
        st.markdown(
            "- Strictly prior inputs and an independent lookahead audit\n"
            "- Costs, slippage, and multiple fill resolutions\n"
            "- Combinatorial purged cross-validation (CPCV)\n"
            "- Permutation, parameter, regime, and instrument stress tests"
        )
with missing_col:
    with st.container(border=True):
        st.markdown("**Evidence still missing**")
        st.markdown(
            "- A completed paper forward-test\n"
            "- Pre-2021 MNQ/NQ coverage\n"
            "- Broader cross-provider reconciliation\n"
            "- Evidence that historical performance will persist"
        )

st.caption(
    "Historical research only—not a trading recommendation or signal service. "
    f"Snapshot digest: `{snapshot_sha256()}`"
)
