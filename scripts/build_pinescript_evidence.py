#!/usr/bin/env python3
"""Validate a TradingView trade-list export and publish aggregate evidence CSVs."""

from __future__ import annotations

import argparse
import csv
import hashlib
import math
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path


REQUIRED_COLUMNS = [
    "Trade number",
    "Type",
    "Date and time",
    "Signal",
    "Price USD",
    "Size (qty)",
    "Size (value)",
    "Net PnL USD",
    "Return %",
    "Favorable excursion USD",
    "Favorable excursion %",
    "Adverse excursion USD",
    "Adverse excursion %",
    "Cumulative PnL USD",
    "Cumulative PnL %",
    "Duration (bars)",
]


@dataclass(frozen=True)
class Trade:
    number: int
    exited_at: datetime
    side: str
    pnl_usd: float
    cumulative_pnl_usd: float
    duration_bars: int


def _number(value: str, field: str) -> float:
    try:
        parsed = float(value)
    except ValueError as exc:
        raise ValueError(f"{field} contains a non-numeric value") from exc
    if not math.isfinite(parsed):
        raise ValueError(f"{field} contains a non-finite value")
    return parsed


def _drawdown(pnls: list[float]) -> float:
    cumulative = 0.0
    peak = 0.0
    worst = 0.0
    for pnl in pnls:
        cumulative += pnl
        peak = max(peak, cumulative)
        worst = max(worst, peak - cumulative)
    return worst


def _metrics(trades: list[Trade]) -> dict[str, float | int]:
    pnls = [trade.pnl_usd for trade in trades]
    wins = [pnl for pnl in pnls if pnl > 0]
    losses = [pnl for pnl in pnls if pnl < 0]
    gross_profit = sum(wins)
    gross_loss = sum(losses)
    return {
        "trades": len(trades),
        "winning_trades": len(wins),
        "losing_trades": len(losses),
        "net_pnl_usd": sum(pnls),
        "mean_trade_usd": sum(pnls) / len(pnls),
        "win_rate_pct": len(wins) / len(pnls) * 100,
        "profit_factor": gross_profit / abs(gross_loss) if gross_loss else math.inf,
        "gross_profit_usd": gross_profit,
        "gross_loss_usd": gross_loss,
        "max_drawdown_usd": _drawdown(pnls),
    }


def read_and_validate_export(path: Path) -> tuple[list[Trade], dict[str, str]]:
    raw = path.read_bytes()
    digest = hashlib.sha256(raw).hexdigest()
    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames != REQUIRED_COLUMNS:
            raise ValueError(
                "TradingView schema mismatch; expected the reviewed List of Trades columns"
            )
        rows = list(reader)

    if not rows:
        raise ValueError("TradingView export is empty")
    if any(value == "" for row in rows for value in row.values()):
        raise ValueError("TradingView export contains missing cells")
    if len({tuple(row[column] for column in REQUIRED_COLUMNS) for row in rows}) != len(rows):
        raise ValueError("TradingView export contains duplicate rows")
    for row in rows:
        for field in ("Type", "Signal"):
            if row[field].lstrip().startswith(("=", "+", "@")):
                raise ValueError(f"unsafe spreadsheet formula prefix in {field}")

    grouped: dict[int, list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        grouped[int(row["Trade number"])].append(row)
    expected_ids = list(range(1, len(grouped) + 1))
    if sorted(grouped) != expected_ids:
        raise ValueError("trade identifiers are not contiguous from 1")

    trades: list[Trade] = []
    pair_error = 0.0
    cumulative_error = 0.0
    running_pnl = 0.0
    for number in expected_ids:
        pair = grouped[number]
        entries = [row for row in pair if row["Type"].startswith("Entry ")]
        exits = [row for row in pair if row["Type"].startswith("Exit ")]
        if len(pair) != 2 or len(entries) != 1 or len(exits) != 1:
            raise ValueError(f"trade {number} is not one complete entry/exit pair")
        entry, exit_row = entries[0], exits[0]
        entry_side = entry["Type"].split()[-1]
        exit_side = exit_row["Type"].split()[-1]
        if entry_side != exit_side:
            raise ValueError(f"trade {number} changes side between entry and exit")

        entry_pnl = _number(entry["Net PnL USD"], "Net PnL USD")
        exit_pnl = _number(exit_row["Net PnL USD"], "Net PnL USD")
        pair_error = max(pair_error, abs(entry_pnl - exit_pnl))
        running_pnl += exit_pnl
        reported_cumulative = _number(exit_row["Cumulative PnL USD"], "Cumulative PnL USD")
        cumulative_error = max(cumulative_error, abs(running_pnl - reported_cumulative))

        trades.append(
            Trade(
                number=number,
                exited_at=datetime.strptime(exit_row["Date and time"], "%Y-%m-%d %H:%M"),
                side=exit_side,
                pnl_usd=exit_pnl,
                cumulative_pnl_usd=reported_cumulative,
                duration_bars=int(exit_row["Duration (bars)"]),
            )
        )

    if pair_error > 0.005:
        raise ValueError(f"entry/exit P&L disagreement exceeds tolerance: {pair_error}")
    if cumulative_error > 0.011:
        raise ValueError(f"cumulative P&L reconciliation exceeds tolerance: {cumulative_error}")

    qa = {
        "source_sha256": digest,
        "source_rows": str(len(rows)),
        "complete_trades": str(len(trades)),
        "duplicate_rows": "0",
        "missing_cells": "0",
        "entry_exit_pnl_max_error_usd": f"{pair_error:.6f}",
        "cumulative_pnl_max_error_usd": f"{cumulative_error:.6f}",
        "first_exit_month": trades[0].exited_at.strftime("%Y-%m"),
        "last_exit_month": trades[-1].exited_at.strftime("%Y-%m"),
    }
    return trades, qa


def build_monthly_rows(trades: list[Trade]) -> list[dict[str, str | int | float]]:
    grouped: dict[str, list[Trade]] = defaultdict(list)
    for trade in trades:
        grouped[trade.exited_at.strftime("%Y-%m")].append(trade)

    cumulative = 0.0
    output: list[dict[str, str | int | float]] = []
    for month in sorted(grouped):
        metrics = _metrics(grouped[month])
        cumulative += float(metrics["net_pnl_usd"])
        output.append(
            {
                "month": month,
                "trades": metrics["trades"],
                "winning_trades": metrics["winning_trades"],
                "losing_trades": metrics["losing_trades"],
                "win_rate_pct": f"{metrics['win_rate_pct']:.2f}",
                "net_pnl_usd": f"{metrics['net_pnl_usd']:.2f}",
                "cumulative_pnl_usd": f"{cumulative:.2f}",
                "gross_profit_usd": f"{metrics['gross_profit_usd']:.2f}",
                "gross_loss_usd": f"{metrics['gross_loss_usd']:.2f}",
                "profit_factor": f"{metrics['profit_factor']:.3f}",
                "within_month_max_drawdown_usd": f"{metrics['max_drawdown_usd']:.2f}",
            }
        )
    return output


def build_window_rows(trades: list[Trade]) -> list[dict[str, str | int]]:
    windows = [
        ("Full export", trades),
        ("2020+", [trade for trade in trades if trade.exited_at.year >= 2020]),
        ("2023+", [trade for trade in trades if trade.exited_at.year >= 2023]),
        ("2024+", [trade for trade in trades if trade.exited_at.year >= 2024]),
        ("Last 250 trades", trades[-250:]),
        ("2026 YTD", [trade for trade in trades if trade.exited_at.year == 2026]),
    ]
    output: list[dict[str, str | int]] = []
    for label, selected in windows:
        metrics = _metrics(selected)
        output.append(
            {
                "window": label,
                "start_month": selected[0].exited_at.strftime("%Y-%m"),
                "end_month": selected[-1].exited_at.strftime("%Y-%m"),
                "trades": int(metrics["trades"]),
                "net_pnl_usd": f"{metrics['net_pnl_usd']:.2f}",
                "mean_trade_usd": f"{metrics['mean_trade_usd']:.2f}",
                "win_rate_pct": f"{metrics['win_rate_pct']:.2f}",
                "profit_factor": f"{metrics['profit_factor']:.3f}",
                "max_drawdown_usd": f"{metrics['max_drawdown_usd']:.2f}",
            }
        )
    return output


def write_rows(path: Path, rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mnq-export", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, default=Path("data/backtests"))
    parser.add_argument("--expected-sha256")
    parser.add_argument("--expected-trades", type=int)
    args = parser.parse_args()

    trades, qa = read_and_validate_export(args.mnq_export)
    if args.expected_sha256 and qa["source_sha256"] != args.expected_sha256:
        raise ValueError("source SHA-256 does not match the reviewed export")
    if args.expected_trades and len(trades) != args.expected_trades:
        raise ValueError("complete trade count does not match the reviewed export")

    monthly_rows = build_monthly_rows(trades)
    window_rows = build_window_rows(trades)
    qa_rows = [
        {
            "check": key,
            "status": "PASS",
            "value": value,
            "interpretation": {
                "source_sha256": "Pins the reviewed TradingView export without publishing it.",
                "source_rows": "TradingView emits one entry and one exit row per completed trade.",
                "complete_trades": "Complete entry/exit pairs available for aggregation.",
                "duplicate_rows": "Exact duplicate source rows found.",
                "missing_cells": "Blank source cells found.",
                "entry_exit_pnl_max_error_usd": "Maximum P&L disagreement within a trade pair.",
                "cumulative_pnl_max_error_usd": "Maximum error versus reconstructed cumulative P&L.",
                "first_exit_month": "First month represented in the reviewed export.",
                "last_exit_month": "Last month represented in the reviewed export.",
            }[key],
        }
        for key, value in qa.items()
    ]

    write_rows(args.output_dir / "orb_sym_v4_1_mnq_monthly.csv", monthly_rows)
    write_rows(args.output_dir / "orb_sym_v4_1_mnq_windows.csv", window_rows)
    write_rows(args.output_dir / "orb_sym_v4_1_mnq_qa.csv", qa_rows)
    print(
        f"Published {len(monthly_rows)} monthly rows and {len(window_rows)} windows "
        f"from {len(trades)} reviewed MNQ trades."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
