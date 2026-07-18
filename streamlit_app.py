"""Quant strategy validation lab — public work-in-progress dashboard."""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import streamlit as st

from src.charts import (
    annual_pnl,
    cutoff_sensitivity_chart,
    drawdown_distribution,
    equity_curve,
    execution_heatmap,
    gate_sensitivity_chart,
    monthly_pnl_distribution,
    monte_carlo_fan,
    parameter_surface_heatmap,
    pinescript_equity_curve,
    rr_sensitivity,
    terminal_distribution,
)
from src.data import (
    entry_cutoff_frame,
    execution_frame,
    gate_frame,
    load_snapshot,
    monthly_frame,
    parameter_surface_frame,
    rr_frame,
    snapshot_sha256,
    yearly_frame,
)
from src.metrics import (
    execution_range,
    max_drawdown_from_monthly,
    profitable_year_count,
    quant_summary,
)
from src.pinescript import (
    BACKTEST_FILES,
    evidence_bytes,
    load_pinescript_backtests,
    load_pinescript_manifest,
    pinescript_excerpt,
    pinescript_source,
    pinescript_versions_frame,
)
from src.simulations import monthly_block_bootstrap


st.set_page_config(
    page_title="Quant strategy validation lab",
    page_icon=":material/query_stats:",
    layout="wide",
    initial_sidebar_state="auto",
)


@st.cache_data(show_spinner=False)
def get_dashboard_data() -> tuple[
    dict,
    pd.DataFrame,
    pd.DataFrame,
    pd.DataFrame,
    pd.DataFrame,
    pd.DataFrame,
    pd.DataFrame,
]:
    snapshot = load_snapshot()
    return (
        snapshot,
        monthly_frame(snapshot),
        yearly_frame(snapshot),
        execution_frame(snapshot),
        rr_frame(snapshot),
        gate_frame(snapshot),
        entry_cutoff_frame(snapshot),
    )


@st.cache_data(show_spinner=False, max_entries=24)
def run_public_monte_carlo(
    monthly: pd.DataFrame,
    horizon_months: int,
    paths: int,
    block_months: int,
):
    return monthly_block_bootstrap(
        monthly,
        horizon_months=horizon_months,
        paths=paths,
        block_months=block_months,
        seed=2026,
    )


snapshot, monthly, yearly, execution, rr, gates, cutoffs = get_dashboard_data()
headline = snapshot["headline"]
meta = snapshot["meta"]

with st.sidebar:
    st.markdown("### Research navigation")
    view = st.radio(
        "Research view",
        [
            "Overview",
            "Monte Carlo",
            "Parameter lab",
            "Validation",
            "Pine Script",
            "Build log",
        ],
    )
    st.markdown(":blue-badge[Work in progress]")
    st.caption(
        "Public portfolio build. Historical research only—not live signals or investment advice."
    )
    with st.container(border=True):
        st.markdown("**Current research boundary**")
        st.caption(f"Instrument: {meta['instrument']}")
        st.caption(f"Sample: {meta['research_window']}")
        st.caption(f"Snapshot: {meta['snapshot_date']}")
        st.caption("Raw market data: excluded")
    st.caption(f"Snapshot digest: `{snapshot_sha256()}`")

st.caption("PUBLIC QUANT RESEARCH · PORTFOLIO BUILD")
with st.container(
    horizontal=True,
    horizontal_alignment="distribute",
    vertical_alignment="center",
):
    st.title("Quant strategy validation lab")
    st.badge("Work in progress", icon=":material/construction:", color="blue")

st.markdown(
    "**Research question:** Can a deliberately simple intraday strategy survive costs, "
    "out-of-sample testing, parameter perturbation, and adversarial review?"
)
st.caption(
    "The project is designed to reject fragile results. It demonstrates quantitative research and Python engineering—not a trading recommendation."
)


if view == "Overview":
    profitable, periods = profitable_year_count(yearly)
    max_monthly_dd = max_drawdown_from_monthly(monthly)
    risk = quant_summary(monthly)

    with st.container(horizontal=True):
        st.metric("Cost-adjusted trades", f"{headline['trade_count']:,}", border=True)
        st.metric("Win rate", f"{headline['win_rate_pct']:.1f}%", border=True)
        st.metric("Profit factor", f"{headline['profit_factor']:.3f}", border=True)
        st.metric("Calendar-honest Sharpe", f"{headline['daily_sharpe']:.2f}", border=True)

    with st.container(border=True):
        st.subheader("Strategy background")
        st.markdown(
            "The case study is a rules-based opening-range breakout on the Micro E-mini "
            "Nasdaq-100 futures contract (MNQ). It tests whether expansion beyond the "
            "regular-session opening range remains positive after realistic implementation "
            "costs and adversarial validation."
        )
        market_col, signal_col, risk_col = st.columns(3, gap="large")
        with market_col:
            st.markdown("**Market context**")
            st.write(
                "The first 30 minutes of the regular session define the reference high and low."
            )
        with signal_col:
            st.markdown("**Entry logic**")
            st.write(
                "A completed bar must close beyond the range. Strictly prior filters determine "
                "eligibility, with at most one trade per session."
            )
        with risk_col:
            st.markdown("**Risk and execution**")
            st.write(
                "The frozen design uses a symmetric 1:1 stop and target, explicit commission, "
                "modeled slippage, and stress tests under worse fills."
            )
        st.caption(
            "Why this case study: the strategy is simple, interpretable, and low-dimensional, "
            "which makes it useful for demonstrating bias control and robustness without a "
            "black-box model. Historical research only—not a live signal."
        )

    left, right = st.columns([1.65, 1], gap="large")
    with left:
        with st.container(border=True):
            st.subheader("Cumulative research P&L")
            st.caption(
                "Monthly aggregates, one MNQ contract, after $1.20 round-turn commission and 0.5-tick modeled slippage."
            )
            st.altair_chart(equity_curve(monthly))
    with right:
        with st.container(border=True):
            st.subheader("Calendar-year outcomes")
            st.caption("2021 begins in June; 2026 ends in June and is explicitly marked partial.")
            st.altair_chart(annual_pnl(yearly))

    st.subheader("Quant risk snapshot")
    st.caption(
        f"Dollar-based diagnostics across {risk['sample_months']} complete months; partial edge months are excluded."
    )
    with st.container(horizontal=True):
        st.metric(
            "Positive complete months",
            f"{risk['positive_month_rate_pct']:.1f}%",
            border=True,
        )
        st.metric(
            "Annualized P&L",
            f"${risk['annualized_pnl_usd']:,.0f}",
            border=True,
        )
        st.metric(
            "Annualized P&L volatility",
            f"${risk['annualized_volatility_usd']:,.0f}",
            border=True,
        )
        st.metric("Monthly Sortino", f"{risk['monthly_sortino']:.2f}", border=True)

    distribution_col, tail_col = st.columns([1.45, 1], gap="large")
    with distribution_col:
        with st.container(border=True):
            st.subheader("Complete-month P&L distribution")
            st.caption("Histogram of 59 complete monthly aggregates; the vertical rule marks zero.")
            st.altair_chart(monthly_pnl_distribution(monthly))
    with tail_col:
        with st.container(border=True):
            st.subheader("Tail and path diagnostics")
            diagnostics = pd.DataFrame(
                [
                    {"Metric": "Historical monthly VaR (95%)", "Value": f"${risk['historical_var_95_usd']:,.0f}"},
                    {"Metric": "Historical monthly CVaR (95%)", "Value": f"${risk['historical_cvar_95_usd']:,.0f}"},
                    {"Metric": "Monthly skewness", "Value": f"{risk['skewness']:.2f}"},
                    {"Metric": "Excess kurtosis", "Value": f"{risk['excess_kurtosis']:.2f}"},
                    {"Metric": "Aggregate max drawdown", "Value": f"${risk['max_drawdown_usd']:,.0f}"},
                    {"Metric": "Longest aggregate recovery", "Value": f"{risk['max_drawdown_duration_months']} months"},
                    {"Metric": "Recovery factor", "Value": f"{risk['recovery_factor']:.2f}×"},
                ]
            )
            st.dataframe(
                diagnostics,
                hide_index=True,
                column_config={
                    "Metric": st.column_config.TextColumn("Metric", pinned=True),
                    "Value": st.column_config.TextColumn("Value"),
                },
            )

    with st.container(horizontal=True):
        st.metric("Positive calendar periods", f"{profitable}/{periods}", border=True)
        st.metric("Monthly-aggregate max drawdown", f"${max_monthly_dd:,.0f}", border=True)
        st.metric("CPCV OOS-positive splits", "45/45", border=True)
        st.metric("PSR vs zero", "3.30σ", border=True)

    st.subheader("What this result does—and does not—show")
    explain_left, explain_right = st.columns(2, gap="large")
    with explain_left:
        with st.container(border=True):
            st.markdown("**Evidence currently in scope**")
            st.markdown(
                "- Strictly prior inputs and an independent lookahead audit\n"
                "- Costs, slippage, and multiple fill resolutions\n"
                "- Combinatorial purged cross-validation (CPCV)\n"
                "- Permutation, parameter, regime, and instrument stress tests"
            )
    with explain_right:
        with st.container(border=True):
            st.markdown("**Evidence still missing**")
            st.markdown(
                "- Pre-2021 MNQ/NQ coverage\n"
                "- A completed paper forward-test\n"
                "- Cross-provider reconciliation beyond the current audit\n"
                "- Evidence that historical performance will persist"
            )


elif view == "Monte Carlo":
    st.subheader("Aggregate monthly Monte Carlo")
    st.caption(
        "Moving-block bootstrap of complete monthly P&L. Contiguous blocks preserve limited month-to-month dependence; the output is a stress distribution, not a forecast."
    )

    control_left, control_mid, control_right = st.columns(3, gap="large")
    with control_left:
        horizon_label = st.segmented_control(
            "Projection horizon",
            ["12 mo", "24 mo", "36 mo"],
            default="24 mo",
            key="mc_horizon",
        )
    with control_mid:
        block_label = st.segmented_control(
            "Bootstrap block",
            ["1 month", "3 months", "6 months"],
            default="3 months",
            key="mc_block",
        )
    with control_right:
        paths = st.selectbox(
            "Simulation paths",
            [1_000, 2_500, 5_000],
            index=1,
            key="mc_paths",
        )

    horizon_months = int(horizon_label.split()[0])
    block_months = int(block_label.split()[0])
    fan, simulated_paths, simulation = run_public_monte_carlo(
        monthly,
        horizon_months,
        paths,
        block_months,
    )

    with st.container(horizontal=True):
        st.metric(
            "Terminal P&L above zero",
            f"{simulation['probability_terminal_positive_pct']:.1f}%",
            border=True,
        )
        st.metric("P05 terminal P&L", f"${simulation['terminal_p05_usd']:,.0f}", border=True)
        st.metric(
            "Median terminal P&L",
            f"${simulation['terminal_median_usd']:,.0f}",
            border=True,
        )
        st.metric(
            "P95 drawdown magnitude",
            f"${abs(simulation['max_drawdown_p95_loss_usd']):,.0f}",
            border=True,
        )

    with st.container(border=True):
        st.subheader("Cumulative P&L percentile fan")
        st.caption(
            f"{paths:,} paths · {horizon_months}-month horizon · {block_months}-month moving blocks · fixed seed 2026 · one contract."
        )
        st.altair_chart(monte_carlo_fan(fan))

    terminal_col, drawdown_col = st.columns(2, gap="large")
    with terminal_col:
        with st.container(border=True):
            st.subheader("Terminal P&L distribution")
            st.caption("Reference rules mark zero, the fifth percentile, and the median.")
            st.altair_chart(terminal_distribution(simulated_paths, simulation))
    with drawdown_col:
        with st.container(border=True):
            st.subheader("Maximum drawdown distribution")
            st.caption("Drawdown magnitude is calculated within each simulated cumulative path.")
            st.altair_chart(drawdown_distribution(simulated_paths))

    st.subheader("Simulation interpretation")
    interpretation_left, interpretation_right = st.columns(2, gap="large")
    with interpretation_left:
        with st.container(border=True):
            st.markdown("**What the simulation changes**")
            st.markdown(
                "- Reorders observed complete-month P&L in contiguous blocks\n"
                "- Shows terminal and path-dependent drawdown uncertainty\n"
                "- Lets the horizon and dependence assumption vary\n"
                "- Keeps the public app aggregate-only"
            )
    with interpretation_right:
        with st.container(border=True):
            st.markdown("**What the simulation cannot establish**")
            st.markdown(
                "- It does not create unseen market regimes\n"
                "- It assumes the historical monthly distribution remains relevant\n"
                "- It understates intramonth drawdown and execution path risk\n"
                "- It is not a probability forecast for future trading performance"
            )


elif view == "Parameter lab":
    surface_options = {
        "Reward:risk × filter strength": {
            "key": "reward_risk_x_filter_drop",
            "x": "filter_drop_pct",
            "y": "reward_risk",
            "x_title": "Widest opening ranges excluded (%)",
            "y_title": "Reward:risk target",
        },
        "Opening range × reward:risk": {
            "key": "opening_range_x_reward_risk",
            "x": "reward_risk",
            "y": "opening_range_minutes",
            "x_title": "Reward:risk target",
            "y_title": "Opening-range length (minutes)",
        },
        "Filter strength × lookback": {
            "key": "filter_drop_x_lookback",
            "x": "lookback_days",
            "y": "filter_drop_pct",
            "x_title": "Trailing lookback (sessions)",
            "y_title": "Widest opening ranges excluded (%)",
        },
    }
    metric_options = {
        "Daily Sharpe": "daily_sharpe",
        "Profit factor": "profit_factor",
        "Net P&L": "net_pnl_usd",
    }

    st.subheader("Reviewed parameter atlas")
    st.caption(
        "Five-minute execution audit used to map the neighborhood around the frozen strategy. This is stability analysis—not permission to adopt the best full-sample cell."
    )
    frozen_left, frozen_right = st.columns([1.1, 2], gap="large")
    with frozen_left:
        with st.container(border=True):
            st.markdown("**Frozen specification**")
            st.markdown(
                "- Opening range: **30 minutes**\n"
                "- Reward:risk: **1.0**\n"
                "- Widest ranges excluded: **10%**\n"
                "- Filter lookback: **60 sessions**\n"
                "- Short trend gate: **SMA50**"
            )
    with frozen_right:
        top_left, top_right = st.columns(2)
        bottom_left, bottom_right = st.columns(2)
        with top_left:
            st.metric("Reviewed 2D cells", "81", border=True)
        with top_right:
            st.metric("Reward:risk settings", "9", border=True)
        with bottom_left:
            st.metric("Trend-gate variants", "17", border=True)
        with bottom_right:
            st.metric("Entry cutoffs", "7", border=True)

    control_left, control_right = st.columns(2, gap="large")
    with control_left:
        surface_name = st.selectbox(
            "Parameter surface",
            list(surface_options),
            key="parameter_surface",
        )
    with control_right:
        metric_name = st.segmented_control(
            "Surface metric",
            list(metric_options),
            default="Daily Sharpe",
            key="parameter_metric",
        )

    surface_spec = surface_options[surface_name]
    surface = parameter_surface_frame(snapshot, surface_spec["key"])
    metric_field = metric_options[metric_name]
    with st.container(border=True):
        st.subheader(surface_name)
        st.caption(
        "Brighter blue indicates a higher value for the selected metric. The white diamond marks the frozen cell; tooltips retain trade count and win rate."
        )
        st.altair_chart(
            parameter_surface_heatmap(
                surface,
                x_field=surface_spec["x"],
                y_field=surface_spec["y"],
                x_title=surface_spec["x_title"],
                y_title=surface_spec["y_title"],
                metric=metric_field,
            )
        )

    rr_col, gate_col = st.columns(2, gap="large")
    with rr_col:
        with st.container(border=True):
            st.subheader("Reward:risk sensitivity")
            st.caption(
                "The 1.0 setting remains frozen; higher full-sample net P&L settings failed the adoption discipline."
            )
            st.altair_chart(rr_sensitivity(rr))
    with gate_col:
        with st.container(border=True):
            st.subheader("Trend-gate length sensitivity")
            st.caption("SMA and EMA variants share the same five-minute audit lens; the diamond marks SMA50.")
            st.altair_chart(gate_sensitivity_chart(gates, metric_field))

    with st.container(border=True):
        st.subheader("Entry-window cutoff sensitivity")
        st.caption(
            "Earlier cutoffs reduce opportunity count. The fully open session is the frozen specification and uses full opacity."
        )
        st.altair_chart(cutoff_sensitivity_chart(cutoffs, metric_field))


elif view == "Validation":
    pf_min, pf_max = execution_range(execution, "profit_factor")
    sharpe_min, sharpe_max = execution_range(execution, "daily_sharpe")

    with st.container(horizontal=True):
        st.metric("Displayed execution cells", f"{len(execution)}/12", border=True)
        st.metric("Profit-factor range", f"{pf_min:.3f}–{pf_max:.3f}", border=True)
        st.metric("Daily-Sharpe range", f"{sharpe_min:.2f}–{sharpe_max:.2f}", border=True)
        st.metric("Full cost battery profitable", "24/24", border=True)

    with st.container(border=True):
        st.subheader("Execution stress matrix")
        metric = st.segmented_control(
            "Matrix metric",
            ["Profit factor", "Daily Sharpe", "Net P&L"],
            default="Profit factor",
            key="execution_metric",
        )
        metric_field = {
            "Profit factor": "profit_factor",
            "Daily Sharpe": "daily_sharpe",
            "Net P&L": "net_pnl_usd",
        }[metric]
        st.caption("Fill resolution × modeled slippage; $1.20 round-turn commission.")
        st.altair_chart(execution_heatmap(execution, metric_field))

    st.subheader("Validation ledger")
    validation = pd.DataFrame(snapshot["validation"])[
        ["test", "status", "evidence", "why_it_matters"]
    ]
    st.dataframe(
        validation,
        hide_index=True,
        column_config={
            "test": st.column_config.TextColumn("Test", pinned=True),
            "status": st.column_config.TextColumn("Status"),
            "evidence": st.column_config.TextColumn("Evidence", width="large"),
            "why_it_matters": st.column_config.TextColumn("Why it matters", width="large"),
        },
    )

    st.subheader("Failure journal")
    st.caption("A credible research project should show what was rejected, not only what survived.")
    failed = pd.DataFrame(snapshot["failed_ideas"])
    st.dataframe(
        failed,
        hide_index=True,
        column_config={
            "idea": st.column_config.TextColumn("Hypothesis", pinned=True),
            "result": st.column_config.TextColumn("Observed result", width="large"),
            "decision": st.column_config.TextColumn("Decision"),
        },
    )


elif view == "Pine Script":
    pine_manifest = load_pinescript_manifest()
    pine_backtests = load_pinescript_backtests()
    pine_monthly = pine_backtests["monthly"]
    pine_windows = pine_backtests["windows"]
    pine_qa = pine_backtests["qa"]
    pine_versions = pine_manifest["versions"]
    current_version = next(version for version in pine_versions if version["current"])
    full_export = pine_windows.loc[pine_windows["window"] == "Full export"].iloc[0]
    ytd_2026 = pine_windows.loc[pine_windows["window"] == "2026 YTD"].iloc[0]

    st.subheader("Pine Script evolution and export evidence")
    st.info(
        "This is a related **15-minute symmetric ORB implementation track**, not the "
        "exact 30-minute filtered Python engine behind the 729-trade headline snapshot. "
        "The code, hashes, and TradingView aggregates below belong to this companion track "
        "and are deliberately kept separate from the headline metrics."
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
        "Historical source headers are preserved as research records. Later corrections and "
        "the manifest status take precedence over superseded estimates in older comments."
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

    with st.container(border=True):
        st.subheader("Representative source excerpt")
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
        "Aggregate derivatives of the 2026-07-16 TradingView List of Trades export. "
        "The source trade list is hash-pinned but not published; exact timestamps, prices, "
        "signals, quantities, and individual outcomes remain outside the public boundary."
    )
    with st.container(horizontal=True):
        st.metric("Full-export net P&L", f"${full_export['net_pnl_usd']:,.0f}", border=True)
        st.metric("Full-export profit factor", f"{full_export['profit_factor']:.3f}", border=True)
        st.metric("Full-export max drawdown", f"${full_export['max_drawdown_usd']:,.0f}", border=True)
        st.metric(
            "2026 YTD net P&L",
            f"${ytd_2026['net_pnl_usd']:,.0f}",
            border=True,
        )

    with st.container(border=True):
        st.subheader("TradingView aggregate path")
        st.caption(
            "Monthly sums from 1,269 completed v4.1 MNQ trades using dynamic sizing and "
            "the reviewed TradingView fee configuration. This is not the one-contract "
            "headline series shown on Overview."
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
        "The negative 2026 YTD row is intentionally retained. Last-250 and date-window rows "
        "are descriptive diagnostics, not independent out-of-sample tests."
    )

    with st.expander("Export QA and provenance", expanded=False):
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
            st.subheader("Next acceptance steps")
            st.markdown(
                "1. Verify the wrong-symbol lock on a non-MNQ chart.\n"
                "2. Inspect one normal-session replay for markers and fixed TP/SL segments.\n"
                "3. Replay a known half-day in the split v4.1 script.\n"
                "4. Confirm exactly one observation-only alert per eligible signal.\n"
                "5. Reconcile an append-only paper log before any promotion decision."
            )
    with boundary_col:
        with st.container(border=True):
            st.subheader("What remains private")
            st.markdown(
                "- Licensed intraday OHLCV bars\n"
                "- Full TradingView trade-list exports\n"
                "- Exact signal timestamps, prices, and quantities\n"
                "- Broker, account, and execution data\n"
                "- Any credentials or automation connection"
            )
            st.caption(
                "The app is evidence and code review material—not a signal service or an execution interface."
            )


else:
    st.subheader("Public-project roadmap")

    left, right = st.columns(2, gap="large")
    with left:
        with st.container(border=True):
            st.subheader("Public architecture")
            st.code(
                """streamlit_app.py     # thin UI layer
src/data.py           # aggregate snapshot loading
src/metrics.py        # high-level quant diagnostics
src/simulations.py    # aggregate monthly bootstrap
src/charts.py         # explicit Altair specs
data/public_snapshot.json
data/backtests/       # aggregate TradingView evidence
pinescript/           # versioned Pine source + manifest
tests/                # metrics + release safeguards
scripts/              # snapshot + fail-closed release/security gate""",
                language="text",
            )
    with right:
        with st.container(border=True):
            st.subheader("Known limitations")
            for limitation in snapshot["limitations"]:
                st.markdown(f"- {limitation}")

    st.subheader("Next research milestones")
    st.markdown(
        "1. Complete and reconcile the paper forward-test.\n"
        "2. Add pre-2021 MNQ/NQ data under an appropriate license.\n"
        "3. Publish a reproducible notebook using user-supplied data.\n"
        "4. Add a CI-generated research card and versioned release.\n"
        "5. Replace the WIP label only after those exit criteria are met."
    )

st.caption(
    f"Aggregate public evidence · schema {meta['schema_version']} · generated {meta['snapshot_date']} · no raw market data included"
)
