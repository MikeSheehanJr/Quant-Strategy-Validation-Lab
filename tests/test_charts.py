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
    monte_carlo_paths,
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
        monte_carlo_paths(paths, fan),
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


def test_equity_curve_uses_solid_navy_line_and_focused_scale():
    snapshot = load_snapshot()
    chart_spec = equity_curve(monthly_frame(snapshot)).to_dict()
    assert chart_spec["layer"][0]["encoding"]["y"]["scale"]["domain"][0] == -500.0
    assert chart_spec["layer"][0]["mark"]["color"] == "#0A3D62"
    assert all(layer["mark"]["type"] != "point" for layer in chart_spec["layer"])
    assert "gradient" not in json.dumps(chart_spec).lower()


def test_annual_bars_use_full_ordered_palette_and_label_headroom():
    yearly = yearly_frame(load_snapshot())
    spec = annual_pnl(yearly).to_dict()
    bars, labels = spec["layer"]

    assert bars["encoding"]["color"]["scale"]["range"] == [
        "#0A3D62",
        "#D4AF37",
        "#2D3436",
        "#A9BEC9",
        "#0A3D62",
        "#D4AF37",
    ]
    y_domain = bars["encoding"]["y"]["scale"]["domain"]
    assert y_domain[0] == 0.0
    assert y_domain[1] >= float(yearly["pnl_usd"].max()) * 1.15
    assert bars["encoding"]["opacity"]["legend"] is None
    assert labels["mark"]["clip"] is False
    assert labels["mark"]["color"] == "#2D3436"


def test_single_series_lines_use_solid_strokes_without_nodes():
    snapshot = load_snapshot()
    monthly = monthly_frame(snapshot)
    fan, paths, _ = monthly_block_bootstrap(
        monthly, horizon_months=24, paths=250, block_months=3, seed=2026
    )
    charts = [
        pinescript_equity_curve(load_pinescript_backtests()["monthly"]),
        rr_sensitivity(rr_frame(snapshot)),
        monte_carlo_paths(paths, fan),
    ]

    for chart in charts:
        spec = chart.to_dict()
        line_marks = [
            layer["mark"]
            for layer in spec["layer"]
            if layer["mark"]["type"] == "line"
        ]
        assert line_marks
        assert all(mark["color"] in {"#0A3D62", "#A9BEC9", "#D4AF37"} for mark in line_marks)
        assert all("point" not in mark for mark in line_marks)
        assert "gradient" not in json.dumps(spec).lower()


def test_monte_carlo_uses_individual_lines_without_area_fills():
    monthly = monthly_frame(load_snapshot())
    fan, paths, _ = monthly_block_bootstrap(
        monthly, horizon_months=24, paths=250, block_months=3, seed=2026
    )
    spec = monte_carlo_paths(paths, fan, max_display_paths=80).to_dict()
    mark_types = [layer["mark"]["type"] for layer in spec["layer"]]
    assert mark_types == ["line", "line", "rule"]
    assert spec["layer"][0]["encoding"]["detail"]["field"] == "path_id"
    assert "area" not in mark_types


def test_gate_sensitivity_lines_have_no_point_nodes():
    spec = gate_sensitivity_chart(
        gate_frame(load_snapshot()), "profit_factor"
    ).to_dict()
    mark_types = [layer["mark"]["type"] for layer in spec["layer"]]
    assert mark_types == ["line", "rule"]
    assert "point" not in spec["layer"][0]["mark"]


def test_execution_heatmaps_use_four_flat_color_bands():
    snapshot = load_snapshot()
    execution = execution_frame(snapshot)
    expected = ["#E6EEF2", "#A9BEC9", "#D4AF37", "#0A3D62"]

    for metric in ("profit_factor", "daily_sharpe", "net_pnl_usd"):
        spec = execution_heatmap(execution, metric).to_dict()
        color = spec["layer"][0]["encoding"]["color"]
        assert color["field"] == "metric_band"
        assert color["type"] == "nominal"
        assert color["scale"]["range"] == expected
        assert "gradient" not in json.dumps(spec).lower()


def test_parameter_surface_uses_the_same_flat_band_language():
    snapshot = load_snapshot()
    frame = parameter_surface_frame(snapshot, "reward_risk_x_filter_drop")
    spec = parameter_surface_heatmap(
        frame,
        x_field="filter_drop_pct",
        y_field="reward_risk",
        x_title="Filter drop (%)",
        y_title="Reward:risk",
        metric="daily_sharpe",
    ).to_dict()
    color = spec["layer"][0]["encoding"]["color"]
    assert color["field"] == "metric_band"
    assert color["scale"]["range"] == ["#E6EEF2", "#A9BEC9", "#D4AF37", "#0A3D62"]
    assert "gradient" not in json.dumps(spec).lower()
