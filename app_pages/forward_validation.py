"""Claim-limited forward-validation protocol and current evidence state."""

from __future__ import annotations

import pandas as pd
import streamlit as st

from src.data import load_snapshot
from src.forward import load_forward_status
from src.ui import render_page_header, render_research_boundary


snapshot = load_snapshot()
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
render_research_boundary(snapshot["meta"])

st.warning(
    "Forward collection has not started. There are no public forward observations and no "
    "forward-performance conclusion.",
    icon=":material/schedule:",
)

with st.container(horizontal=True):
    st.metric("Candidate", candidate["version"], border=True)
    st.metric("Public observations", f"{evidence['public_observation_count']}", border=True)
    st.metric("Complete months", f"{evidence['complete_months']}", border=True)
    st.metric("Evidence state", "Not started", border=True)

lock_col, boundary_col = st.columns([1.2, 1], gap="large")
with lock_col:
    with st.container(border=True):
        st.subheader("Version lock")
        st.markdown(f"**Track:** {candidate['track']}")
        st.markdown(f"**Frozen build:** {candidate['version']} · {candidate['freeze_date']}")
        st.markdown(f"**Source SHA-256:** `{candidate['source_sha256']}`")
        st.caption(candidate["relationship_to_headline"])
with boundary_col:
    with st.container(border=True):
        st.subheader("Public boundary")
        st.markdown(
            f"- Reporting cadence: **{reporting['cadence']}**\n"
            f"- Publication delay: **{reporting['minimum_delay']}**\n"
            f"- Published grain: **{reporting['granularity']}**\n"
            "- Live signals: **excluded**\n"
            "- Trade-level records: **excluded**"
        )

st.subheader("Protocol")
protocol_col, correction_col, report_col = st.columns(3, gap="large")
with protocol_col:
    with st.container(border=True, height="stretch"):
        st.markdown("**1 · Freeze before observing**")
        st.write(
            "The candidate source and hash are fixed. A rule change creates a new version; "
            "it does not rewrite the current record."
        )
with correction_col:
    with st.container(border=True, height="stretch"):
        st.markdown("**2 · Reconcile privately**")
        st.write(
            "Observation-only alerts, missed events, late records, and corrections are logged "
            "before any public aggregate is produced."
        )
with report_col:
    with st.container(border=True, height="stretch"):
        st.markdown("**3 · Publish after the period**")
        st.write(
            "Only completed monthly aggregates are published. Exact signals, timestamps, "
            "prices, quantities, and broker information remain private."
        )

st.subheader("Planned monthly public record")
st.caption(
    "This is the intended aggregate schema—not observed data. No performance row is created "
    "until a complete month has been reconciled."
)
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
    st.write(status["next_gate"])
    st.caption(
        "Until that gate is committed, this page is protocol-only and must not be cited as "
        "forward evidence. No chart is shown because there are no observations to plot."
    )
