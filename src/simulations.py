"""Deterministic, aggregate-only Monte Carlo helpers for the public dashboard."""

from __future__ import annotations

import math

import numpy as np
import pandas as pd

from src.metrics import complete_months


def monthly_block_bootstrap(
    monthly: pd.DataFrame,
    *,
    horizon_months: int = 24,
    paths: int = 2_500,
    block_months: int = 3,
    seed: int = 2026,
) -> tuple[pd.DataFrame, pd.DataFrame, dict[str, float | int]]:
    """Resample contiguous blocks of complete monthly P&L observations.

    This is a distributional stress view, not a forecast. It deliberately uses
    only the checked-in monthly aggregates so the public app never needs raw
    bars, daily paths, or trade-level records.
    """

    sample = complete_months(monthly)
    values = sample["pnl_usd"].to_numpy(dtype=float)
    if values.size < 12:
        raise ValueError("At least 12 complete monthly observations are required")
    if horizon_months < 1 or paths < 1 or block_months < 1:
        raise ValueError("Simulation dimensions must be positive")
    if block_months > values.size:
        raise ValueError("Block length cannot exceed the historical monthly sample")

    rng = np.random.default_rng(seed)
    blocks_needed = math.ceil(horizon_months / block_months)
    starts = rng.integers(
        0,
        values.size - block_months + 1,
        size=(paths, blocks_needed),
    )
    offsets = np.arange(block_months)
    sampled = values[starts[..., None] + offsets].reshape(paths, -1)[:, :horizon_months]

    cumulative = np.cumsum(sampled, axis=1)
    cumulative = np.concatenate([np.zeros((paths, 1)), cumulative], axis=1)
    percentiles = np.quantile(cumulative, [0.05, 0.25, 0.50, 0.75, 0.95], axis=0)
    fan = pd.DataFrame(
        {
            "month": np.arange(horizon_months + 1),
            "p05": percentiles[0],
            "p25": percentiles[1],
            "p50": percentiles[2],
            "p75": percentiles[3],
            "p95": percentiles[4],
        }
    )

    running_peak = np.maximum.accumulate(cumulative, axis=1)
    max_drawdown = (cumulative - running_peak).min(axis=1)
    terminal = cumulative[:, -1]
    path_frame = pd.DataFrame(
        {
            "path_id": np.arange(1, paths + 1),
            "terminal_pnl_usd": terminal,
            "max_drawdown_usd": max_drawdown,
        }
    )
    terminal_p05 = float(np.quantile(terminal, 0.05))
    summary: dict[str, float | int] = {
        "historical_months": int(values.size),
        "horizon_months": int(horizon_months),
        "paths": int(paths),
        "block_months": int(block_months),
        "seed": int(seed),
        "probability_terminal_positive_pct": float((terminal > 0).mean() * 100),
        "terminal_p05_usd": terminal_p05,
        "terminal_median_usd": float(np.median(terminal)),
        "terminal_p95_usd": float(np.quantile(terminal, 0.95)),
        "terminal_expected_shortfall_usd": float(terminal[terminal <= terminal_p05].mean()),
        "max_drawdown_median_usd": float(np.median(max_drawdown)),
        "max_drawdown_p95_loss_usd": float(np.quantile(max_drawdown, 0.05)),
    }
    return fan, path_frame, summary
