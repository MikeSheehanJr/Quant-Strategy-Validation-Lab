#!/usr/bin/env python3
"""Compare forward evidence with a trusted Git baseline before publication."""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import re
import subprocess
import sys
from datetime import date

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.forward import validate_forward_status, validate_forward_transition

STATUS_PATH = "data/forward_validation.json"


def check_transition_records(previous: dict, current: dict, as_of: date | None = None) -> None:
    """Allow the zero-observation legacy migration, otherwise check transitions."""
    validate_forward_status(current, as_of=as_of)
    if previous.get("schema_version") == "1.0.0":
        evidence = previous.get("evidence", {})
        if (previous.get("status") != "not_started"
                or evidence.get("public_observation_count") != 0
                or evidence.get("complete_months") != 0
                or current["status"] != "not_ready"
                or current["evidence"]["monthly_records"]):
            raise ValueError("Legacy migration requires an unobserved, not-ready track")
        old = previous["candidate"]
        archived = [item for item in current["candidate_history"]
                    if item.get("version") == old.get("version")
                    and item.get("source_sha256") == old.get("source_sha256")
                    and item.get("freeze_date") == old.get("freeze_date")
                    and item.get("public_observation_count") == 0]
        if not archived:
            raise ValueError("Legacy source identity must be retained in candidate history")
        return
    validate_forward_transition(previous, current, as_of=as_of)


def _git(*arguments: str) -> str:
    return subprocess.run(["git", *arguments], cwd=ROOT, check=True,
                          capture_output=True, text=True).stdout


def choose_base_ref(explicit: str | None = None) -> str:
    """CI supplies the PR base/push-before SHA; local work uses HEAD or its parent."""
    ref = explicit or os.environ.get("FORWARD_BASE_REF")
    if ref:
        if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._/~^\-]*", ref) or set(ref) == {"0"}:
            raise ValueError("Invalid or unavailable forward baseline ref")
        return ref
    committed = _git("show", f"HEAD:{STATUS_PATH}")
    working = (ROOT / STATUS_PATH).read_text(encoding="utf-8")
    return "HEAD" if committed != working else "HEAD^"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-ref", help="Trusted prior commit or branch; CI supplies this")
    args = parser.parse_args()
    try:
        ref = choose_base_ref(args.base_ref)
        previous = json.loads(_git("show", f"{ref}:{STATUS_PATH}"))
        current = json.loads((ROOT / STATUS_PATH).read_text(encoding="utf-8"))
        check_transition_records(previous, current)
    except (OSError, ValueError, KeyError, subprocess.CalledProcessError) as exc:
        print(f"Forward history gate FAILED: {exc}", file=sys.stderr)
        return 1
    print("Forward history gate PASSED: prior identity and evidence preserved.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
