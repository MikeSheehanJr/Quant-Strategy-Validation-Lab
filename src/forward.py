"""Validate the public, aggregate-only prospective paper protocol."""

from __future__ import annotations

import hashlib
import json
import re
from datetime import date, datetime
from functools import lru_cache
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

from src.pinescript import load_pinescript_manifest


PROJECT_ROOT = Path(__file__).resolve().parents[1]
FORWARD_STATUS_PATH = PROJECT_ROOT / "data" / "forward_validation.json"
STATES = {"not_ready", "ready", "collecting", "under_review", "inconclusive", "completed"}
DECISIONS = {"supports_further_research", "does_not_support", "inconclusive"}
CONCLUSIONS = {
    "supports_further_research": "The descriptive paper checkpoint supports further research; it does not establish alpha or expected returns.",
    "does_not_support": "The descriptive paper checkpoint does not support the candidate.",
    "inconclusive": "The descriptive paper checkpoint is inconclusive because tracking errors were recorded.",
}
ACCEPTANCE_IDS = {"wrong_symbol", "wrong_timeframe", "rth_eth_missing_post_session_bar",
                  "early_close", "opening_range_missing", "entry_exit", "brackets",
                  "fees", "sizing", "alerts"}
SHA256 = re.compile(r"[0-9a-f]{64}\Z")


def canonical_sha256(value: Any) -> str:
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return hashlib.sha256(encoded.encode("ascii")).hexdigest()


def _hash_ok(value: Any) -> bool:
    return isinstance(value, str) and SHA256.fullmatch(value) is not None


def _date(value: Any, field: str) -> date:
    try:
        return date.fromisoformat(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"Invalid {field} date") from exc


def _reviewed_gates(candidate: dict[str, Any], acceptance: dict[str, Any]) -> bool:
    calendar = candidate["calendar"]
    cases = acceptance["cases"]
    return (
        _hash_ok(candidate.get("settings_sha256"))
        and candidate["settings_sha256"] == canonical_sha256(candidate["settings"])
        and bool(candidate.get("freeze_date"))
        and bool(candidate.get("collection_start"))
        and isinstance(calendar.get("source"), str)
        and calendar["source"].startswith("https://www.cmegroup.com/")
        and not any(char.isspace() for char in calendar["source"])
        and _hash_ok(calendar.get("sha256"))
        and bool(calendar.get("verified_at"))
        and bool(candidate.get("ready_registered_at"))
        and acceptance.get("status") == "passed"
        and bool(cases)
        and all(case.get("status") == "passed" and _hash_ok(case.get("evidence_ref")) for case in cases)
    )


def validate_forward_status(status: dict[str, Any], manifest: dict[str, Any] | None = None,
                            as_of: date | None = None) -> dict[str, Any]:
    """Fail closed on identity, readiness, state, and evidence inconsistencies."""

    required = {"schema_version", "status", "last_updated", "candidate", "candidate_history",
                "protocol", "protocol_history", "acceptance", "public_reporting", "evidence", "next_gate"}
    if required.difference(status):
        raise ValueError(f"Forward status is missing sections: {sorted(required.difference(status))}")
    if status["schema_version"] != "2.0.0" or status["status"] not in STATES:
        raise ValueError("Unsupported forward schema or state")
    today = as_of or datetime.now(ZoneInfo("America/New_York")).date()
    updated = _date(status["last_updated"], "last_updated")
    if updated > today:
        raise ValueError("Forward status cannot be dated in the future")
    reporting = status["public_reporting"]
    if set(reporting) != {"cadence", "minimum_delay", "granularity", "live_signals", "trade_level_records"}:
        raise ValueError("Forward reporting has unreviewed fields")
    if (reporting.get("live_signals") is not False
            or reporting.get("trade_level_records") is not False
            or reporting.get("granularity") != "aggregate monthly"):
        raise ValueError("Forward reporting must remain delayed, aggregate-only, and non-live")

    manifest = manifest or load_pinescript_manifest()
    versions = {item["version"]: item for item in manifest["versions"]}
    candidate = status["candidate"]
    if set(candidate["calendar"]) != {"source", "sha256", "verified_at"}:
        raise ValueError("Calendar has unreviewed fields")
    history = status["candidate_history"]
    if not isinstance(history, list) or not history or candidate.get("id") in {item.get("id") for item in history}:
        raise ValueError("Current candidate needs a distinct identity and archived history")
    for item in [*history, candidate]:
        if item.get("version") not in versions or item.get("source_sha256") != versions[item["version"]]["sha256"]:
            raise ValueError("Forward candidate source does not match the pinned Pine manifest")
    if any(item.get("status") != "archived" for item in history):
        raise ValueError("Historical candidates must remain archived")
    if any(not isinstance(item.get("monthly_records"), list) for item in history):
        raise ValueError("Archived candidate record history is required")

    protocol = status["protocol"]
    if protocol.get("sha256") != canonical_sha256({k: v for k, v in protocol.items() if k != "sha256"}):
        raise ValueError("Forward protocol hash mismatch")
    if not isinstance(status["protocol_history"], list) or any(
        item.get("sha256") != canonical_sha256({k: v for k, v in item.items() if k != "sha256"})
        for item in status["protocol_history"]
    ):
        raise ValueError("Archived protocol record mismatch")
    if (protocol.get("first_review_complete_months") != 3
            or protocol.get("first_review_resolved_trades") != 60
            or protocol.get("max_unresolved_for_conclusion") != 0):
        raise ValueError("Minimum sample or unresolved-event gate changed")
    if protocol.get("decision_policy") != {
        "tracking_errors_present": "inconclusive",
        "positive_total_net_r": "supports_further_research",
        "nonpositive_total_net_r": "does_not_support",
    }:
        raise ValueError("Registered decision policy changed")
    cases = status["acceptance"].get("cases")
    if set(status["acceptance"]) != {"status", "cases"}:
        raise ValueError("Acceptance has unreviewed fields")
    if not isinstance(cases, list) or {c.get("id") for c in cases} != ACCEPTANCE_IDS or len(cases) != len(ACCEPTANCE_IDS):
        raise ValueError("All required TradingView acceptance cases are required")
    if any(set(case) != {"id", "status", "evidence_ref"} for case in cases):
        raise ValueError("Acceptance cases cannot contain private or unreviewed fields")
    if any(case.get("status") not in {"pending", "passed", "failed"} for case in cases):
        raise ValueError("Invalid TradingView acceptance case state")

    evidence = status["evidence"]
    if set(evidence) != {"public_observation_count", "complete_months", "resolved_trades",
                         "unresolved_opportunities", "monthly_records", "conclusion", "review"}:
        raise ValueError("Forward evidence has unreviewed fields")
    records = evidence.get("monthly_records")
    if not isinstance(records, list):
        raise ValueError("Forward monthly records must be a list")
    from src.forward_records import validate_public_monthly_records
    summary = validate_public_monthly_records(records, candidate, protocol, updated)
    for key in ("public_observation_count", "complete_months", "resolved_trades", "unresolved_opportunities"):
        if evidence.get(key) != summary[key]:
            raise ValueError(f"Forward evidence {key} does not reconcile")

    ready = _reviewed_gates(candidate, status["acceptance"])
    if ready:
        registered = _date(candidate["registered_at"], "registered_at")
        verified = _date(candidate["calendar"]["verified_at"], "calendar verified_at")
        frozen = _date(candidate["freeze_date"], "freeze_date")
        ready_at = _date(candidate["ready_registered_at"], "ready_registered_at")
        start = _date(candidate["collection_start"], "collection_start")
        if not (registered <= verified <= frozen <= ready_at <= updated and ready_at < start):
            raise ValueError("Settings must be frozen before a future first-of-month start")
        if start.day != 1:
            raise ValueError("Settings must be frozen before a future first-of-month start")
        if status["status"] not in {"ready", "not_ready"} and start > updated:
            raise ValueError("Collection cannot predate the frozen start")
    no_conclusion = evidence.get("conclusion") == "No forward-performance conclusion."
    if status["status"] == "not_ready":
        if ready or records or not no_conclusion or evidence["review"] is not None:
            raise ValueError("Not-ready track cannot contain observations or a conclusion")
    elif not ready:
        raise ValueError("Collection or review requires all actual readiness gates")
    elif status["status"] == "ready":
        if records or not no_conclusion or evidence["review"] is not None:
            raise ValueError("Ready track cannot contain observations or a conclusion")
    elif status["status"] == "collecting":
        if not records or summary["review_ready"] or not no_conclusion or evidence["review"] is not None:
            raise ValueError("Collecting state has inconsistent evidence")
    elif status["status"] == "under_review":
        if not summary["review_ready"] or not no_conclusion or evidence["review"] is not None:
            raise ValueError("Under-review state requires a complete sample but no conclusion")
    else:
        review = evidence.get("review")
        if not summary["review_ready"] or not isinstance(review, dict) or set(review) != {"decision", "reviewed_at"}:
            raise ValueError("Conclusion requires a complete reconciled sample and review")
        decision = review.get("decision")
        if decision not in DECISIONS or not review.get("reviewed_at"):
            raise ValueError("Conclusion requires a dated, registered decision")
        expected_decision = ("inconclusive" if summary["tracking_errors"] > 0 else
                             "supports_further_research" if summary["net_pnl_r"] > 0 else
                             "does_not_support")
        if decision != expected_decision:
            raise ValueError("Review decision disagrees with the registered rule")
        reviewed_at = _date(review["reviewed_at"], "reviewed_at")
        if reviewed_at > updated:
            raise ValueError("Review cannot be dated after the public update")
        if ((status["status"] == "inconclusive") != (decision == "inconclusive")
                or evidence.get("conclusion") != CONCLUSIONS[decision]):
            raise ValueError("Conclusion state, text, and review decision disagree")
    return status


def validate_forward_transition(previous: dict[str, Any], current: dict[str, Any],
                                as_of: date | None = None) -> None:
    """Prevent changed identities, erased revisions, or impossible state jumps."""

    validate_forward_status(previous, as_of=as_of)
    validate_forward_status(current, as_of=as_of)
    allowed = {
        "not_ready": {"not_ready", "ready"},
        "ready": {"ready", "collecting", "under_review"},
        "collecting": {"collecting", "under_review"},
        "under_review": {"under_review", "collecting", "inconclusive", "completed"},
        "inconclusive": {"inconclusive"},
        "completed": {"completed"},
    }
    new_candidate = current["candidate"]["id"] != previous["candidate"]["id"]
    if new_candidate:
        raise ValueError("New candidate registration requires a separately reviewed archive workflow")
    if current["status"] not in allowed[previous["status"]]:
        raise ValueError("Forward state transition is not allowed")
    if previous["status"] == "not_ready" and current["status"] == "ready":
        today = as_of or datetime.now(ZoneInfo("America/New_York")).date()
        if (current["candidate"]["ready_registered_at"] != today.isoformat()
                or current["last_updated"] != today.isoformat()
                or _date(current["candidate"]["collection_start"], "collection_start") <= today):
            raise ValueError("Readiness must be registered prospectively on the transition date")
    identity = ("id", "version", "source_sha256", "settings_sha256", "freeze_date",
                "ready_registered_at", "collection_start")
    if previous["status"] != "not_ready" and any(
        previous["candidate"].get(key) != current["candidate"].get(key) for key in identity
    ):
        raise ValueError("Frozen candidate identity or configuration changed")
    if previous["status"] != "not_ready" and previous["candidate"].get("calendar") != current["candidate"].get("calendar"):
        raise ValueError("Frozen calendar changed")
    if current["candidate_history"][:len(previous["candidate_history"])] != previous["candidate_history"]:
        raise ValueError("Archived candidate history changed or was removed")
    if current["protocol_history"][:len(previous["protocol_history"])] != previous["protocol_history"]:
        raise ValueError("Archived protocol history changed or was removed")
    if current["protocol"] != previous["protocol"]:
        raise ValueError("Protocol changed without new candidate")
    old_records = previous["evidence"]["monthly_records"]
    if current["evidence"]["monthly_records"][:len(old_records)] != old_records:
        raise ValueError("Published month revisions changed or were removed")


@lru_cache(maxsize=1)
def load_forward_status() -> dict[str, Any]:
    return validate_forward_status(json.loads(FORWARD_STATUS_PATH.read_text(encoding="utf-8")))
