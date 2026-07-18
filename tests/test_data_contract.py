from __future__ import annotations

import pytest

from src.data import (
    entry_cutoff_frame,
    execution_frame,
    gate_frame,
    load_snapshot,
    monthly_frame,
    parameter_surface_frame,
    yearly_frame,
)
from src.metrics import (
    execution_range,
    max_drawdown_from_monthly,
    profitable_year_count,
    quant_summary,
)
from src.simulations import monthly_block_bootstrap


@pytest.fixture(scope="module")
def snapshot():
    return load_snapshot()


def test_headline_reconciles_to_verified_gate(snapshot):
    headline = snapshot["headline"]
    assert headline["trade_count"] == 729
    assert headline["win_rate_pct"] == 58.8
    assert headline["profit_factor"] == 1.315
    assert headline["daily_sharpe"] == 1.317
    assert headline["net_pnl_per_contract_usd"] == 16935


def test_aggregates_reconcile(snapshot):
    monthly = monthly_frame(snapshot)
    yearly = yearly_frame(snapshot)
    assert len(monthly) == 61
    assert int(monthly["trades"].sum()) == snapshot["headline"]["trade_count"]
    assert int(yearly["trades"].sum()) == snapshot["headline"]["trade_count"]
    assert round(float(monthly["pnl_usd"].sum())) == snapshot["headline"][
        "net_pnl_per_contract_usd"
    ]
    assert round(float(monthly.iloc[-1]["cumulative_pnl_usd"])) == snapshot["headline"][
        "net_pnl_per_contract_usd"
    ]


def test_public_snapshot_excludes_raw_records(snapshot):
    meta = snapshot["meta"]
    assert meta["raw_market_data_included"] is False
    assert meta["trade_level_records_included"] is False
    assert meta["data_granularity"] == "Monthly P&L and reviewed aggregate stress cells"
    assert meta["schema_version"] == "1.1.0"


def test_summary_helpers(snapshot):
    monthly = monthly_frame(snapshot)
    yearly = yearly_frame(snapshot)
    execution = execution_frame(snapshot)
    assert max_drawdown_from_monthly(monthly) < 0
    assert profitable_year_count(yearly) == (6, 6)
    low, high = execution_range(execution, "profit_factor")
    assert low == pytest.approx(1.247)
    assert high == pytest.approx(1.326)


def test_execution_matrix_is_complete(snapshot):
    execution = execution_frame(snapshot)
    assert len(execution) == 12
    assert set(execution["fill_minutes"]) == {1, 5, 15, 30}
    assert set(execution["slippage_ticks"]) == {0.5, 1.0, 2.0}
    assert (execution["profit_factor"] > 1.0).all()


def test_parameter_atlas_is_complete_and_marks_frozen_cells(snapshot):
    expected = {
        "reward_risk_x_filter_drop": 30,
        "opening_range_x_reward_risk": 16,
        "filter_drop_x_lookback": 35,
    }
    for surface, rows in expected.items():
        frame = parameter_surface_frame(snapshot, surface)
        assert len(frame) == rows
        assert int(frame["is_frozen"].sum()) == 1
        assert (frame["trades"] > 0).all()
    assert len(gate_frame(snapshot)) == 17
    assert int(gate_frame(snapshot)["is_frozen"].sum()) == 1
    assert len(entry_cutoff_frame(snapshot)) == 7
    assert int(entry_cutoff_frame(snapshot)["is_frozen"].sum()) == 1


def test_quant_summary_uses_complete_months(snapshot):
    monthly = monthly_frame(snapshot)
    summary = quant_summary(monthly)
    assert summary["sample_months"] == 59
    assert summary["positive_month_rate_pct"] == pytest.approx(76.2712)
    assert summary["max_drawdown_usd"] == pytest.approx(-2264.0)
    assert summary["max_drawdown_duration_months"] == 11
    assert summary["monthly_sortino"] == pytest.approx(2.8397, abs=1e-4)


def test_monthly_bootstrap_is_reproducible(snapshot):
    monthly = monthly_frame(snapshot)
    fan_a, paths_a, summary_a = monthly_block_bootstrap(
        monthly, horizon_months=24, paths=1_000, block_months=3, seed=2026
    )
    fan_b, paths_b, summary_b = monthly_block_bootstrap(
        monthly, horizon_months=24, paths=1_000, block_months=3, seed=2026
    )
    assert fan_a.equals(fan_b)
    assert paths_a.equals(paths_b)
    assert summary_a == summary_b
    assert summary_a["historical_months"] == 59
    assert summary_a["probability_terminal_positive_pct"] == pytest.approx(97.4)
    assert summary_a["max_drawdown_p95_loss_usd"] < 0
