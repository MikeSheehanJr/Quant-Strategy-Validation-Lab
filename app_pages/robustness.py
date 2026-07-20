"""Interactive historical robustness and stress-testing page."""

from __future__ import annotations

import pandas as pd
import streamlit as st

from src.charts import (
    cutoff_sensitivity_chart,
    drawdown_distribution,
    execution_heatmap,
    gate_sensitivity_chart,
    monthly_pnl_distribution,
    monte_carlo_paths,
    parameter_surface_heatmap,
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
)
from src.metrics import execution_range, max_drawdown_from_monthly, quant_summary
from src.simulations import monthly_block_bootstrap
from src.ui import render_page_header, render_section_header


MONTE_CARLO_CACHE_SCHEMA = "cumulative-paths-v1"


@st.cache_data(show_spinner=False, max_entries=24)
def run_research_monte_carlo(
    monthly: pd.DataFrame,
    horizon_months: int,
    paths: int,
    block_months: int,
    cache_schema: str,
):
    """Return deterministic aggregate resamples for the research dashboard."""

    if cache_schema != MONTE_CARLO_CACHE_SCHEMA:
        raise ValueError("Unsupported Monte Carlo cache schema")
    return monthly_block_bootstrap(
        monthly,
        horizon_months=horizon_months,
        paths=paths,
        block_months=block_months,
        seed=2026,
    )


snapshot = load_snapshot()
monthly = monthly_frame(snapshot)
execution = execution_frame(snapshot)
rr = rr_frame(snapshot)
gates = gate_frame(snapshot)
cutoffs = entry_cutoff_frame(snapshot)

render_page_header(
    "Historical research diagnostics",
    "Robustness",
    "I use four complementary lenses to look for fragility in the historical result. I’m "
    "trying to learn where the strategy breaks. I am not turning the sample into a forecast.",
)

with st.container(border=True, key="robustness_switcher"):
    view = st.segmented_control(
        "Robustness view",
        ["Historical risk", "Monte Carlo", "Parameters", "Validation"],
        default="Historical risk",
        key="robustness_view",
    )


if view == "Historical risk":
    risk = quant_summary(monthly)
    max_monthly_dd = max_drawdown_from_monthly(monthly)

    render_section_header(
        "Historical risk snapshot",
        f"These dollar based diagnostics cover {risk['sample_months']} complete months. "
        "Partial edge months are excluded.",
        key="historical_risk",
    )
    with st.container(horizontal=True, gap="small"):
        st.metric(
            "Positive complete months",
            f"{risk['positive_month_rate_pct']:.1f}%",
            border=True,
        )
        st.metric("Annualized P&L", f"${risk['annualized_pnl_usd']:,.0f}", border=True)
        st.metric(
            "Annualized P&L volatility",
            f"${risk['annualized_volatility_usd']:,.0f}",
            border=True,
        )
        st.metric("Monthly Sortino", f"{risk['monthly_sortino']:.2f}", border=True)

    distribution_col, tail_col = st.columns([1.5, 1], gap="small")
    with distribution_col:
        with st.container(border=True):
            st.subheader("Complete month P&L distribution")
            st.caption(
                "This histogram covers 59 complete monthly aggregates; the rule marks zero."
            )
            st.altair_chart(monthly_pnl_distribution(monthly))
    with tail_col:
        with st.container(border=True):
            st.subheader("Tail and path diagnostics")
            diagnostics = pd.DataFrame(
                [
                    {
                        "Metric": "Historical monthly VaR (95%)",
                        "Value": f"${risk['historical_var_95_usd']:,.0f}",
                    },
                    {
                        "Metric": "Historical monthly CVaR (95%)",
                        "Value": f"${risk['historical_cvar_95_usd']:,.0f}",
                    },
                    {"Metric": "Monthly skewness", "Value": f"{risk['skewness']:.2f}"},
                    {
                        "Metric": "Excess kurtosis",
                        "Value": f"{risk['excess_kurtosis']:.2f}",
                    },
                    {
                        "Metric": "Aggregate max drawdown",
                        "Value": f"${risk['max_drawdown_usd']:,.0f}",
                    },
                    {
                        "Metric": "Longest aggregate recovery",
                        "Value": f"{risk['max_drawdown_duration_months']} months",
                    },
                    {
                        "Metric": "Recovery factor",
                        "Value": f"{risk['recovery_factor']:.2f}×",
                    },
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

    with st.container(horizontal=True, gap="small"):
        st.metric(
            "Aggregate monthly max drawdown",
            f"${max_monthly_dd:,.0f}",
            border=True,
        )
        st.metric("CPCV positive OOS splits", "45/45", border=True)
        st.metric("PSR vs zero", "3.30σ", border=True)

    with st.container(border=True, key="risk_caveat", gap="xxsmall"):
        st.caption(
            "VaR and CVaR are empirical monthly diagnostics. They are not capital requirements "
            "and do not capture intramonth execution paths."
        )


elif view == "Monte Carlo":
    with st.container(border=True, key="monte_carlo_controls"):
        st.subheader("Aggregate monthly Monte Carlo")
        st.caption(
            "This moving block bootstrap resamples complete monthly P&L. Contiguous blocks "
            "preserve limited dependence between months; the output is a stress distribution, "
            "not a forecast."
        )
        control_left, control_mid, control_right = st.columns(3, gap="small")
        with control_left:
            horizon_label = st.segmented_control(
                "Simulation horizon",
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
    fan, simulated_paths, simulation = run_research_monte_carlo(
        monthly,
        horizon_months,
        paths,
        block_months,
        MONTE_CARLO_CACHE_SCHEMA,
    )

    with st.container(horizontal=True, gap="small"):
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
        st.subheader("Cumulative P&L simulation paths")
        st.caption(
            f"{min(paths, 180):,} representative lines from {paths:,} simulations · "
            f"{horizon_months}-month horizon · {block_months}-month moving blocks · "
            "fixed seed 2026 · one contract. Every simulation informs the metrics above."
        )
        st.altair_chart(monte_carlo_paths(simulated_paths, fan))

    terminal_col, drawdown_col = st.columns([1.05, 1], gap="small")
    with terminal_col:
        with st.container(border=True):
            st.subheader("Terminal P&L distribution")
            st.caption("Reference lines mark zero, the fifth percentile, and the median.")
            st.altair_chart(terminal_distribution(simulated_paths, simulation))
    with drawdown_col:
        with st.container(border=True):
            st.subheader("Maximum drawdown distribution")
            st.caption("Drawdown magnitude is calculated within each cumulative path.")
            st.altair_chart(drawdown_distribution(simulated_paths))

    simulation_scope = pd.DataFrame(
        [
            {
                "Question": "Sequence uncertainty",
                "Treatment": "Reorder complete month P&L in contiguous blocks",
                "Boundary": "Observed monthly distribution only",
            },
            {
                "Question": "Path and terminal dispersion",
                "Treatment": "Display distinct simulation paths and maximum drawdown",
                "Boundary": "No intramonth execution path",
            },
            {
                "Question": "Assumption sensitivity",
                "Treatment": "Vary horizon, path count, and block length",
                "Boundary": "Cannot create unseen regimes",
            },
        ]
    )
    with st.container(border=True, key="simulation_scope"):
        st.subheader("Simulation scope")
        st.dataframe(
            simulation_scope,
            hide_index=True,
            column_config={
                "Question": st.column_config.TextColumn(
                    "Question", pinned=True, width="medium"
                ),
                "Treatment": st.column_config.TextColumn("What changes", width="large"),
                "Boundary": st.column_config.TextColumn("What remains unknown", width="large"),
            },
        )


elif view == "Parameters":
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
            "y_title": "Opening range length (minutes)",
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

    render_section_header(
        "Reviewed parameter atlas",
        "A five-minute execution audit around the frozen specification. This is stability "
        "analysis. It is not permission to adopt the best full-sample cell.",
        key="parameter_atlas",
    )
    frozen_specification = pd.DataFrame(
        [
            {"Parameter": "Opening range", "Frozen value": "30 minutes"},
            {"Parameter": "Reward:risk", "Frozen value": "1.0"},
            {"Parameter": "Widest ranges excluded", "Frozen value": "10%"},
            {"Parameter": "Filter lookback", "Frozen value": "60 sessions"},
            {"Parameter": "Short trend gate", "Frozen value": "SMA50"},
        ]
    )
    frozen_left, frozen_right = st.columns([1.1, 2], gap="small")
    with frozen_left:
        with st.container(border=True, height="stretch"):
            st.subheader("Frozen specification")
            st.dataframe(
                frozen_specification,
                hide_index=True,
                column_config={
                    "Parameter": st.column_config.TextColumn("Parameter", pinned=True),
                    "Frozen value": st.column_config.TextColumn("Frozen value"),
                },
            )
    with frozen_right:
        with st.container(horizontal=True, gap="small"):
            st.metric("Reviewed 2D cells", "81", border=True)
            st.metric("Reward:risk settings", "9", border=True)
            st.metric("Gate variants", "17", border=True)
            st.metric("Entry cutoffs", "7", border=True)

    with st.container(border=True, key="parameter_controls"):
        control_left, control_right = st.columns([1.1, 1], gap="small")
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
            "Four flat color bands rank the selected metric from low to high. The outlined "
            "diamond marks the frozen cell; tooltips retain trade count and win rate."
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

    rr_col, gate_col = st.columns([1, 1.05], gap="small")
    with rr_col:
        with st.container(border=True):
            st.subheader("Reward:risk sensitivity")
            st.caption(
                "The 1.0 setting remains frozen; I did not adopt settings with higher P&L from the "
                "full sample."
            )
            st.altair_chart(rr_sensitivity(rr))
    with gate_col:
        with st.container(border=True):
            st.subheader("Trend gate sensitivity")
            st.caption(
                "SMA and EMA variants share the same audit lens; the vertical rule marks SMA50."
            )
            st.altair_chart(gate_sensitivity_chart(gates, metric_field))

    with st.container(border=True):
        st.subheader("Entry window cutoff sensitivity")
        st.caption(
            "Earlier cutoffs reduce opportunity count. The open session is the frozen "
            "specification and uses full opacity."
        )
        st.altair_chart(cutoff_sensitivity_chart(cutoffs, metric_field))


else:
    pf_min, pf_max = execution_range(execution, "profit_factor")
    sharpe_min, sharpe_max = execution_range(execution, "daily_sharpe")

    render_section_header(
        "Validation and rejected ideas",
        "Successful stress tests and rejected hypotheses share the same review surface.",
        key="validation_ledger",
    )
    with st.container(horizontal=True, gap="small"):
        st.metric("Displayed execution cells", f"{len(execution)}/12", border=True)
        st.metric("Profit factor range", f"{pf_min:.3f}–{pf_max:.3f}", border=True)
        st.metric("Daily Sharpe range", f"{sharpe_min:.2f}–{sharpe_max:.2f}", border=True)
        st.metric("Profitable cost stress cells", "24/24", border=True)

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
        st.caption(
            "The matrix crosses fill resolution with modeled slippage under a $1.20 "
            "round turn commission."
        )
        st.altair_chart(execution_heatmap(execution, metric_field))

    validation = pd.DataFrame(snapshot["validation"])[
        ["test", "status", "evidence", "why_it_matters"]
    ]
    with st.container(border=True, key="validation_table"):
        st.subheader("Validation ledger")
        st.dataframe(
            validation,
            hide_index=True,
            column_config={
                "test": st.column_config.TextColumn("Test", pinned=True),
                "status": st.column_config.TextColumn("Status"),
                "evidence": st.column_config.TextColumn("Evidence", width="large"),
                "why_it_matters": st.column_config.TextColumn(
                    "Why it matters", width="large"
                ),
            },
        )

    failed = pd.DataFrame(snapshot["failed_ideas"])
    with st.container(border=True, key="failure_table"):
        st.subheader("Failure journal")
        st.caption(
            "I keep rejected ideas visible instead of letting them disappear from the "
            "research record."
        )
        st.dataframe(
            failed,
            hide_index=True,
            column_config={
                "idea": st.column_config.TextColumn("Hypothesis", pinned=True),
                "result": st.column_config.TextColumn("Observed result", width="large"),
                "decision": st.column_config.TextColumn("Decision"),
            },
        )
