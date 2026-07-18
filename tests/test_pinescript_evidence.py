from __future__ import annotations

from src.pinescript import load_pinescript_backtests, load_pinescript_manifest


def test_pinescript_manifest_pins_five_versions():
    manifest = load_pinescript_manifest()
    versions = manifest["versions"]
    assert [version["version"] for version in versions] == ["v1", "v2", "v3", "v4", "v4.1"]
    assert sum(version["current"] for version in versions) == 1
    assert versions[-1]["evidence_status"].startswith("TradingView compile/run")


def test_public_pinescript_backtests_reconcile():
    backtests = load_pinescript_backtests()
    monthly = backtests["monthly"]
    windows = backtests["windows"]
    qa = backtests["qa"]

    full = windows.loc[windows["window"] == "Full export"].iloc[0]
    ytd = windows.loc[windows["window"] == "2026 YTD"].iloc[0]
    assert int(full["trades"]) == 1269
    assert round(float(full["net_pnl_usd"]), 2) == 16378.76
    assert round(float(monthly["net_pnl_usd"].sum()), 2) == 16378.76
    assert round(float(monthly.iloc[-1]["cumulative_pnl_usd"]), 2) == 16378.76
    assert float(ytd["net_pnl_usd"]) < 0
    assert set(qa["status"]) == {"PASS"}
