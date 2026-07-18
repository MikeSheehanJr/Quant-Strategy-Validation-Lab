from __future__ import annotations

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
    yearly_frame,
)
from src.simulations import monthly_block_bootstrap


def test_chart_specs_compile():
    snapshot = load_snapshot()
    monthly = monthly_frame(snapshot)
    fan, paths, summary = monthly_block_bootstrap(
        monthly, horizon_months=24, paths=500, block_months=3, seed=2026
    )
    rr_filter = parameter_surface_frame(snapshot, "reward_risk_x_filter_drop")
    charts = [
        equity_curve(monthly),
        annual_pnl(yearly_frame(snapshot)),
        monthly_pnl_distribution(monthly),
        execution_heatmap(execution_frame(snapshot), "profit_factor"),
        execution_heatmap(execution_frame(snapshot), "daily_sharpe"),
        execution_heatmap(execution_frame(snapshot), "net_pnl_usd"),
        rr_sensitivity(rr_frame(snapshot)),
        monte_carlo_fan(fan),
        terminal_distribution(paths, summary),
        drawdown_distribution(paths),
        parameter_surface_heatmap(
            rr_filter,
            x_field="filter_drop_pct",
            y_field="reward_risk",
            x_title="Filter drop (%)",
            y_title="Reward:risk",
            metric="daily_sharpe",
        ),
        gate_sensitivity_chart(gate_frame(snapshot), "profit_factor"),
        cutoff_sensitivity_chart(entry_cutoff_frame(snapshot), "net_pnl_usd"),
    ]
    for chart in charts:
        spec = chart.to_dict()
        assert "$schema" in spec
