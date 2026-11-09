from __future__ import annotations

from copy import deepcopy
from datetime import date

import pytest

from src.forward import (canonical_sha256, load_forward_status,
                         validate_forward_status, validate_forward_transition)


def ready_fixture() -> dict:
    status = deepcopy(load_forward_status())
    candidate = status["candidate"]
    candidate["settings_sha256"] = canonical_sha256(candidate["settings"])
    candidate["calendar"] = {"source": "https://www.cmegroup.com/trading-hours.html", "sha256": "a" * 64,
                             "verified_at": "2026-12-01"}
    candidate["freeze_date"] = "2026-12-01"
    candidate["ready_registered_at"] = "2026-12-01"
    candidate["collection_start"] = "2027-01-01"
    status["acceptance"]["status"] = "passed"
    for case in status["acceptance"]["cases"]:
        case.update(status="passed", evidence_ref="b" * 64)
    status["status"] = "ready"
    status["last_updated"] = "2026-12-01"
    return status


def test_current_status_is_unready_and_has_no_forward_performance():
    status = load_forward_status()
    assert status["status"] == "not_ready"
    assert status["candidate"]["freeze_date"] is None
    assert status["candidate"]["calendar"]["sha256"] is None
    assert status["evidence"]["public_observation_count"] == 0
    assert status["evidence"]["monthly_records"] == []
    assert status["evidence"]["conclusion"] == "No forward-performance conclusion."
    assert status["candidate_history"][0]["version"] == "v4.1"


def test_protocol_hash_and_source_identity_are_enforced():
    status = deepcopy(load_forward_status())
    status["protocol"]["first_review_resolved_trades"] = 59
    with pytest.raises(ValueError, match="hash mismatch"):
        validate_forward_status(status)
    status = deepcopy(load_forward_status())
    status["candidate"]["source_sha256"] = "0" * 64
    with pytest.raises(ValueError, match="source"):
        validate_forward_status(status)


def test_readiness_cannot_be_backdated_or_incomplete():
    status = ready_fixture()
    assert validate_forward_status(status, as_of=date(2026, 12, 1))
    original = deepcopy(load_forward_status())
    with pytest.raises(ValueError, match="prospectively"):
        validate_forward_transition(original, status, as_of=date(2026, 12, 2))
    status["candidate"]["calendar"]["verified_at"] = "2026-12-02"
    with pytest.raises(ValueError, match="frozen"):
        validate_forward_status(status, as_of=date(2026, 12, 2))
    status = ready_fixture()
    status["acceptance"]["cases"][0]["status"] = "pending"
    with pytest.raises(ValueError, match="readiness"):
        validate_forward_status(status, as_of=date(2026, 12, 1))
    status = ready_fixture()
    status["acceptance"]["cases"][0]["id"] = "invented_case"
    with pytest.raises(ValueError, match="required TradingView"):
        validate_forward_status(status, as_of=date(2026, 12, 1))
    status = ready_fixture()
    status["candidate"]["calendar"]["source"] = "private-calendar"
    with pytest.raises(ValueError, match="readiness"):
        validate_forward_status(status, as_of=date(2026, 12, 1))


def test_invalid_state_and_candidate_replacement_are_rejected():
    status = deepcopy(load_forward_status())
    status["status"] = "completed"
    with pytest.raises(ValueError, match="readiness"):
        validate_forward_status(status)
    previous = ready_fixture()
    current = deepcopy(previous)
    current["candidate"]["id"] = "replacement"
    current["status"] = "not_ready"
    current["candidate"]["settings_sha256"] = None
    current["candidate"]["calendar"] = {"source": None, "sha256": None, "verified_at": None}
    current["candidate"]["freeze_date"] = None
    current["candidate"]["ready_registered_at"] = None
    current["candidate"]["collection_start"] = None
    with pytest.raises(ValueError):
        validate_forward_transition(previous, current, as_of=date(2026, 12, 1))
