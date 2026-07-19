from __future__ import annotations

import json

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
    yearly_frame,
)
from src.simulations import monthly_block_bootstrap
from src.pinescript import load_pinescript_backtests


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
        pinescript_equity_curve(load_pinescript_backtests()["monthly"]),
    ]
    for chart in charts:
        spec = chart.to_dict()
        assert "$schema" in spec


def test_equity_curve_uses_semantic_palette_and_focused_scale():
    snapshot = load_snapshot()
    chart_spec = equity_curve(monthly_frame(snapshot)).to_dict()
    spec = json.dumps(chart_spec)

    for color in ("#D62828", "#F77F00", "#FCBF49", "#EAE2B7"):
        assert color in spec
    assert chart_spec["layer"][0]["encoding"]["y"]["scale"]["domain"][0] == -500.0
    assert chart_spec["layer"][0]["mark"]["color"]["gradient"] == "linear"
    assert all(layer["mark"]["type"] != "point" for layer in chart_spec["layer"])


def test_single_series_lines_use_gradient_strokes_without_nodes():
    snapshot = load_snapshot()
    monthly = monthly_frame(snapshot)
    fan, _, _ = monthly_block_bootstrap(
        monthly, horizon_months=24, paths=250, block_months=3, seed=2026
    )
    charts = [
        pinescript_equity_curve(load_pinescript_backtests()["monthly"]),
        rr_sensitivity(rr_frame(snapshot)),
        monte_carlo_fan(fan),
    ]

    for chart in charts:
        spec = chart.to_dict()
        line_marks = [
            layer["mark"]
            for layer in spec["layer"]
            if layer["mark"]["type"] == "line"
        ]
        assert line_marks
        assert all(mark["color"]["gradient"] == "linear" for mark in line_marks)
        assert all("point" not in mark for mark in line_marks)


def test_gate_sensitivity_lines_have_no_point_nodes():
    spec = gate_sensitivity_chart(
        gate_frame(load_snapshot()), "profit_factor"
    ).to_dict()
    mark_types = [layer["mark"]["type"] for layer in spec["layer"]]
    assert mark_types == ["line", "rule"]
    assert "point" not in spec["layer"][0]["mark"]


def test_quantitative_heatmap_runs_through_the_reviewed_palette():
    snapshot = load_snapshot()
    spec = json.dumps(
        execution_heatmap(execution_frame(snapshot), "profit_factor").to_dict()
    )

    expected = ["#003049", "#D62828", "#F77F00", "#FCBF49", "#EAE2B7"]
    assert f'"range": {json.dumps(expected)}' in spec
