"""Versioned Pine Script implementation and aggregate export evidence."""

from __future__ import annotations

from pathlib import Path

import streamlit as st

from src.charts import pinescript_equity_curve
from src.data import load_snapshot
from src.pinescript import (
    BACKTEST_FILES,
    evidence_bytes,
    load_pinescript_backtests,
    load_pinescript_manifest,
    pinescript_excerpt,
    pinescript_source,
    pinescript_versions_frame,
)
from src.ui import render_page_header, render_research_boundary


snapshot = load_snapshot()
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
    "Inspect how the companion TradingView implementation changed from a research baseline "
    "to a symbol-locked paper-control build.",
)
render_research_boundary(snapshot["meta"])

st.info(
    "This is a related **15-minute symmetric ORB implementation track**, not the exact "
    "30-minute filtered Python engine behind the 729-trade headline snapshot. The code, "
    "hashes, and TradingView aggregates below are kept separate from the headline metrics.",
    icon=":material/info:",
)

with st.container(horizontal=True):
    st.metric("Versioned source files", f"{len(pine_versions)}", border=True)
    st.metric("Current build", current_version["version"], border=True)
    st.metric("Reviewed MNQ trades", f"{int(full_export['trades']):,}", border=True)
    st.metric("Structural QA checks", f"{len(pine_qa)}/{len(pine_qa)}", border=True)

with st.container(border=True):
    st.subheader("What the script does")
    process_col, controls_col = st.columns(2, gap="large")
    with process_col:
        st.markdown("**Signal and exit sequence**")
        st.markdown(
            "1. Build the 09:30–10:00 ET opening range on a 15-minute chart.\n"
            "2. Accept the first completed close beyond either boundary.\n"
            "3. Lock the session after the first decision, including a risk skip.\n"
            "4. Place the stop at the opposite range boundary and target 1R.\n"
            "5. Flatten at the normal or registered early session close."
        )
    with controls_col:
        st.markdown("**Engineering controls**")
        st.markdown(
            "- Bar-close decisions and `lookahead_off`-compatible state logic\n"
            "- Dollar-risk sizing with a hard contract cap\n"
            "- MNQ symbol and 15-minute timeframe lock in v4.1\n"
            "- User-maintained early-close calendar\n"
            "- Observation-only alerts; no broker or execution connection"
        )

st.subheader("Version-by-version research ledger")
st.caption(
    "Historical source headers are preserved as research records. Later corrections and the "
    "manifest status take precedence over superseded estimates in older comments."
)
st.dataframe(
    pinescript_versions_frame(pine_manifest),
    hide_index=True,
    column_config={
        "version": st.column_config.TextColumn("Version", pinned=True),
        "research_date": st.column_config.DateColumn("Research date", format="MMM DD, YYYY"),
        "title": st.column_config.TextColumn("Build"),
        "change": st.column_config.TextColumn("Primary change", width="large"),
        "evidence_status": st.column_config.TextColumn("Evidence state", width="large"),
    },
)

selected_version_id = st.selectbox(
    "Inspect a version",
    [version["version"] for version in pine_versions],
    index=len(pine_versions) - 1,
    key="pinescript_version",
)
selected_version = next(
    version for version in pine_versions if version["version"] == selected_version_id
)
detail_col, rationale_col = st.columns(2, gap="large")
with detail_col:
    with st.container(border=True):
        st.markdown(f"**{selected_version['version']} · {selected_version['title']}**")
        st.write(selected_version["change"])
        st.caption(f"Evidence: {selected_version['evidence_status']}")
        st.caption(
            f"{selected_version['line_count']:,} lines · SHA-256 "
            f"`{selected_version['sha256'][:16]}…`"
        )
with rationale_col:
    with st.container(border=True):
        st.markdown("**Research rationale**")
        st.write(selected_version["why"])
        st.markdown("**Known limitation**")
        st.write(selected_version["known_limitations"])

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

st.subheader("Reviewed v4.1 MNQ backtest evidence")
st.caption(
    "Aggregate derivatives of the July 16, 2026 TradingView List of Trades export. The "
    "source trade list is hash-pinned but not published; timestamps, prices, quantities, "
    "and individual outcomes remain outside the public boundary."
)
with st.container(horizontal=True):
    st.metric("Full-export net P&L", f"${full_export['net_pnl_usd']:,.0f}", border=True)
    st.metric("Full-export profit factor", f"{full_export['profit_factor']:.3f}", border=True)
    st.metric("Full-export max drawdown", f"${full_export['max_drawdown_usd']:,.0f}", border=True)
    st.metric("2026 YTD net P&L", f"${ytd_2026['net_pnl_usd']:,.0f}", border=True)

with st.container(border=True):
    st.subheader("TradingView aggregate path")
    st.caption(
        "Monthly sums from 1,269 completed v4.1 MNQ trades using dynamic sizing and the "
        "reviewed TradingView fee configuration. This is not the one-contract headline series."
    )
    st.altair_chart(pinescript_equity_curve(pine_monthly))

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
        "max_drawdown_usd": st.column_config.NumberColumn("Max drawdown", format="$%.2f"),
    },
)
st.caption(
    "The negative 2026 YTD row is intentionally retained. Last-250 and date-window rows are "
    "descriptive diagnostics, not independent out-of-sample tests."
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

st.markdown("**Download aggregate evidence**")
with st.container(horizontal=True):
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

next_col, boundary_col = st.columns(2, gap="large")
with next_col:
    with st.container(border=True):
        st.subheader("Open acceptance checks")
        st.markdown(
            "1. Verify the wrong-symbol lock on a non-MNQ chart.\n"
            "2. Inspect one normal-session replay for markers and fixed TP/SL segments.\n"
            "3. Replay a known half-day in the split v4.1 script.\n"
            "4. Confirm one observation-only alert per eligible signal.\n"
            "5. Register the forward-test decision rule before collection begins."
        )
with boundary_col:
    with st.container(border=True):
        st.subheader("What remains private")
        st.markdown(
            "- Licensed intraday OHLCV bars\n"
            "- Full TradingView trade-list exports\n"
            "- Exact signal timestamps, prices, and quantities\n"
            "- Broker, account, and execution data\n"
            "- Credentials or automation connections"
        )
        st.caption(
            "This is evidence and code-review material—not a signal service or execution interface."
        )
