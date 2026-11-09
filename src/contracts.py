"""Schema 1.1.0 contract for the aggregate-only public research snapshot.

The checked-in artifact is evidence, so invalid data must fail at the load and
export boundaries instead of being silently coerced by pandas or a chart.
"""

from __future__ import annotations

from collections import defaultdict
from datetime import date
from decimal import Decimal
from itertools import product
import math
import re
from typing import Any


SCHEMA_VERSION = "1.1.0"
TOP_LEVEL = {
    "meta", "headline", "monthly", "yearly", "sides", "execution",
    "rr_sensitivity", "parameter_surfaces", "gate_sensitivity",
    "entry_cutoff_sensitivity", "validation", "failed_ideas",
    "project_status", "limitations",
}
METRIC_FIELDS = {
    "trades", "win_rate_pct", "profit_factor", "daily_sharpe", "net_pnl_usd",
}


def _fail(path: str, reason: str) -> None:
    raise ValueError(f"{path}: {reason}")


def _record(value: Any, path: str, fields: set[str]) -> dict[str, Any]:
    if not isinstance(value, dict):
        _fail(path, "must be an object")
    missing, extra = fields - value.keys(), value.keys() - fields
    if missing or extra:
        _fail(path, f"fields differ (missing={sorted(missing)}, extra={sorted(extra)})")
    return value


def _rows(value: Any, path: str) -> list[dict[str, Any]]:
    if not isinstance(value, list) or not value:
        _fail(path, "must be a nonempty array")
    return value


def _text(value: Any, path: str) -> str:
    if not isinstance(value, str) or not value.strip():
        _fail(path, "must be nonempty text")
    return value


def _boolean(value: Any, path: str) -> bool:
    if type(value) is not bool:
        _fail(path, "must be a boolean")
    return value


def _number(value: Any, path: str, *, integer: bool = False,
            minimum: float | None = None, maximum: float | None = None) -> int | float:
    if integer:
        if type(value) is not int:
            _fail(path, "must be an integer")
    elif type(value) not in (int, float) or not math.isfinite(value):
        _fail(path, "must be a finite number")
    if minimum is not None and value < minimum:
        _fail(path, f"must be at least {minimum}")
    if maximum is not None and value > maximum:
        _fail(path, f"must be at most {maximum}")
    return value


def _date(value: Any, path: str) -> date:
    _text(value, path)
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", value):
        _fail(path, "must be an ISO date")
    try:
        return date.fromisoformat(value)
    except ValueError:
        _fail(path, "must be a valid ISO date")


def _month(value: Any, path: str) -> tuple[int, int]:
    _text(value, path)
    if not re.fullmatch(r"\d{4}-(0[1-9]|1[0-2])", value):
        _fail(path, "must be YYYY-MM")
    return int(value[:4]), int(value[5:])


def _status(value: Any, path: str) -> None:
    if value not in ("Partial", "Complete") or type(value) is not str:
        _fail(path, "must be Partial or Complete")


def _counted_metrics(row: dict[str, Any], path: str, *, pnl_field: str,
                     with_wins: bool = False, with_pf: bool = True,
                     with_sharpe: bool = False) -> None:
    trades = _number(row["trades"], f"{path}.trades", integer=True, minimum=1)
    _number(row[pnl_field], f"{path}.{pnl_field}")
    if with_wins:
        wins = _number(row["wins"], f"{path}.wins", integer=True, minimum=0)
        if wins > trades:
            _fail(f"{path}.wins", "cannot exceed trades")
    _number(row["win_rate_pct"], f"{path}.win_rate_pct", minimum=0, maximum=100)
    if with_wins and abs(row["win_rate_pct"] - 100 * wins / trades) > 0.050000001:
        _fail(f"{path}.win_rate_pct", "does not reconcile with wins/trades at one decimal")
    if with_pf:
        _number(row["profit_factor"], f"{path}.profit_factor", minimum=0)
    if with_sharpe:
        _number(row["daily_sharpe"], f"{path}.daily_sharpe")


def _decimal(value: int | float) -> Decimal:
    return Decimal(str(value))


def _near(actual: Decimal, expected: Decimal, tolerance: str, path: str) -> None:
    if abs(actual - expected) > Decimal(tolerance):
        _fail(path, f"does not reconcile ({actual} versus {expected})")


def _grid(rows: list[dict[str, Any]], path: str,
          axes: dict[str, tuple[Any, ...]], fields: set[str],
          *, frozen: tuple[Any, ...] | None = None,
          expected_cells: set[tuple[Any, ...]] | None = None) -> None:
    seen: set[tuple[Any, ...]] = set()
    axis_names = tuple(axes)
    expected = (expected_cells if expected_cells is not None
                else set(product(*(axes[name] for name in axis_names))))
    for index, value in enumerate(_rows(rows, path)):
        row_path = f"{path}[{index}]"
        row = _record(value, row_path, fields)
        for name in axis_names:
            if type(row[name]) is not type(axes[name][0]):
                _fail(f"{row_path}.{name}", "has the wrong axis type")
        key = tuple(row[name] for name in axis_names)
        if key not in expected:
            _fail(row_path, f"unexpected grid cell {key}")
        if key in seen:
            _fail(row_path, f"duplicate grid cell {key}")
        seen.add(key)
        _counted_metrics(row, row_path, pnl_field="net_pnl_usd", with_sharpe=True)
        if frozen is not None:
            marker = _boolean(row["is_frozen"], f"{row_path}.is_frozen")
            if marker is not (key == frozen):
                _fail(f"{row_path}.is_frozen", "does not match the frozen configuration")
    missing = expected - seen
    if missing:
        _fail(path, f"incomplete grid; missing {sorted(missing, key=str)}")


def validate_public_snapshot(snapshot: Any) -> dict[str, Any]:
    """Validate one complete public snapshot, returning it unchanged.

    P&L cells are generated at cents, while the headline is published at whole
    dollars. Cross-view allowances bound only independent cent rounding; they
    do not require exact equality to the rounded headline.
    """
    s = _record(snapshot, "snapshot", TOP_LEVEL)
    meta = _record(s["meta"], "meta", {
        "schema_version", "snapshot_date", "research_window", "instrument",
        "strategy_family", "data_granularity", "source_data_description",
        "raw_market_data_included", "trade_level_records_included",
        "source_artifact_hashes",
    })
    if meta["schema_version"] != SCHEMA_VERSION or type(meta["schema_version"]) is not str:
        _fail("meta.schema_version", f"must be {SCHEMA_VERSION}")
    _date(meta["snapshot_date"], "meta.snapshot_date")
    for name in ("research_window", "instrument", "strategy_family",
                 "data_granularity", "source_data_description"):
        _text(meta[name], f"meta.{name}")
    for name in ("raw_market_data_included", "trade_level_records_included"):
        if _boolean(meta[name], f"meta.{name}") is not False:
            _fail(f"meta.{name}", "must be false for a public aggregate snapshot")
    hashes = _record(meta["source_artifact_hashes"], "meta.source_artifact_hashes",
                     {"engine", "atlas", "stress_report"})
    for name, value in hashes.items():
        if type(value) is not str or not re.fullmatch(r"[0-9a-f]{64}", value):
            _fail(f"meta.source_artifact_hashes.{name}", "must be a SHA-256 hex digest")

    headline = _record(s["headline"], "headline", {
        "trade_count", "win_rate_pct", "profit_factor",
        "net_pnl_per_contract_usd", "max_loss_per_contract_usd",
        "expectancy_r", "daily_sharpe", "commission_round_turn_usd",
        "modeled_slippage_ticks", "fill_resolution_minutes",
    })
    _number(headline["trade_count"], "headline.trade_count", integer=True, minimum=1)
    _number(headline["win_rate_pct"], "headline.win_rate_pct", minimum=0, maximum=100)
    _number(headline["profit_factor"], "headline.profit_factor", minimum=0)
    _number(headline["net_pnl_per_contract_usd"], "headline.net_pnl_per_contract_usd",
            integer=True)
    _number(headline["max_loss_per_contract_usd"], "headline.max_loss_per_contract_usd", maximum=0)
    _number(headline["expectancy_r"], "headline.expectancy_r")
    _number(headline["daily_sharpe"], "headline.daily_sharpe")
    _number(headline["commission_round_turn_usd"], "headline.commission_round_turn_usd", minimum=0)
    _number(headline["modeled_slippage_ticks"], "headline.modeled_slippage_ticks", minimum=0)
    _number(headline["fill_resolution_minutes"], "headline.fill_resolution_minutes", integer=True, minimum=1)

    monthly = _rows(s["monthly"], "monthly")
    years: dict[int, list[dict[str, Any]]] = defaultdict(list)
    monthly_total = Decimal(0)
    months: list[tuple[int, int]] = []
    for index, value in enumerate(monthly):
        path = f"monthly[{index}]"
        row = _record(value, path, {"month", "period_status", "pnl_usd",
                                    "cumulative_pnl_usd", "trades", "wins", "win_rate_pct"})
        month = _month(row["month"], f"{path}.month")
        if months and (month[0] * 12 + month[1]) != (months[-1][0] * 12 + months[-1][1] + 1):
            _fail(f"{path}.month", "months must be chronological and continuous")
        months.append(month)
        _status(row["period_status"], f"{path}.period_status")
        expected_status = "Partial" if index in (0, len(monthly) - 1) else "Complete"
        if row["period_status"] != expected_status:
            _fail(f"{path}.period_status", f"must be {expected_status} for this sample position")
        _counted_metrics(row, path, pnl_field="pnl_usd", with_wins=True, with_pf=False)
        _number(row["cumulative_pnl_usd"], f"{path}.cumulative_pnl_usd")
        monthly_total += _decimal(row["pnl_usd"])
        _near(_decimal(row["cumulative_pnl_usd"]), monthly_total, "0.01",
              f"{path}.cumulative_pnl_usd")
        years[month[0]].append(row)
    first = date(months[0][0], months[0][1], 1)
    last = date(months[-1][0], months[-1][1], 1)
    if meta["research_window"] != f"{first:%b %Y}–{last:%b %Y}":
        _fail("meta.research_window", "does not match the monthly endpoints")

    yearly = _rows(s["yearly"], "yearly")
    if len(yearly) != len(years):
        _fail("yearly", "must include each month-grouped calendar year once")
    yearly_total = Decimal(0)
    for index, value in enumerate(yearly):
        path = f"yearly[{index}]"
        row = _record(value, path, {"year", "period_status", "pnl_usd", "trades",
                                    "wins", "win_rate_pct", "profit_factor"})
        year = _text(row["year"], f"{path}.year")
        if not re.fullmatch(r"\d{4}", year) or int(year) != sorted(years)[index]:
            _fail(f"{path}.year", "years must follow the monthly calendar years")
        _status(row["period_status"], f"{path}.period_status")
        group = years[int(year)]
        expected_status = "Partial" if any(m["period_status"] == "Partial" for m in group) else "Complete"
        if row["period_status"] != expected_status:
            _fail(f"{path}.period_status", "does not match the monthly statuses")
        _counted_metrics(row, path, pnl_field="pnl_usd", with_wins=True)
        for name in ("trades", "wins"):
            if row[name] != sum(m[name] for m in group):
                _fail(f"{path}.{name}", "does not reconcile with monthly rows")
        # At most twelve independently cent-rounded months plus one year cell.
        _near(_decimal(row["pnl_usd"]), sum((_decimal(m["pnl_usd"]) for m in group), Decimal(0)),
              "0.07", f"{path}.pnl_usd")
        yearly_total += _decimal(row["pnl_usd"])

    sides = _rows(s["sides"], "sides")
    if len(sides) != 2:
        _fail("sides", "must contain Long and Short")
    side_names: set[str] = set()
    for index, value in enumerate(sides):
        path = f"sides[{index}]"
        row = _record(value, path, {"side", "pnl_usd", "trades", "wins",
                                    "win_rate_pct", "profit_factor"})
        if row["side"] not in ("Long", "Short") or type(row["side"]) is not str:
            _fail(f"{path}.side", "must be Long or Short")
        if row["side"] in side_names:
            _fail(f"{path}.side", "duplicate side")
        side_names.add(row["side"])
        _counted_metrics(row, path, pnl_field="pnl_usd", with_wins=True)

    for name, rows in (("monthly", monthly), ("yearly", yearly), ("sides", sides)):
        for key, headline_key in (("trades", "trade_count"),):
            if sum(row[key] for row in rows) != headline[headline_key]:
                _fail(name, f"{key} do not reconcile with headline")
        if sum(row["wins"] for row in rows) != sum(m["wins"] for m in monthly):
            _fail(name, "wins do not reconcile with monthly rows")
    wins = sum(row["wins"] for row in monthly)
    if abs(headline["win_rate_pct"] - 100 * wins / headline["trade_count"]) > 0.050000001:
        _fail("headline.win_rate_pct", "does not reconcile with wins/trades")
    side_total = sum((_decimal(row["pnl_usd"]) for row in sides), Decimal(0))
    _near(yearly_total, monthly_total, "0.34", "yearly.pnl_usd")
    _near(side_total, monthly_total, "0.32", "sides.pnl_usd")
    _near(side_total, _decimal(headline["net_pnl_per_contract_usd"]), "0.51",
          "headline.net_pnl_per_contract_usd")

    _grid(s["execution"], "execution", {
        "fill_minutes": (1, 5, 15, 30), "slippage_ticks": (0.5, 1.0, 2.0),
    }, METRIC_FIELDS | {"fill_minutes", "slippage_ticks"})
    _grid(s["rr_sensitivity"], "rr_sensitivity", {
        "reward_risk": (0.5, 0.75, 1.0, 1.25, 1.5, 1.75, 2.0, 2.5, 3.0),
    }, METRIC_FIELDS | {"reward_risk"})
    surfaces = _record(s["parameter_surfaces"], "parameter_surfaces", {
        "reward_risk_x_filter_drop", "opening_range_x_reward_risk",
        "filter_drop_x_lookback",
    })
    _grid(surfaces["reward_risk_x_filter_drop"], "parameter_surfaces.reward_risk_x_filter_drop", {
        "reward_risk": (0.75, 1.0, 1.25, 1.5, 2.0),
        "filter_drop_pct": (0, 5, 10, 15, 20, 30),
    }, METRIC_FIELDS | {"reward_risk", "filter_drop_pct", "is_frozen"}, frozen=(1.0, 10))
    _grid(surfaces["opening_range_x_reward_risk"], "parameter_surfaces.opening_range_x_reward_risk", {
        "opening_range_minutes": (15, 30, 45, 60),
        "reward_risk": (0.75, 1.0, 1.25, 1.5),
    }, METRIC_FIELDS | {"opening_range_minutes", "reward_risk", "is_frozen"}, frozen=(30, 1.0))
    _grid(surfaces["filter_drop_x_lookback"], "parameter_surfaces.filter_drop_x_lookback", {
        "filter_drop_pct": (0, 5, 10, 15, 20, 25, 30),
        "lookback_days": (30, 40, 60, 90, 120),
    }, METRIC_FIELDS | {"filter_drop_pct", "lookback_days", "is_frozen"}, frozen=(10, 60))
    _grid(s["gate_sensitivity"], "gate_sensitivity", {
        "gate_kind": ("EMA", "SMA", "Off"),
        "gate_length": (0, 10, 20, 30, 50, 75, 100, 150, 200),
    }, METRIC_FIELDS | {"gate_kind", "gate_length", "is_frozen"}, frozen=("SMA", 50),
          expected_cells={(kind, length) for kind in ("EMA", "SMA")
                          for length in (10, 20, 30, 50, 75, 100, 150, 200)} | {("Off", 0)})
    _grid(s["entry_cutoff_sensitivity"], "entry_cutoff_sensitivity", {
        "entry_cutoff": ("10:30", "11:00", "12:00", "13:00", "14:30", "15:00", "16:00 (none)"),
    }, METRIC_FIELDS | {"entry_cutoff", "display_order", "is_frozen"}, frozen=("16:00 (none)",))
    for index, row in enumerate(s["entry_cutoff_sensitivity"]):
        _number(row["display_order"], f"entry_cutoff_sensitivity[{index}].display_order",
                integer=True, minimum=0, maximum=6)
        if row["display_order"] != index or row["entry_cutoff"] != (
            "10:30", "11:00", "12:00", "13:00", "14:30", "15:00", "16:00 (none)"
        )[index]:
            _fail(f"entry_cutoff_sensitivity[{index}]", "display order must match cutoff order")

    # The execution grid contains the published strategy baseline; the other
    # atlas views share a different frozen comparison cell with one another.
    execution_baseline = next((row for row in s["execution"]
                               if row["fill_minutes"] == headline["fill_resolution_minutes"]
                               and row["slippage_ticks"] == headline["modeled_slippage_ticks"]), None)
    if execution_baseline is None:
        _fail("headline", "declared execution baseline is absent from the grid")
    for field, headline_field in (("trades", "trade_count"),
                                  ("win_rate_pct", "win_rate_pct"),
                                  ("profit_factor", "profit_factor"),
                                  ("daily_sharpe", "daily_sharpe"),
                                  ("net_pnl_usd", "net_pnl_per_contract_usd")):
        if execution_baseline[field] != headline[headline_field]:
            _fail(f"execution baseline.{field}", "does not match headline")
    frozen_rows = [next(row for row in rows if row["is_frozen"]) for rows in (
        *surfaces.values(), s["gate_sensitivity"], s["entry_cutoff_sensitivity"]
    )]
    rr_baseline = next(row for row in s["rr_sensitivity"] if row["reward_risk"] == 1.0)
    for index, row in enumerate(frozen_rows):
        for field in METRIC_FIELDS:
            if row[field] != rr_baseline[field]:
                _fail(f"frozen atlas cell {index}.{field}",
                      "does not reconcile with reward:risk baseline")

    for name, fields in (("validation", {"test", "status", "evidence", "why_it_matters"}),
                         ("failed_ideas", {"idea", "result", "decision"}),
                         ("project_status", {"phase", "status", "objective", "evidence"})):
        for index, value in enumerate(_rows(s[name], name)):
            row = _record(value, f"{name}[{index}]", fields)
            for key in fields:
                _text(row[key], f"{name}[{index}].{key}")
    for index, value in enumerate(_rows(s["limitations"], "limitations")):
        _text(value, f"limitations[{index}]")
    return s
