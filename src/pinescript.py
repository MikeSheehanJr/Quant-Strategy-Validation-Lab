"""Load and validate the public Pine Script evolution evidence."""

from __future__ import annotations

import hashlib
import json
from functools import lru_cache
from pathlib import Path
from typing import Any

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
PINE_ROOT = PROJECT_ROOT / "pinescript"
MANIFEST_PATH = PINE_ROOT / "manifest.json"
BACKTEST_ROOT = PROJECT_ROOT / "data" / "backtests"
BACKTEST_FILES = {
    "monthly": BACKTEST_ROOT / "orb_sym_v4_1_mnq_monthly.csv",
    "windows": BACKTEST_ROOT / "orb_sym_v4_1_mnq_windows.csv",
    "qa": BACKTEST_ROOT / "orb_sym_v4_1_mnq_qa.csv",
}


@lru_cache(maxsize=1)
def load_pinescript_manifest() -> dict[str, Any]:
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    versions = manifest.get("versions")
    if not isinstance(versions, list) or len(versions) < 2:
        raise ValueError("Pine Script manifest must contain at least two versions")
    if sum(bool(version.get("current")) for version in versions) != 1:
        raise ValueError("Pine Script manifest must mark exactly one current version")

    seen: set[str] = set()
    for version in versions:
        version_id = str(version["version"])
        if version_id in seen:
            raise ValueError(f"Duplicate Pine Script version: {version_id}")
        seen.add(version_id)
        source_path = PINE_ROOT / version["file"]
        source = source_path.read_bytes()
        if hashlib.sha256(source).hexdigest() != version["sha256"]:
            raise ValueError(f"Pine Script hash mismatch: {version_id}")
        line_count = len(source.decode("utf-8").splitlines())
        if line_count != version["line_count"]:
            raise ValueError(f"Pine Script line-count mismatch: {version_id}")
    return manifest


def pinescript_versions_frame(manifest: dict[str, Any]) -> pd.DataFrame:
    frame = pd.DataFrame(manifest["versions"])[
        ["version", "research_date", "title", "change", "evidence_status"]
    ]
    frame["research_date"] = pd.to_datetime(frame["research_date"], format="%Y-%m-%d")
    return frame


def pinescript_source(version: dict[str, Any]) -> str:
    return (PINE_ROOT / version["file"]).read_text(encoding="utf-8")


def pinescript_excerpt(version: dict[str, Any]) -> str:
    lines = pinescript_source(version).splitlines()
    start = int(version["excerpt_start"]) - 1
    end = int(version["excerpt_end"])
    return "\n".join(lines[start:end])


@lru_cache(maxsize=1)
def load_pinescript_backtests() -> dict[str, pd.DataFrame]:
    frames = {name: pd.read_csv(path) for name, path in BACKTEST_FILES.items()}
    monthly = frames["monthly"]
    monthly["month"] = pd.to_datetime(monthly["month"], format="%Y-%m")
    return frames


def evidence_bytes(name: str) -> bytes:
    if name not in BACKTEST_FILES:
        raise KeyError(f"Unknown Pine Script evidence file: {name}")
    return BACKTEST_FILES[name].read_bytes()
