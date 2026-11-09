"""Claim-limited forward-validation protocol and current evidence state."""

from __future__ import annotations

import pandas as pd
import streamlit as st

from src.forward import load_forward_status
from src.ui import render_page_header, render_section_header


status = load_forward_status()
candidate = status["candidate"]
reporting = status["public_reporting"]
evidence = status["evidence"]
protocol = status["protocol"]
acceptance = status["acceptance"]

render_page_header(
    "Prospective research protocol",
    "Forward validation",
    "A prospective paper protocol for the MNQ Pine companion. The proposed candidate "
    "has not passed the collection gates, and no forward results exist yet.",
)

with st.container(border=True, key="forward_status", gap="xsmall"):
    state_labels = {
        "not_ready": "Not ready for collection", "ready": "Ready for collection",
        "collecting": "Collecting paper observations", "under_review": "First review due",
        "inconclusive": "Review inconclusive", "completed": "Review completed",
    }
    st.subheader(f":material/schedule: {state_labels[status['status']]}")
    st.write(evidence["conclusion"])
    if status["status"] == "not_ready":
        st.caption("Calendar verification, settings freeze, start date, and interactive TradingView acceptance remain pending.")

with st.container(horizontal=True, gap="small"):
    st.metric("Candidate", candidate["version"], border=True)
    st.metric("Forward observations", f"{evidence['public_observation_count']}", border=True)
    st.metric("Complete months", f"{evidence['complete_months']}", border=True)
    st.metric("Resolved trades", f"{evidence['resolved_trades']}", border=True)

protocol_contract = pd.DataFrame(
    [
        {"Control": "Candidate track", "Commitment": candidate["track"]},
        {
            "Control": "Frozen source",
            "Commitment": f"{candidate['version']} · source SHA-256 {candidate['source_sha256'][:12]}…",
        },
        {"Control": "Settings freeze", "Commitment": candidate["freeze_date"] or "Pending"},
        {"Control": "Calendar source and hash", "Commitment": "Verified" if candidate["calendar"]["sha256"] else "Pending"},
        {"Control": "Collection start", "Commitment": candidate["collection_start"] or "Pending"},
        {"Control": "First review", "Commitment": "3 complete months and 60 resolved trades; zero unresolved opportunities"},
        {"Control": "Reporting cadence", "Commitment": reporting["cadence"]},
        {"Control": "Minimum delay", "Commitment": reporting["minimum_delay"]},
        {"Control": "Reported grain", "Commitment": reporting["granularity"]},
        {"Control": "Live signals / trade records", "Commitment": "Excluded"},
    ]
)
with st.container(border=True, key="forward_contract"):
    st.subheader("Forward test contract")
    st.caption(f"Protocol {protocol['version']} registered {protocol['registered_at']}; hash {protocol['sha256'][:12]}…")
    st.dataframe(
        protocol_contract,
        hide_index=True,
        column_config={
            "Control": st.column_config.TextColumn("Control", pinned=True, width="medium"),
            "Commitment": st.column_config.TextColumn("Commitment", width="large"),
        },
    )

render_section_header(
    "Protocol",
    "The fixed build, private reconciliation, and delayed aggregate reporting form one chain.",
    key="forward_protocol",
)
protocol_col, correction_col, report_col = st.columns(3, gap="small")
with protocol_col:
    with st.container(border=True, height="stretch", gap="xxsmall"):
        st.caption("01 / FREEZE")
        st.subheader("Freeze rules before observation")
        st.write("A new candidate and protocol record are required for any rule change.")
with correction_col:
    with st.container(border=True, height="stretch", gap="xxsmall"):
        st.caption("02 / RECONCILE")
        st.subheader("Resolve tracking errors")
        st.write("Every opportunity is accounted for. Corrections and negative results remain in revision history.")
with report_col:
    with st.container(border=True, height="stretch", gap="xxsmall"):
        st.caption("03 / REPORT")
        st.subheader("Closed months only")
        st.write("Publish closed calendar months only, in aggregate risk units.")

schema = pd.DataFrame(
    [
        {"Field": "month", "Purpose": "Closed calendar month covered by the record"},
        {"Field": "eligible_sessions", "Purpose": "Sessions that passed the frozen rules"},
        {"Field": "resolved_trades", "Purpose": "Paper trades fully reconciled"},
        {"Field": "opportunities_detected", "Purpose": "All opportunities, including no-trade and unresolved decisions"},
        {"Field": "negative_trades", "Purpose": "Losing paper outcomes retained"},
        {"Field": "net_pnl_r", "Purpose": "Aggregate outcome in risk units, not dollars"},
        {"Field": "within_month_max_drawdown_r", "Purpose": "Within-month drawdown magnitude in risk units"},
        {"Field": "revision", "Purpose": "Original and corrected versions retained"},
    ]
)
with st.container(border=True, key="forward_schema"):
    st.subheader("Planned monthly research record")
    st.caption(
        "This is the intended aggregate schema, not observed data. No performance row is "
        "created until a complete month has been reconciled."
    )
    st.dataframe(
        schema,
        hide_index=True,
        column_config={
            "Field": st.column_config.TextColumn("Field", pinned=True),
            "Purpose": st.column_config.TextColumn("Purpose", width="large"),
        },
    )

with st.container(border=True, key="forward_acceptance"):
    st.subheader("TradingView acceptance")
    st.caption("Each case needs an actual observed pass and evidence reference before collection can begin.")
    st.dataframe(pd.DataFrame(acceptance["cases"])[["id", "status"]], hide_index=True)

if evidence["monthly_records"] and evidence["public_observation_count"] > 0:
    with st.container(border=True, key="forward_monthly"):
        st.subheader("Published closed-month aggregates")
        st.caption("All revisions are shown, including corrections and negative outcomes.")
        st.dataframe(pd.DataFrame(evidence["monthly_records"]), hide_index=True)

with st.container(border=True):
    st.subheader("Next required gate")
    st.badge("Prospective protocol", icon=":material/lock:", color="gray")
    st.write(status["next_gate"])
    st.caption("No chart is shown because no forward observations exist.")
