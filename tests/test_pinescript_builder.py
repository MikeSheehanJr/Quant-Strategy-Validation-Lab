from __future__ import annotations

import csv

import pytest

from scripts.build_pinescript_evidence import (
    REQUIRED_COLUMNS,
    build_monthly_rows,
    build_window_rows,
    read_and_validate_export,
)


def _row(number: int, row_type: str, timestamp: str, pnl: float, cumulative: float):
    side = "long" if number == 1 else "short"
    values = {
        "Trade number": str(number),
        "Type": f"{row_type} {side}",
        "Date and time": timestamp,
        "Signal": "test signal",
        "Price USD": "100.00",
        "Size (qty)": "1",
        "Size (value)": "100.00",
        "Net PnL USD": f"{pnl:.2f}",
        "Return %": "0.10",
        "Favorable excursion USD": "10.00",
        "Favorable excursion %": "0.10",
        "Adverse excursion USD": "-5.00",
        "Adverse excursion %": "-0.05",
        "Cumulative PnL USD": f"{cumulative:.2f}",
        "Cumulative PnL %": "0.10",
        "Duration (bars)": "2",
    }
    return values


def _write_export(path, rows):
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=REQUIRED_COLUMNS)
        writer.writeheader()
        writer.writerows(rows)


def test_builder_validates_pairs_and_aggregates(tmp_path):
    export = tmp_path / "reviewed.csv"
    rows = [
        _row(1, "Exit", "2025-01-02 11:00", 25.0, 25.0),
        _row(1, "Entry", "2025-01-02 10:00", 25.0, 25.0),
        _row(2, "Exit", "2026-01-03 11:00", -10.0, 15.0),
        _row(2, "Entry", "2026-01-03 10:00", -10.0, 15.0),
    ]
    _write_export(export, rows)

    trades, qa = read_and_validate_export(export)
    monthly = build_monthly_rows(trades)
    windows = build_window_rows(trades)
    assert qa["complete_trades"] == "2"
    assert len(monthly) == 2
    assert monthly[-1]["cumulative_pnl_usd"] == "15.00"
    assert windows[0]["net_pnl_usd"] == "15.00"


def test_builder_rejects_spreadsheet_formula_prefix(tmp_path):
    export = tmp_path / "unsafe.csv"
    rows = [
        _row(1, "Exit", "2025-01-02 11:00", 25.0, 25.0),
        _row(1, "Entry", "2025-01-02 10:00", 25.0, 25.0),
    ]
    rows[0]["Signal"] = "=HYPERLINK(test)"
    _write_export(export, rows)
    with pytest.raises(ValueError, match="formula prefix"):
        read_and_validate_export(export)
