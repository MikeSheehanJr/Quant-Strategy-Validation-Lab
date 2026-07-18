from __future__ import annotations

from src.forward import load_forward_status


def test_forward_status_is_claim_limited_and_not_started():
    status = load_forward_status()
    assert status["status"] == "not_started"
    assert status["evidence"]["public_observation_count"] == 0
    assert status["evidence"]["complete_months"] == 0
    assert status["public_reporting"]["live_signals"] is False
    assert status["public_reporting"]["trade_level_records"] is False
    assert status["evidence"]["conclusion"] == "No forward-performance conclusion."


def test_forward_candidate_is_hash_pinned():
    status = load_forward_status()
    assert status["candidate"]["version"] == "v4.1"
    assert len(status["candidate"]["source_sha256"]) == 64
