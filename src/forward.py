"""Load the machine-readable status of the public forward-validation track."""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any

from src.pinescript import load_pinescript_manifest


PROJECT_ROOT = Path(__file__).resolve().parents[1]
FORWARD_STATUS_PATH = PROJECT_ROOT / "data" / "forward_validation.json"


@lru_cache(maxsize=1)
def load_forward_status() -> dict[str, Any]:
    """Return a validated, claim-limited forward-validation status record."""

    status = json.loads(FORWARD_STATUS_PATH.read_text(encoding="utf-8"))
    required = {
        "schema_version",
        "status",
        "last_updated",
        "candidate",
        "public_reporting",
        "evidence",
        "next_gate",
    }
    missing = required.difference(status)
    if missing:
        raise ValueError(f"Forward status is missing required sections: {sorted(missing)}")

    evidence = status["evidence"]
    if status["status"] == "not_started":
        if evidence.get("public_observation_count") != 0:
            raise ValueError("A not-started forward track cannot report observations")
        if evidence.get("complete_months") != 0:
            raise ValueError("A not-started forward track cannot report complete months")

    reporting = status["public_reporting"]
    if reporting.get("live_signals") is not False:
        raise ValueError("The public forward track must exclude live signals")
    if reporting.get("trade_level_records") is not False:
        raise ValueError("The public forward track must exclude trade-level records")

    manifest = load_pinescript_manifest()
    current = next(version for version in manifest["versions"] if version["current"])
    candidate = status["candidate"]
    if candidate.get("version") != current["version"]:
        raise ValueError("Forward candidate version does not match the current Pine build")
    if candidate.get("source_sha256") != current["sha256"]:
        raise ValueError("Forward candidate hash does not match the current Pine source")

    return status
