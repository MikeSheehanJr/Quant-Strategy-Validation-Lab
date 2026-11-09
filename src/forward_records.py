"""Pure validation for public month aggregates and revision history."""

from __future__ import annotations

import math
import re
from datetime import date
from typing import Any


MONTH = re.compile(r"[0-9]{4}-(0[1-9]|1[0-2])\Z")
PUBLIC_MONTH_KEYS = {
    "month", "revision", "supersedes_revision", "revision_reason", "eligible_sessions",
    "opportunities_detected", "resolved_trades", "no_trade_decisions",
    "unresolved_opportunities", "negative_trades", "tracking_errors", "net_pnl_r",
    "within_month_max_drawdown_r",
}


def _whole(value: Any, name: str) -> int:
    if type(value) is not int or value < 0:
        raise ValueError(f"{name} must be a nonnegative integer")
    return value


def _finite(value: Any, name: str) -> float:
    if type(value) not in (int, float) or not math.isfinite(value):
        raise ValueError(f"{name} must be a finite number")
    return float(value)


def _month_start(month: str) -> date:
    if not isinstance(month, str) or not MONTH.fullmatch(month):
        raise ValueError("Invalid public month")
    return date.fromisoformat(month + "-01")


def _next_month(month: str) -> date:
    start = _month_start(month)
    return date(start.year + (start.month == 12), start.month % 12 + 1, 1)


def validate_public_monthly_records(
    records: list[dict[str, Any]], candidate: dict[str, Any], protocol: dict[str, Any],
    as_of: date | None = None,
) -> dict[str, Any]:
    """Check aggregate accounting, corrections, revision history, and sample gate."""

    if not isinstance(records, list):
        raise ValueError("Monthly records must be a list")
    latest: dict[str, dict[str, Any]] = {}
    errors_ever: dict[str, int] = {}
    seen: set[tuple[str, int]] = set()
    last_new_month: str | None = None
    for record in records:
        if not isinstance(record, dict) or set(record) != PUBLIC_MONTH_KEYS:
            raise ValueError("Monthly record has missing or private fields")
        month = record["month"]
        _month_start(month)
        if as_of is not None and _next_month(month) > as_of:
            raise ValueError("Future or still-open calendar month cannot be published")
        revision = _whole(record["revision"], "revision")
        if revision < 1 or (month, revision) in seen:
            raise ValueError("Month revisions must be positive and unique")
        seen.add((month, revision))
        prior = latest.get(month)
        if prior is None:
            if last_new_month is not None and month <= last_new_month:
                raise ValueError("New months must be introduced chronologically")
            last_new_month = month
            if revision != 1 or record["supersedes_revision"] is not None or record["revision_reason"] != "original":
                raise ValueError("Original month must start at revision one")
        else:
            if (revision != prior["revision"] + 1
                    or record["supersedes_revision"] != prior["revision"]
                    or record["revision_reason"] != "correction"):
                raise ValueError("Correction must retain and identify its prior revision")
        latest[month] = record

        for field in ("eligible_sessions", "opportunities_detected", "resolved_trades",
                      "no_trade_decisions", "unresolved_opportunities", "negative_trades",
                      "tracking_errors"):
            _whole(record[field], field)
        errors_ever[month] = max(errors_ever.get(month, 0), record["tracking_errors"])
        if record["eligible_sessions"] == 0 or record["opportunities_detected"] > record["eligible_sessions"]:
            raise ValueError("A month needs eligible sessions and at most one opportunity per session")
        if record["opportunities_detected"] != (record["resolved_trades"]
                                               + record["no_trade_decisions"]
                                               + record["unresolved_opportunities"]):
            raise ValueError("Every detected opportunity must be accounted for")
        if record["negative_trades"] > record["resolved_trades"]:
            raise ValueError("Negative trade count exceeds resolved trades")
        if record["resolved_trades"] == 0 and _finite(record["net_pnl_r"], "net_pnl_r") != 0:
            raise ValueError("Zero trades cannot carry P&L")
        if _finite(record["within_month_max_drawdown_r"], "within_month_max_drawdown_r") < 0:
            raise ValueError("Drawdown magnitude cannot be negative")

    ordered_months = sorted(latest)
    if ordered_months and candidate.get("collection_start"):
        start = date.fromisoformat(candidate["collection_start"])
        if start.day != 1 or ordered_months[0] != start.strftime("%Y-%m"):
            raise ValueError("First month must begin on the frozen collection start")
        for before, after in zip(ordered_months, ordered_months[1:]):
            if _next_month(before) != _month_start(after):
                raise ValueError("Every intervening calendar month must be reported")

    complete = sum(item["unresolved_opportunities"] == 0 for item in latest.values())
    trades = sum(item["resolved_trades"] for item in latest.values())
    unresolved = sum(item["unresolved_opportunities"] for item in latest.values())
    net_r = sum(item["net_pnl_r"] for item in latest.values())
    tracking_errors = sum(errors_ever.values())
    review_ready = (complete >= protocol["first_review_complete_months"]
                    and trades >= protocol["first_review_resolved_trades"]
                    and unresolved == protocol["max_unresolved_for_conclusion"])
    return {"public_observation_count": trades, "complete_months": complete,
            "resolved_trades": trades, "unresolved_opportunities": unresolved,
            "net_pnl_r": net_r, "tracking_errors": tracking_errors,
            "review_ready": review_ready}
