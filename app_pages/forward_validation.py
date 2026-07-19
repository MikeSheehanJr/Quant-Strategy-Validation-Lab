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

render_page_header(
    "Prospective research protocol",
    "Forward validation",
    "A small, version-locked paper-validation track for the current Pine companion build. "
    "This page reports the evidence state before it reports performance.",
)

with st.container(border=True, key="forward_status", gap="xsmall"):
    st.subheader(":material/schedule: Forward collection has not started")
    st.write(
        "There are no public forward observations and no forward-performance conclusion."
    )

with st.container(horizontal=True, gap="small"):
    st.metric("Candidate", candidate["version"], border=True)
    st.metric("Public observations", f"{evidence['public_observation_count']}", border=True)
    st.metric("Complete months", f"{evidence['complete_months']}", border=True)

protocol_contract = pd.DataFrame(
    [
        {"Control": "Candidate track", "Commitment": candidate["track"]},
        {
            "Control": "Frozen source",
            "Commitment": f"{candidate['version']} · {candidate['freeze_date']}",
        },
        {"Control": "Source SHA-256", "Commitment": candidate["source_sha256"]},
        {"Control": "Publication cadence", "Commitment": reporting["cadence"]},
        {"Control": "Minimum delay", "Commitment": reporting["minimum_delay"]},
        {"Control": "Published grain", "Commitment": reporting["granularity"]},
        {"Control": "Live signals / trade records", "Commitment": "Excluded"},
    ]
)
with st.container(border=True, key="forward_contract"):
    st.subheader("Forward-test contract")
    st.caption("Version lock and public boundary shown as one auditable specification.")
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
    "The frozen build, private reconciliation, and delayed aggregate publication form one chain.",
    key="forward_protocol",
)
protocol_col, correction_col, report_col = st.columns(3, gap="small")
with protocol_col:
    with st.container(border=True, height="stretch", gap="xxsmall"):
        st.caption("01 / FREEZE")
        st.subheader("Hash before observation")
        st.write("Rule changes create a new version.")
with correction_col:
    with st.container(border=True, height="stretch", gap="xxsmall"):
        st.caption("02 / RECONCILE")
        st.subheader("Resolve tracking errors")
        st.write("Missed, late, duplicate, and corrected records stay private.")
with report_col:
    with st.container(border=True, height="stretch", gap="xxsmall"):
        st.caption("03 / PUBLISH")
        st.subheader("Closed months only")
        st.write("Aggregate risk units after the minimum delay.")

schema = pd.DataFrame(
    [
        {"Field": "month", "Purpose": "Closed calendar month covered by the record"},
        {"Field": "eligible_sessions", "Purpose": "Sessions that passed the frozen rules"},
        {"Field": "resolved_observations", "Purpose": "Paper observations fully reconciled"},
        {"Field": "net_pnl_r", "Purpose": "Aggregate outcome in risk units, not dollars"},
        {"Field": "max_drawdown_r", "Purpose": "Aggregate forward drawdown in risk units"},
        {"Field": "tracking_errors", "Purpose": "Missed, duplicate, or unreconciled events"},
        {"Field": "status", "Purpose": "Complete, corrected, or withheld with reason"},
    ]
)
with st.container(border=True, key="forward_schema"):
    st.subheader("Planned monthly public record")
    st.caption(
        "This is the intended aggregate schema—not observed data. No performance row is "
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

with st.container(border=True):
    st.subheader("Next required gate")
    st.badge("Protocol only", icon=":material/lock:", color="gray")
    st.write(status["next_gate"])
    st.caption("No chart is shown because no forward observations exist.")
