"""Small, testable calculations used by the dashboard."""

from __future__ import annotations

import math

import pandas as pd


def max_drawdown_from_monthly(monthly: pd.DataFrame) -> float:
    """Compute peak-to-trough drawdown from aggregate monthly P&L."""

    if monthly.empty:
        return 0.0
    equity = monthly["pnl_usd"].cumsum()
    equity_with_origin = pd.concat([pd.Series([0.0]), equity], ignore_index=True)
    drawdown = equity_with_origin - equity_with_origin.cummax()
    return float(drawdown.min())


def profitable_year_count(yearly: pd.DataFrame) -> tuple[int, int]:
    """Return profitable periods and total periods in the yearly snapshot."""

    if yearly.empty:
        return 0, 0
    return int((yearly["pnl_usd"] > 0).sum()), int(len(yearly))


def execution_range(execution: pd.DataFrame, field: str) -> tuple[float, float]:
    """Return minimum and maximum for an execution stress metric."""

    if execution.empty:
        return 0.0, 0.0
    return float(execution[field].min()), float(execution[field].max())


def complete_months(monthly: pd.DataFrame) -> pd.DataFrame:
    """Exclude explicitly partial edge months from distributional analysis."""

    if "period_status" not in monthly:
        return monthly.copy()
    return monthly.loc[monthly["period_status"] == "Complete"].copy()


def max_drawdown_duration_months(monthly: pd.DataFrame) -> int:
    """Return the longest run below the prior aggregate equity peak."""

    if monthly.empty:
        return 0
    equity = pd.concat(
        [pd.Series([0.0]), monthly["pnl_usd"].cumsum().reset_index(drop=True)],
        ignore_index=True,
    )
    underwater = equity < equity.cummax()
    longest = current = 0
    for is_underwater in underwater:
        current = current + 1 if bool(is_underwater) else 0
        longest = max(longest, current)
    return int(longest)


def quant_summary(monthly: pd.DataFrame) -> dict[str, float | int]:
    """Compute high-level, dollar-based diagnostics from complete monthly aggregates."""

    sample = complete_months(monthly)
    if sample.empty:
        return {
            "sample_months": 0,
            "positive_month_rate_pct": 0.0,
            "mean_monthly_pnl_usd": 0.0,
            "annualized_pnl_usd": 0.0,
            "annualized_volatility_usd": 0.0,
            "monthly_sortino": 0.0,
            "skewness": 0.0,
            "excess_kurtosis": 0.0,
            "historical_var_95_usd": 0.0,
            "historical_cvar_95_usd": 0.0,
            "best_month_usd": 0.0,
            "worst_month_usd": 0.0,
            "max_drawdown_usd": 0.0,
            "max_drawdown_duration_months": 0,
            "recovery_factor": 0.0,
        }

    pnl = sample["pnl_usd"].astype(float)
    mean = float(pnl.mean())
    volatility = float(pnl.std(ddof=0))
    downside = pnl.clip(upper=0.0)
    downside_deviation = math.sqrt(float((downside**2).mean()))
    q05 = float(pnl.quantile(0.05))
    tail = pnl.loc[pnl <= q05]
    max_drawdown = max_drawdown_from_monthly(sample)
    total_pnl = float(pnl.sum())

    return {
        "sample_months": int(len(pnl)),
        "positive_month_rate_pct": float((pnl > 0).mean() * 100),
        "mean_monthly_pnl_usd": mean,
        "annualized_pnl_usd": mean * 12,
        "annualized_volatility_usd": volatility * math.sqrt(12),
        "monthly_sortino": mean / downside_deviation * math.sqrt(12)
        if downside_deviation
        else 0.0,
        "skewness": float(pnl.skew()),
        "excess_kurtosis": float(pnl.kurt()),
        "historical_var_95_usd": q05,
        "historical_cvar_95_usd": float(tail.mean()),
        "best_month_usd": float(pnl.max()),
        "worst_month_usd": float(pnl.min()),
        "max_drawdown_usd": max_drawdown,
        "max_drawdown_duration_months": max_drawdown_duration_months(sample),
        "recovery_factor": total_pnl / abs(max_drawdown) if max_drawdown else 0.0,
    }
