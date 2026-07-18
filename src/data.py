"""Load the checked-in, aggregate-only research snapshot."""

from __future__ import annotations

import hashlib
import json
from functools import lru_cache
from pathlib import Path
from typing import Any

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SNAPSHOT = PROJECT_ROOT / "data" / "public_snapshot.json"


@lru_cache(maxsize=2)
def load_snapshot(path: str | Path = DEFAULT_SNAPSHOT) -> dict[str, Any]:
    """Return a validated aggregate research snapshot.

    The app intentionally reads only a small JSON artifact. Raw intraday bars
    and trade-level records are outside this project's public boundary.
    """

    snapshot_path = Path(path)
    with snapshot_path.open(encoding="utf-8") as handle:
        snapshot: dict[str, Any] = json.load(handle)

    required = {
        "meta",
        "headline",
        "monthly",
        "yearly",
        "sides",
        "execution",
        "rr_sensitivity",
        "parameter_surfaces",
        "gate_sensitivity",
        "entry_cutoff_sensitivity",
        "validation",
        "failed_ideas",
        "project_status",
        "limitations",
    }
    missing = required.difference(snapshot)
    if missing:
        raise ValueError(f"Snapshot is missing required sections: {sorted(missing)}")
    if snapshot["meta"].get("raw_market_data_included") is not False:
        raise ValueError("Public snapshot must explicitly exclude raw market data")
    return snapshot


def snapshot_sha256(path: str | Path = DEFAULT_SNAPSHOT) -> str:
    """Return a short content digest for visible provenance."""

    digest = hashlib.sha256(Path(path).read_bytes()).hexdigest()
    return digest[:12]


def monthly_frame(snapshot: dict[str, Any]) -> pd.DataFrame:
    frame = pd.DataFrame(snapshot["monthly"])
    frame["month"] = pd.to_datetime(frame["month"], format="%Y-%m")
    return frame


def yearly_frame(snapshot: dict[str, Any]) -> pd.DataFrame:
    return pd.DataFrame(snapshot["yearly"])


def execution_frame(snapshot: dict[str, Any]) -> pd.DataFrame:
    return pd.DataFrame(snapshot["execution"])


def rr_frame(snapshot: dict[str, Any]) -> pd.DataFrame:
    return pd.DataFrame(snapshot["rr_sensitivity"])


def parameter_surface_frame(snapshot: dict[str, Any], surface: str) -> pd.DataFrame:
    """Return one reviewed parameter surface from the aggregate snapshot."""

    surfaces = snapshot["parameter_surfaces"]
    if surface not in surfaces:
        raise KeyError(f"Unknown parameter surface: {surface}")
    return pd.DataFrame(surfaces[surface])


def gate_frame(snapshot: dict[str, Any]) -> pd.DataFrame:
    return pd.DataFrame(snapshot["gate_sensitivity"])


def entry_cutoff_frame(snapshot: dict[str, Any]) -> pd.DataFrame:
    return pd.DataFrame(snapshot["entry_cutoff_sensitivity"])
