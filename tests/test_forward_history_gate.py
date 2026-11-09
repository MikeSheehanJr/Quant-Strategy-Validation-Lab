from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

from scripts.check_forward_transition import check_transition_records, choose_base_ref

ROOT = Path(__file__).resolve().parents[1]


def current_status():
    return json.loads((ROOT / "data/forward_validation.json").read_text())


def legacy_status(current):
    archive = current["candidate_history"][0]
    return {
        "schema_version": "1.0.0", "status": "not_started",
        "candidate": {key: archive[key] for key in ("version", "source_sha256", "freeze_date")},
        "evidence": {"public_observation_count": 0, "complete_months": 0},
    }


def test_zero_observation_legacy_migration_preserves_source_identity():
    current = current_status()
    check_transition_records(legacy_status(current), current)


def test_legacy_migration_cannot_erase_observations():
    current = current_status()
    previous = legacy_status(current)
    previous["evidence"]["public_observation_count"] = 1
    with pytest.raises(ValueError, match="unobserved"):
        check_transition_records(previous, current)


def test_legacy_migration_cannot_replace_archived_source():
    current = current_status()
    previous = legacy_status(current)
    previous["candidate"]["source_sha256"] = "0" * 64
    with pytest.raises(ValueError, match="source identity"):
        check_transition_records(previous, current)


def test_v2_publication_checks_prior_history_instead_of_only_current_shape():
    previous = current_status()
    current = copy.deepcopy(previous)
    current["candidate_history"][0]["note"] = "Rewritten archive"
    with pytest.raises(ValueError, match="Archived candidate history"):
        check_transition_records(previous, current)


@pytest.mark.parametrize("reference", ["0" * 40, "--unsafe-option", "HEAD:file", "bad ref"])
def test_invalid_or_missing_trusted_baseline_cannot_silently_skip_history(reference):
    with pytest.raises(ValueError, match="baseline ref"):
        choose_base_ref(reference)
