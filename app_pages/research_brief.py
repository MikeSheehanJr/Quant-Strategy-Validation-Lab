"""Default, summary-first research page."""

from __future__ import annotations

import pandas as pd
import streamlit as st

from src.charts import annual_pnl, equity_curve
from src.data import load_snapshot, monthly_frame, snapshot_sha256, yearly_frame
from src.ui import render_page_header, render_research_boundary, render_section_header


snapshot = load_snapshot()
headline = snapshot["headline"]
meta = snapshot["meta"]
monthly = monthly_frame(snapshot)
yearly = yearly_frame(snapshot)
complete_years = yearly.loc[yearly["period_status"] == "Complete"]
positive_complete_years = int((complete_years["pnl_usd"] > 0).sum())

render_page_header(
    "AI assisted passion project · iterative validation",
    "Quant strategy validation lab",
    "I started this as a personal strategy experiment. It became a disciplined validation "
    "lab for one question: can a deliberately simple opening range breakout survive costs, "
    "out of sample checks, parameter changes, and skeptical review?",
)
render_research_boundary(meta)

with st.container(border=False, key="brief_research_read", gap="small"):
    st.caption("MY CURRENT READ")
    read_col, gate_col = st.columns([1.55, 1], gap="medium", vertical_alignment="center")
    with read_col:
        st.subheader("The strategy has earned a paper forward test, not a deployment claim.")
        st.write(
            "I’m encouraged that the simple rule set remains positive after costs and the "
            "stress tests shown here. Now it has to prove itself prospectively, without "
            "hindsight."
        )
    with gate_col:
        with st.container(border=False, key="brief_gate", gap="xxsmall"):
            st.caption("RESEARCH GATE")
            st.markdown(
                ":material/check_circle: **Reviewed** · Historical evidence  \n"
                ":material/arrow_forward: **Now** · Paper forward setup  \n"
                ":material/block: **Not claimed** · Live or forward performance"
            )

with st.container(horizontal=True, key="brief_metrics", gap="small"):
    with st.container(border=False, key="brief_metric_pnl"):
        st.metric(
            "Net P&L per contract",
            f"${headline['net_pnl_per_contract_usd']:,.0f}",
            border=False,
        )
    with st.container(border=False, key="brief_metric_trades"):
        st.metric("Cost adjusted trades", f"{headline['trade_count']:,}", border=False)
    with st.container(border=False, key="brief_metric_win_rate"):
        st.metric("Win rate", f"{headline['win_rate_pct']:.1f}%", border=False)
    with st.container(border=False, key="brief_metric_profit_factor"):
        st.metric("Profit factor", f"{headline['profit_factor']:.3f}", border=False)

path_col, year_col = st.columns([1.7, 1], gap="small")
with path_col:
    with st.container(
        border=True,
        height="stretch",
        key="brief_path_chart",
        gap="xxsmall",
    ):
        st.subheader("Historical research path")
        st.caption(
            "One MNQ contract · net of $1.20 round turn commission and 0.5 tick modeled "
            "slippage · Jun 2021–Jun 2026."
        )
        st.altair_chart(equity_curve(monthly))
with year_col:
    with st.container(
        border=True,
        height="stretch",
        key="brief_year_chart",
        gap="xxsmall",
    ):
        st.subheader("Calendar year outcomes")
        st.caption(
            f"Complete years: {positive_complete_years}/{len(complete_years)} positive. "
            "2021 and 2026 are partial edge periods."
        )
        st.altair_chart(annual_pnl(yearly))

render_section_header(
    "How I’m testing the idea",
    "The rule set stays intentionally small so each assumption can be challenged directly.",
    key="strategy_sequence",
)
market_col, signal_col, risk_col = st.columns(3, gap="small")
with market_col:
    with st.container(border=True, height="stretch", gap="xxsmall"):
        st.caption("01 / REFERENCE")
        st.subheader("Define the morning range")
        st.write("Use only the 09:30–10:00 ET session high and low.")
with signal_col:
    with st.container(border=True, height="stretch", gap="xxsmall"):
        st.caption("02 / ENTRY")
        st.subheader("Wait for confirmation")
        st.write("Enter only after a completed bar break, with one decision per session.")
with risk_col:
    with st.container(border=True, height="stretch", gap="xxsmall"):
        st.caption("03 / EXECUTION")
        st.subheader("Model friction explicitly")
        st.write("Apply a 1R stop, 1R target, commission, and 0.5 tick slippage.")

evidence_register = pd.DataFrame(
    [
        {
            "Review": "Lookahead and prior input audit",
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
            "Review": "Before 2021 and broader data provider coverage",
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
    st.subheader("What has and has not been established")
    st.caption("The reviewed support and unresolved limits I use to govern the next step.")
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
        "Built as an AI assisted passion project: I set the research question, modeling "
        "choices, and publication standards; AI accelerated coding, documentation, and "
        "interface iteration. Every public claim remains tied to reviewed aggregate evidence. "
        "Historical research only. This is not a trading recommendation or signal service. "
        f"Snapshot digest: `{snapshot_sha256()}`"
    )
