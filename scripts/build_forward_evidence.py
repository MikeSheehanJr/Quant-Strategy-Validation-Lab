#!/usr/bin/env python3
"""Publish reviewed month aggregates from a private reconciliation input.

This is an offline publisher, not a trade ingester or paper execution system.
The private input must stay outside the public repository.
"""

from __future__ import annotations

import argparse
import copy
import json
import sys
from datetime import date, datetime
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.forward import validate_forward_status, validate_forward_transition
from src.forward_records import validate_public_monthly_records


INPUT_KEYS = {"schema_version", "candidate_id", "source_sha256", "settings_sha256",
              "calendar_sha256", "protocol_sha256", "months"}


def build_forward_evidence(
    private: dict[str, Any], public: dict[str, Any], as_of: date,
) -> dict[str, Any]:
    """Return a public status with complete revision history and no private fields."""

    if set(private) != INPUT_KEYS or private.get("schema_version") != "1.0.0":
        raise ValueError("Private reconciliation input schema mismatch")
    if public["status"] not in {"ready", "collecting", "under_review"}:
        raise ValueError("Candidate is not ready for aggregate publication")
    candidate = public["candidate"]
    expected = {"candidate_id": candidate["id"], "source_sha256": candidate["source_sha256"],
                "settings_sha256": candidate["settings_sha256"],
                "calendar_sha256": candidate["calendar"]["sha256"],
                "protocol_sha256": public["protocol"]["sha256"]}
    if any(private[key] != value for key, value in expected.items()):
        raise ValueError("Private input identity or protocol hash mismatch")
    validate_forward_status(public, as_of=as_of)
    if not isinstance(private["months"], list):
        raise ValueError("Private months must be a list")
    old = public["evidence"]["monthly_records"]
    records = copy.deepcopy(private["months"])
    if records[:len(old)] != old:
        raise ValueError("Previously published revisions may not be changed or removed")
    summary = validate_public_monthly_records(records, candidate, public["protocol"], as_of)
    result = copy.deepcopy(public)
    result["evidence"].update({key: summary[key] for key in
                               ("public_observation_count", "complete_months", "resolved_trades",
                                "unresolved_opportunities")})
    result["evidence"]["monthly_records"] = records
    result["evidence"]["conclusion"] = "No forward-performance conclusion."
    result["status"] = "under_review" if summary["review_ready"] else "collecting"
    result["last_updated"] = as_of.isoformat()
    validate_forward_status(result, as_of=as_of)
    validate_forward_transition(public, result, as_of=as_of)
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--private-input", type=Path, required=True)
    parser.add_argument("--public-status", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--as-of", type=date.fromisoformat,
                        default=datetime.now(ZoneInfo("America/New_York")).date())
    args = parser.parse_args()
    if args.as_of > datetime.now(ZoneInfo("America/New_York")).date():
        raise ValueError("Publisher as-of date cannot be in the future")
    private = json.loads(args.private_input.read_text(encoding="utf-8"))
    public = json.loads(args.public_status.read_text(encoding="utf-8"))
    result = build_forward_evidence(private, public, args.as_of)
    args.output.write_text(json.dumps(result, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
