"""Mutation checks for the published snapshot boundary."""

from __future__ import annotations

import copy
import json
from argparse import Namespace

import pytest

from scripts import build_public_snapshot
from src.contracts import validate_public_snapshot
from src.data import load_snapshot


@pytest.fixture
def snapshot():
    return copy.deepcopy(load_snapshot())


def test_checked_in_snapshot_passes_contract(snapshot):
    assert validate_public_snapshot(snapshot) is snapshot


@pytest.mark.parametrize(
    ("change", "match"),
    [
        (lambda s: s["meta"].update(schema_version="1.0.0"), "meta.schema_version"),
        (lambda s: s["meta"].update(trade_level_records_included=0), "trade_level_records_included"),
        (lambda s: s["meta"].update(raw_market_data_included=True), "raw_market_data_included"),
        (lambda s: s["meta"].update(snapshot_date="2026-02-30"), "meta.snapshot_date"),
        (lambda s: s["meta"].update(research_window="Jan 2021–Jun 2026"), "meta.research_window"),
        (lambda s: s["headline"].update(trade_count=True), "headline.trade_count"),
        (lambda s: s["headline"].update(profit_factor=float("nan")), "headline.profit_factor"),
        (lambda s: s["headline"].update(win_rate_pct=100.1), "headline.win_rate_pct"),
        (lambda s: s["headline"].update(fill_resolution_minutes=7), "execution baseline"),
        (lambda s: s["monthly"][0].update(trades="2"), r"monthly\[0\].trades"),
        (lambda s: s["monthly"][0].pop("wins"), r"monthly\[0\]"),
        (lambda s: s["monthly"][0].update(month="2021-13"), r"monthly\[0\].month"),
        (lambda s: s["monthly"][1].update(month="2021-08"), "chronological and continuous"),
        (lambda s: s["monthly"][0].update(period_status="Complete"), "period_status"),
        (lambda s: s["monthly"][1].update(cumulative_pnl_usd=999), "cumulative_pnl_usd"),
        (lambda s: s["yearly"][0].update(trades=62, win_rate_pct=67.7), r"yearly\[0\].trades"),
        (lambda s: s["yearly"][0].update(pnl_usd=1826.3), r"yearly\[0\].pnl_usd"),
        (lambda s: s["sides"][0].update(pnl_usd=11795.3), "sides.pnl_usd"),
        (lambda s: s["sides"][0].update(wins=999), r"sides\[0\].wins"),
        (lambda s: s["monthly"][1].update(win_rate_pct=0), "win_rate_pct"),
        (lambda s: s["execution"][0].update(fill_minutes=[1]), "wrong axis type"),
        (lambda s: next(r for r in s["execution"] if r["fill_minutes"] == 30
                        and r["slippage_ticks"] == 0.5).update(net_pnl_usd=999),
         "execution baseline"),
        (lambda s: next(r for r in s["parameter_surfaces"]["filter_drop_x_lookback"]
                        if r["is_frozen"]).update(trades=1), "frozen atlas"),
        (lambda s: s.update(unreviewed_trades=[]), "extra"),
    ],
)
def test_bad_schema_and_reconciliation_are_rejected(snapshot, change, match):
    change(snapshot)
    with pytest.raises(ValueError, match=match):
        validate_public_snapshot(snapshot)


@pytest.mark.parametrize(
    ("section", "match"),
    [
        ("execution", "duplicate grid cell"),
        ("rr_sensitivity", "duplicate grid cell"),
        ("gate_sensitivity", "duplicate grid cell"),
    ],
)
def test_duplicate_grid_cell_is_rejected(snapshot, section, match):
    snapshot[section].append(copy.deepcopy(snapshot[section][0]))
    with pytest.raises(ValueError, match=match):
        validate_public_snapshot(snapshot)


@pytest.mark.parametrize(
    "section",
    ["execution", "rr_sensitivity", "reward_risk_x_filter_drop",
     "opening_range_x_reward_risk", "filter_drop_x_lookback",
     "gate_sensitivity", "entry_cutoff_sensitivity"],
)
def test_missing_grid_cell_is_rejected(snapshot, section):
    rows = (snapshot["parameter_surfaces"][section]
            if section in snapshot["parameter_surfaces"] else snapshot[section])
    rows.pop()
    with pytest.raises(ValueError, match="incomplete grid"):
        validate_public_snapshot(snapshot)


@pytest.mark.parametrize(
    "section",
    ["reward_risk_x_filter_drop", "opening_range_x_reward_risk", "filter_drop_x_lookback",
     "gate_sensitivity", "entry_cutoff_sensitivity"],
)
def test_frozen_marker_must_match_configuration(snapshot, section):
    rows = (snapshot["parameter_surfaces"][section]
            if section in snapshot["parameter_surfaces"] else snapshot[section])
    frozen = next(row for row in rows if row["is_frozen"])
    frozen["is_frozen"] = False
    with pytest.raises(ValueError, match="frozen configuration"):
        validate_public_snapshot(snapshot)


def test_loader_checks_nested_data_before_returning(tmp_path, snapshot):
    snapshot["execution"][0]["daily_sharpe"] = float("inf")
    path = tmp_path / "bad.json"
    path.write_text(json.dumps(snapshot), encoding="utf-8")
    with pytest.raises(ValueError, match="execution\\[0\\].daily_sharpe"):
        load_snapshot(path)


def test_loader_rejects_duplicate_json_keys(tmp_path):
    path = tmp_path / "duplicate.json"
    path.write_text('{"meta": {}, "meta": {}}', encoding="utf-8")
    with pytest.raises(ValueError, match="duplicate key: meta"):
        load_snapshot(path)


def test_builder_rejects_invalid_export_before_writing(monkeypatch, tmp_path, snapshot):
    snapshot["meta"]["trade_level_records_included"] = True
    output = tmp_path / "published.json"
    output.write_bytes(b"existing published evidence")
    monkeypatch.setattr(build_public_snapshot, "parse_args",
                        lambda: Namespace(source_root=tmp_path, output=output))
    monkeypatch.setattr(build_public_snapshot, "build_snapshot", lambda _: snapshot)
    with pytest.raises(ValueError, match="trade_level_records_included"):
        build_public_snapshot.main()
    assert output.read_bytes() == b"existing published evidence"
