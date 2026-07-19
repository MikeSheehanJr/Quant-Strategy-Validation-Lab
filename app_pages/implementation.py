"""Versioned Pine Script implementation and aggregate export evidence."""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import streamlit as st

from src.charts import pinescript_equity_curve
from src.pinescript import (
    BACKTEST_FILES,
    evidence_bytes,
    load_pinescript_backtests,
    load_pinescript_manifest,
    pinescript_excerpt,
    pinescript_source,
    pinescript_versions_frame,
)
from src.ui import render_page_header


pine_manifest = load_pinescript_manifest()
pine_backtests = load_pinescript_backtests()
pine_monthly = pine_backtests["monthly"]
pine_windows = pine_backtests["windows"]
pine_qa = pine_backtests["qa"]
pine_versions = pine_manifest["versions"]
current_version = next(version for version in pine_versions if version["current"])
full_export = pine_windows.loc[pine_windows["window"] == "Full export"].iloc[0]
ytd_2026 = pine_windows.loc[pine_windows["window"] == "2026 YTD"].iloc[0]

render_page_header(
    "Versioned implementation evidence",
    "Pine Script implementation",
    "I keep the TradingView companion separate from the headline Python engine so I can "
    "review its rule changes, safeguards, and evidence trail on their own terms.",
)

lineage = pd.DataFrame(
    [
        {
            "Track": "Pine companion",
            "Specification": "15-minute symmetric ORB",
            "Evidence role": "Implementation and TradingView traceability",
        },
        {
            "Track": "Headline Python engine",
            "Specification": "30-minute filtered ORB",
            "Evidence role": "729-trade reviewed research snapshot",
        },
    ]
)
with st.container(border=True, key="implementation_lineage"):
    st.subheader("Research lineage")
    st.badge("Separate evidence tracks", icon=":material/call_split:", color="blue")
    st.dataframe(
        lineage,
        hide_index=True,
        column_config={
            "Track": st.column_config.TextColumn("Track", pinned=True),
            "Specification": st.column_config.TextColumn("Frozen specification"),
            "Evidence role": st.column_config.TextColumn("Evidence role", width="large"),
        },
    )

with st.container(horizontal=True, gap="small"):
    st.metric("Versioned source files", f"{len(pine_versions)}", border=True)
    st.metric("Current build", current_version["version"], border=True)
    st.metric("Reviewed MNQ trades", f"{int(full_export['trades']):,}", border=True)
    st.metric("Structural QA checks", f"{len(pine_qa)}/{len(pine_qa)}", border=True)

script_flow = pd.DataFrame(
    [
        {
            "Stage": "Range",
            "Decision rule": "09:30–10:00 ET high / low",
            "Guardrail": "MNQ · 15-minute lock",
        },
        {
            "Stage": "Trigger",
            "Decision rule": "First completed close beyond range",
            "Guardrail": "Bar-close state logic",
        },
        {
            "Stage": "Risk",
            "Decision rule": "Opposite boundary stop · 1R target",
            "Guardrail": "Dollar cap + contract cap",
        },
        {
            "Stage": "Session",
            "Decision rule": "One decision, including risk skip",
            "Guardrail": "Normal and early-close flattening",
        },
        {
            "Stage": "Alert",
            "Decision rule": "Observation-only event",
            "Guardrail": "No broker connection",
        },
    ]
)
with st.container(border=True, key="script_flow"):
    st.subheader("Execution state machine")
    st.caption("Five stages connect the research rule to explicit engineering controls.")
    st.dataframe(
        script_flow,
        hide_index=True,
        column_config={
            "Stage": st.column_config.TextColumn("Stage", pinned=True, width="small"),
            "Decision rule": st.column_config.TextColumn("Decision rule", width="large"),
            "Guardrail": st.column_config.TextColumn("Engineering guardrail", width="large"),
        },
    )

with st.container(border=True, key="version_ledger"):
    st.subheader("Version-by-version research ledger")
    st.caption(
        "Historical source headers are preserved as research records. Later corrections and "
        "the manifest status take precedence over superseded estimates in older comments."
    )
    st.dataframe(
        pinescript_versions_frame(pine_manifest),
        hide_index=True,
        column_config={
            "version": st.column_config.TextColumn("Version", pinned=True),
            "research_date": st.column_config.DateColumn(
                "Research date", format="MMM DD, YYYY"
            ),
            "title": st.column_config.TextColumn("Build"),
            "change": st.column_config.TextColumn("Primary change", width="large"),
            "evidence_status": st.column_config.TextColumn("Evidence state", width="large"),
        },
    )

with st.container(border=True, key="version_picker"):
    selected_version_id = st.selectbox(
        "Inspect a version",
        [version["version"] for version in pine_versions],
        index=len(pine_versions) - 1,
        key="pinescript_version",
    )
selected_version = next(
    version for version in pine_versions if version["version"] == selected_version_id
)
version_review = pd.DataFrame(
    [
        {"Field": "Build", "Review record": selected_version["title"]},
        {"Field": "Primary change", "Review record": selected_version["change"]},
        {"Field": "Research rationale", "Review record": selected_version["why"]},
        {"Field": "Known limitation", "Review record": selected_version["known_limitations"]},
        {"Field": "Evidence state", "Review record": selected_version["evidence_status"]},
        {
            "Field": "Source identity",
            "Review record": (
                f"{selected_version['line_count']:,} lines · SHA-256 "
                f"{selected_version['sha256'][:16]}…"
            ),
        },
    ]
)
with st.container(border=True, key="version_review"):
    st.subheader(f"{selected_version['version']} review record")
    st.dataframe(
        version_review,
        hide_index=True,
        column_config={
            "Field": st.column_config.TextColumn("Field", pinned=True, width="small"),
            "Review record": st.column_config.TextColumn("Review record", width="large"),
        },
    )

with st.expander("Representative source and download", icon=":material/code:"):
    st.code(pinescript_excerpt(selected_version), language="javascript", line_numbers=True)
    st.download_button(
        f"Download {selected_version['version']} source",
        data=pinescript_source(selected_version),
        file_name=Path(selected_version["file"]).name,
        mime="text/plain",
        key=f"download_{selected_version['version']}",
        icon=":material/download:",
        on_click="ignore",
    )

with st.container(border=True, key="pine_evidence_summary"):
    st.subheader("Reviewed v4.1 MNQ backtest evidence")
    st.caption(
        "These aggregates derive from the July 16, 2026 TradingView List of Trades export. "
        "The source trade list is hash-pinned but not published; timestamps, prices, "
        "quantities, and individual outcomes remain outside the release boundary."
    )
    with st.container(horizontal=True, gap="small"):
        st.metric("Full-export net P&L", f"${full_export['net_pnl_usd']:,.0f}", border=True)
        st.metric(
            "Full-export profit factor", f"{full_export['profit_factor']:.3f}", border=True
        )
        st.metric(
            "Full-export max drawdown",
            f"${full_export['max_drawdown_usd']:,.0f}",
            border=True,
        )
        st.metric("2026 YTD net P&L", f"${ytd_2026['net_pnl_usd']:,.0f}", border=True)

with st.container(border=True):
    st.subheader("TradingView aggregate path")
    st.caption(
        "Monthly sums from 1,269 completed v4.1 MNQ trades using dynamic sizing and the "
        "reviewed TradingView fee configuration. I report this separately from the "
        "one-contract headline series."
    )
    st.altair_chart(pinescript_equity_curve(pine_monthly))

with st.container(border=True, key="backtest_windows"):
    st.subheader("Backtest windows")
    st.dataframe(
        pine_windows,
        hide_index=True,
        column_config={
            "window": st.column_config.TextColumn("Window", pinned=True),
            "start_month": st.column_config.TextColumn("Start"),
            "end_month": st.column_config.TextColumn("End"),
            "trades": st.column_config.NumberColumn("Trades", format="%d"),
            "net_pnl_usd": st.column_config.NumberColumn("Net P&L", format="$%.2f"),
            "mean_trade_usd": st.column_config.NumberColumn("Mean/trade", format="$%.2f"),
            "win_rate_pct": st.column_config.NumberColumn("Win rate", format="%.2f%%"),
            "profit_factor": st.column_config.NumberColumn("Profit factor", format="%.3f"),
            "max_drawdown_usd": st.column_config.NumberColumn(
                "Max drawdown", format="$%.2f"
            ),
        },
    )
    st.caption(
        "The negative 2026 YTD row is intentionally retained. The last-250 and date-window "
        "rows are descriptive diagnostics, not independent out-of-sample tests."
    )

with st.expander("Export QA and provenance", icon=":material/fact_check:"):
    st.dataframe(
        pine_qa,
        hide_index=True,
        column_config={
            "check": st.column_config.TextColumn("Check", pinned=True),
            "status": st.column_config.TextColumn("Status"),
            "value": st.column_config.TextColumn("Observed value"),
            "interpretation": st.column_config.TextColumn("Interpretation", width="large"),
        },
    )

with st.container(border=True, key="aggregate_downloads"):
    st.subheader("Download aggregate evidence")
    with st.container(horizontal=True, gap="small"):
        for key, label in (
            ("monthly", "Monthly backtest CSV"),
            ("windows", "Window summary CSV"),
            ("qa", "QA and provenance CSV"),
        ):
            st.download_button(
                label,
                data=evidence_bytes(key),
                file_name=BACKTEST_FILES[key].name,
                mime="text/csv",
                key=f"download_pine_{key}",
                icon=":material/download:",
                on_click="ignore",
            )

review_boundary = pd.DataFrame(
    [
        {
            "Area": "Acceptance",
            "Item": "Wrong-symbol and timeframe lock",
            "State": ":gray-badge[Open]",
        },
        {
            "Area": "Acceptance",
            "Item": "Normal-session replay and fixed TP / SL markers",
            "State": ":gray-badge[Open]",
        },
        {
            "Area": "Acceptance",
            "Item": "Registered half-day replay",
            "State": ":gray-badge[Open]",
        },
        {
            "Area": "Acceptance",
            "Item": "One observation alert per eligible signal",
            "State": ":gray-badge[Open]",
        },
        {
            "Area": "Acceptance",
            "Item": "Forward decision rule registered before collection",
            "State": ":gray-badge[Open]",
        },
        {
            "Area": "Release boundary",
            "Item": "Licensed intraday bars and full trade exports",
            "State": ":blue-badge[Private]",
        },
        {
            "Area": "Release boundary",
            "Item": "Signal timestamps, prices, and quantities",
            "State": ":blue-badge[Private]",
        },
        {
            "Area": "Release boundary",
            "Item": "Broker, account, execution, and credentials",
            "State": ":blue-badge[Excluded]",
        },
    ]
)
with st.container(border=True, key="implementation_review_boundary"):
    st.subheader("Acceptance and release boundary")
    st.caption("I keep open engineering checks visible beside deliberately excluded data.")
    st.dataframe(
        review_boundary,
        hide_index=True,
        column_config={
            "Area": st.column_config.TextColumn("Area", pinned=True, width="small"),
            "Item": st.column_config.TextColumn("Control or boundary", width="large"),
            "State": st.column_config.MarkdownColumn("State", width="small"),
        },
    )
