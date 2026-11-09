from __future__ import annotations

from copy import deepcopy
from datetime import date

import pytest

from scripts.build_forward_evidence import build_forward_evidence
from src.forward import CONCLUSIONS, validate_forward_status
from tests.test_forward_validation import ready_fixture


def month(name: str, r: float = 2.0, *, unresolved: int = 0, revision: int = 1) -> dict:
    return {"month": name, "revision": revision,
            "supersedes_revision": revision - 1 if revision > 1 else None,
            "revision_reason": "correction" if revision > 1 else "original",
            "eligible_sessions": 20 + unresolved, "opportunities_detected": 20 + unresolved,
            "resolved_trades": 20, "no_trade_decisions": 0,
            "unresolved_opportunities": unresolved, "negative_trades": 9,
            "tracking_errors": 0, "net_pnl_r": r,
            "within_month_max_drawdown_r": 3.0}


def private_input(status: dict, months: list[dict]) -> dict:
    c = status["candidate"]
    return {"schema_version": "1.0.0", "candidate_id": c["id"],
            "source_sha256": c["source_sha256"],
            "settings_sha256": c["settings_sha256"],
            "calendar_sha256": c["calendar"]["sha256"],
            "protocol_sha256": status["protocol"]["sha256"], "months": months}


def test_closed_months_reach_review_after_three_months_and_sixty_trades():
    ready = ready_fixture()
    rows = [month("2027-01"), month("2027-02", -3.0), month("2027-03")]
    published = build_forward_evidence(private_input(ready, rows), ready, date(2027, 4, 1))
    assert published["status"] == "under_review"
    assert published["evidence"]["resolved_trades"] == 60
    assert published["evidence"]["complete_months"] == 3
    assert published["evidence"]["monthly_records"][1]["net_pnl_r"] == -3.0
    assert published["evidence"]["conclusion"] == "No forward-performance conclusion."


def test_future_month_unresolved_and_private_field_fail_closed():
    ready = ready_fixture()
    base = [month("2027-01"), month("2027-02"), month("2027-03")]
    with pytest.raises(ValueError, match="Future|still-open"):
        build_forward_evidence(private_input(ready, base), ready, date(2027, 3, 31))
    base[2]["unresolved_opportunities"] = 1
    base[2]["opportunities_detected"] = 21
    base[2]["eligible_sessions"] = 21
    published = build_forward_evidence(private_input(ready, base), ready, date(2027, 4, 1))
    assert published["status"] == "collecting"
    base[0]["entry_price"] = 123.0
    with pytest.raises(ValueError, match="private fields"):
        build_forward_evidence(private_input(ready, base), ready, date(2027, 4, 1))


def test_corrections_append_after_later_month_and_preserve_negative_original():
    ready = ready_fixture()
    original = [month("2027-01", -5), month("2027-02", 2)]
    first = build_forward_evidence(private_input(ready, original), ready, date(2027, 3, 1))
    correction = month("2027-01", -4, revision=2)
    appended = original + [correction]
    second = build_forward_evidence(private_input(first, appended), first, date(2027, 3, 2))
    assert second["evidence"]["monthly_records"] == appended
    assert second["evidence"]["monthly_records"][0]["net_pnl_r"] == -5
    changed = deepcopy(appended)
    changed[0]["net_pnl_r"] = 5
    with pytest.raises(ValueError, match="changed or removed"):
        build_forward_evidence(private_input(first, changed), first, date(2027, 3, 2))


@pytest.mark.parametrize("net,decision", [(3, "supports_further_research"),
                                           (0, "does_not_support"),
                                           (-3, "does_not_support")])
def test_review_decision_is_deterministic(net: float, decision: str):
    ready = ready_fixture()
    rows = [month("2027-01", net), month("2027-02", 0), month("2027-03", 0)]
    status = build_forward_evidence(private_input(ready, rows), ready, date(2027, 4, 1))
    status["status"] = "completed"
    status["evidence"]["review"] = {"decision": decision, "reviewed_at": "2027-04-01"}
    status["evidence"]["conclusion"] = CONCLUSIONS[decision]
    validate_forward_status(status, as_of=date(2027, 4, 1))
    status["evidence"]["review"]["decision"] = (
        "does_not_support" if decision == "supports_further_research" else "supports_further_research"
    )
    with pytest.raises(ValueError, match="registered rule"):
        validate_forward_status(status, as_of=date(2027, 4, 1))


def test_mismatched_hash_and_opportunity_accounting_fail():
    ready = ready_fixture()
    rows = [month("2027-01")]
    source = private_input(ready, rows)
    source["protocol_sha256"] = "0" * 64
    with pytest.raises(ValueError, match="hash mismatch"):
        build_forward_evidence(source, ready, date(2027, 2, 1))
    source = private_input(ready, rows)
    rows[0]["opportunities_detected"] = 19
    with pytest.raises(ValueError, match="accounted for"):
        build_forward_evidence(source, ready, date(2027, 2, 1))


def test_tracking_error_in_earlier_revision_keeps_checkpoint_inconclusive():
    ready = ready_fixture()
    rows = [month("2027-01"), month("2027-02"), month("2027-03")]
    rows[0]["tracking_errors"] = 1
    rows.append(month("2027-01", revision=2))
    status = build_forward_evidence(private_input(ready, rows), ready, date(2027, 4, 1))
    status["status"] = "inconclusive"
    status["evidence"]["review"] = {"decision": "inconclusive", "reviewed_at": "2027-04-01"}
    status["evidence"]["conclusion"] = CONCLUSIONS["inconclusive"]
    validate_forward_status(status, as_of=date(2027, 4, 1))
