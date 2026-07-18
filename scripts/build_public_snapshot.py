#!/usr/bin/env python3
"""Build an aggregate-only snapshot from the private research workspace.

This script is intentionally optional for public users. It requires separately
licensed intraday data and the private research engine. The checked-in app uses
the generated JSON and never loads raw bars or trade-level records.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib
import json
import os
import sys
from collections import defaultdict
from datetime import date
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = PROJECT_ROOT / "data" / "public_snapshot.json"


def file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _aggregate(trades: list[dict[str, Any]], key_func) -> list[dict[str, Any]]:
    buckets: dict[str, dict[str, float]] = defaultdict(
        lambda: {
            "pnl_usd": 0.0,
            "trades": 0,
            "wins": 0,
            "gross_profit": 0.0,
            "gross_loss": 0.0,
        }
    )
    for trade in trades:
        key = str(key_func(trade))
        row = buckets[key]
        row["pnl_usd"] += trade["usd"]
        row["trades"] += 1
        row["wins"] += int(trade["win"])
        if trade["usd"] > 0:
            row["gross_profit"] += trade["usd"]
        else:
            row["gross_loss"] += abs(trade["usd"])

    rows: list[dict[str, Any]] = []
    for label, values in sorted(buckets.items()):
        losses = values["gross_loss"]
        rows.append(
            {
                "label": label,
                "pnl_usd": round(values["pnl_usd"], 2),
                "trades": int(values["trades"]),
                "wins": int(values["wins"]),
                "win_rate_pct": round(values["wins"] / values["trades"] * 100, 1),
                "profit_factor": round(values["gross_profit"] / losses, 3)
                if losses
                else None,
            }
        )
    return rows


def _public_atlas_metrics(values: dict[str, Any]) -> dict[str, Any]:
    """Keep reviewed strategy aggregates and exclude deployment economics."""

    return {
        "trades": values["n"],
        "win_rate_pct": values["win"],
        "profit_factor": values["pf"],
        "daily_sharpe": values["sharpe"],
        "net_pnl_usd": values["net"],
    }


def build_snapshot(source_root: Path) -> dict[str, Any]:
    source_root = source_root.resolve()
    required_paths = {
        "engine": source_root / "scripts" / "qa_v2_lib.py",
        "atlas": source_root / "reports" / "qa_param_atlas.json",
        "stress_report": source_root / "reports" / "qa_v2_stress_report.md",
    }
    missing = [str(path) for path in required_paths.values() if not path.exists()]
    if missing:
        raise FileNotFoundError(
            "The private research workspace is incomplete. Missing: " + ", ".join(missing)
        )

    sys.path.insert(0, str(source_root))
    qa = importlib.import_module("scripts.qa_v2_lib")
    trades: list[dict[str, Any]] = qa.v2_trades(tf=30)
    context = qa.sym_ctx(tf=30)
    stats = qa.stats(trades)

    monthly_source = _aggregate(trades, lambda trade: trade["day"][:7])
    monthly: list[dict[str, Any]] = []
    cumulative = 0.0
    for row in monthly_source:
        cumulative += row["pnl_usd"]
        period_status = "Partial" if row["label"] in {"2021-06", "2026-06"} else "Complete"
        monthly.append(
            {
                "month": row["label"],
                "period_status": period_status,
                "pnl_usd": row["pnl_usd"],
                "cumulative_pnl_usd": round(cumulative, 2),
                "trades": row["trades"],
                "wins": row["wins"],
                "win_rate_pct": row["win_rate_pct"],
            }
        )

    yearly_source = _aggregate(trades, lambda trade: trade["day"][:4])
    yearly = [
        {
            "year": row["label"],
            "period_status": "Partial" if row["label"] in {"2021", "2026"} else "Complete",
            **{key: value for key, value in row.items() if key != "label"},
        }
        for row in yearly_source
    ]
    sides = _aggregate(trades, lambda trade: "Long" if trade["side"] == 1 else "Short")
    for row in sides:
        row["side"] = row.pop("label")

    with required_paths["atlas"].open(encoding="utf-8") as handle:
        atlas = json.load(handle)

    execution = []
    for key, values in atlas["exec"].items():
        fill_minutes, slippage_ticks = key.split("|")
        execution.append(
            {
                "fill_minutes": int(fill_minutes),
                "slippage_ticks": float(slippage_ticks),
                "trades": values["n"],
                "win_rate_pct": values["win"],
                "profit_factor": values["pf"],
                "daily_sharpe": values["sharpe"],
                "net_pnl_usd": values["net"],
            }
        )

    rr_sensitivity = []
    for key, values in atlas["rr"].items():
        rr_sensitivity.append(
            {
                "reward_risk": float(key),
                "trades": values["n"],
                "win_rate_pct": values["win"],
                "profit_factor": values["pf"],
                "daily_sharpe": values["sharpe"],
                "net_pnl_usd": values["net"],
            }
        )

    parameter_surfaces: dict[str, list[dict[str, Any]]] = {
        "reward_risk_x_filter_drop": [],
        "opening_range_x_reward_risk": [],
        "filter_drop_x_lookback": [],
    }
    for key, values in atlas["rr_x_drop"].items():
        reward_risk, filter_drop_pct = key.split("|")
        parameter_surfaces["reward_risk_x_filter_drop"].append(
            {
                "reward_risk": float(reward_risk),
                "filter_drop_pct": int(filter_drop_pct),
                "is_frozen": float(reward_risk) == 1.0 and int(filter_drop_pct) == 10,
                **_public_atlas_metrics(values),
            }
        )
    for key, values in atlas["or_x_rr"].items():
        opening_range_minutes, reward_risk = key.split("|")
        parameter_surfaces["opening_range_x_reward_risk"].append(
            {
                "opening_range_minutes": int(opening_range_minutes),
                "reward_risk": float(reward_risk),
                "is_frozen": int(opening_range_minutes) == 30 and float(reward_risk) == 1.0,
                **_public_atlas_metrics(values),
            }
        )
    for key, values in atlas["drop_x_look"].items():
        filter_drop_pct, lookback_days = key.split("|")
        parameter_surfaces["filter_drop_x_lookback"].append(
            {
                "filter_drop_pct": int(filter_drop_pct),
                "lookback_days": int(lookback_days),
                "is_frozen": int(filter_drop_pct) == 10 and int(lookback_days) == 60,
                **_public_atlas_metrics(values),
            }
        )

    gate_sensitivity = []
    for key, values in atlas["gate"].items():
        if key == "off":
            gate_sensitivity.append(
                {
                    "gate_kind": "Off",
                    "gate_length": 0,
                    "is_frozen": False,
                    **_public_atlas_metrics(values),
                }
            )
            continue
        gate_kind = "SMA" if key.startswith("sma") else "EMA"
        gate_length = int(key[3:])
        gate_sensitivity.append(
            {
                "gate_kind": gate_kind,
                "gate_length": gate_length,
                "is_frozen": gate_kind == "SMA" and gate_length == 50,
                **_public_atlas_metrics(values),
            }
        )

    entry_cutoff_sensitivity = []
    for order, (label, values) in enumerate(atlas["cutoff"].items()):
        entry_cutoff_sensitivity.append(
            {
                "entry_cutoff": label,
                "display_order": order,
                "is_frozen": label == "16:00 (none)",
                **_public_atlas_metrics(values),
            }
        )

    return {
        "meta": {
            "schema_version": "1.1.0",
            "snapshot_date": date.today().isoformat(),
            "research_window": "Jun 2021–Jun 2026",
            "instrument": "MNQ (Micro E-mini Nasdaq-100 futures)",
            "strategy_family": "30-minute opening-range breakout",
            "data_granularity": "Monthly P&L and reviewed aggregate stress cells",
            "source_data_description": "Licensed exchange-derived MNQ intraday bars",
            "raw_market_data_included": False,
            "trade_level_records_included": False,
            "source_artifact_hashes": {
                label: file_sha256(path) for label, path in required_paths.items()
            },
        },
        "headline": {
            "trade_count": stats["n"],
            "win_rate_pct": stats["win"],
            "profit_factor": stats["pf"],
            "net_pnl_per_contract_usd": stats["net"],
            "max_loss_per_contract_usd": stats["maxloss"],
            "expectancy_r": stats["expr"],
            "daily_sharpe": round(qa.sharpe(trades, context["univ"]), 3),
            "commission_round_turn_usd": 1.20,
            "modeled_slippage_ticks": 0.5,
            "fill_resolution_minutes": 30,
        },
        "monthly": monthly,
        "yearly": yearly,
        "sides": sides,
        "execution": sorted(
            execution, key=lambda row: (row["fill_minutes"], row["slippage_ticks"])
        ),
        "rr_sensitivity": sorted(rr_sensitivity, key=lambda row: row["reward_risk"]),
        "parameter_surfaces": {
            key: sorted(
                rows,
                key=lambda row: tuple(
                    value
                    for field, value in row.items()
                    if field
                    in {
                        "reward_risk",
                        "filter_drop_pct",
                        "opening_range_minutes",
                        "lookback_days",
                    }
                ),
            )
            for key, rows in parameter_surfaces.items()
        },
        "gate_sensitivity": sorted(
            gate_sensitivity, key=lambda row: (row["gate_kind"], row["gate_length"])
        ),
        "entry_cutoff_sensitivity": entry_cutoff_sensitivity,
        "validation": [
            {
                "test": "Lookahead audit",
                "status": "Passed",
                "evidence": "0/1,289 opening-range mismatches; 0/1,508 trend-gate mismatches",
                "why_it_matters": "Confirms inputs were reconstructed from information available before entry.",
            },
            {
                "test": "Probabilistic Sharpe ratio",
                "status": "Passed",
                "evidence": "PSR 0.9995; 3.30σ versus zero",
                "why_it_matters": "Adjusts the Sharpe evidence for non-normal returns.",
            },
            {
                "test": "Deflated Sharpe ratio",
                "status": "Passed with caveat",
                "evidence": "DSR 0.961 at raw N=140 configurations",
                "why_it_matters": "Penalizes the result for multiple testing and model search.",
            },
            {
                "test": "Combinatorial purged CV",
                "status": "Passed",
                "evidence": "45/45 OOS-positive splits; p10 Sharpe 0.63",
                "why_it_matters": "Tests the result across embargoed out-of-sample combinations.",
            },
            {
                "test": "Direction permutation",
                "status": "Passed",
                "evidence": "Actual Sharpe 1.46; p < 0.0005",
                "why_it_matters": "Rejects the null that breakout direction was arbitrary.",
            },
            {
                "test": "Fill resolution × costs",
                "status": "Passed",
                "evidence": "24/24 full stress cells profitable; displayed PF range 1.247–1.326",
                "why_it_matters": "Checks whether the edge depends on optimistic execution assumptions.",
            },
        ],
        "failed_ideas": [
            {
                "idea": "Regime-switched reward:risk targets",
                "result": "Honest walk-forward delta was approximately +0.01; selection wins were unstable.",
                "decision": "Rejected",
            },
            {
                "idea": "VWAP trailing exit",
                "result": "Win rate fell to roughly 35–38% and funded-objective performance deteriorated.",
                "decision": "Rejected",
            },
            {
                "idea": "End-of-day exit",
                "result": "Lost 34/45 CPCV splits versus the frozen 1:1 exit.",
                "decision": "Rejected",
            },
            {
                "idea": "Universal cross-instrument edge",
                "result": "ES/MES retained only about 40% of the effect; gold was weak pre-sample.",
                "decision": "Rejected",
            },
            {
                "idea": "Retune to the best full-sample parameter",
                "result": "Several higher full-sample cells failed the pre-registered CPCV adoption bar.",
                "decision": "Rejected",
            },
        ],
        "project_status": [
            {
                "phase": "1. Public safety boundary",
                "status": "Complete",
                "objective": "Separate the portfolio project from the private strategy workspace.",
                "evidence": "Aggregate-only data contract and release scanner.",
            },
            {
                "phase": "2. Evidence snapshot",
                "status": "Complete",
                "objective": "Package verified metrics without redistributing intraday data.",
                "evidence": "Versioned JSON with source hashes and reconciliation tests.",
            },
            {
                "phase": "3. Dashboard MVP",
                "status": "Complete",
                "objective": "Make the research legible to a recruiter in under one minute.",
                "evidence": "Overview, robustness, and build-log views.",
            },
            {
                "phase": "4. Automated QA",
                "status": "Complete",
                "objective": "Test calculations, charts, app rendering, and release safety.",
                "evidence": "pytest suite, CI workflow, and public-release preflight.",
            },
            {
                "phase": "5. Publishing kit",
                "status": "Complete",
                "objective": "Prepare LinkedIn, GitHub, profile, and resume instructions.",
                "evidence": "Step-by-step publishing guide and copy templates.",
            },
            {
                "phase": "6. Hosted launch",
                "status": "Pending",
                "objective": "Publish only after a final human review of the staged repository.",
                "evidence": "Public GitHub URL, live Streamlit URL, and logged-out review.",
            },
            {
                "phase": "7. Forward validation",
                "status": "Planned",
                "objective": "Reconcile paper signals and extend evidence beyond the research sample.",
                "evidence": "Versioned forward-test log and predefined pass/fail criteria.",
            },
        ],
        "limitations": [
            "Historical backtests can overstate future performance even after extensive validation.",
            "The MNQ/NQ sample begins in June 2021; pre-2021 Nasdaq regimes are not covered.",
            "The 2026 calendar bar is a partial year ending in June.",
            "Monthly aggregates conceal intramonth drawdown and path dependence.",
            "The public snapshot cannot reproduce the backtest without separately licensed raw data.",
            "No live-money execution claim is made; paper forward-testing remains outstanding.",
        ],
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--source-root",
        type=Path,
        required=True,
        help="Path to the private research workspace with licensed data.",
    )
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    source_root = args.source_root.resolve()
    previous_working_directory = Path.cwd()
    os.chdir(source_root)
    try:
        snapshot = build_snapshot(source_root)
    finally:
        os.chdir(previous_working_directory)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(snapshot, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote aggregate-only snapshot: {args.output}")


if __name__ == "__main__":
    main()
