#!/usr/bin/env python3
"""Fail closed when the public release contains unsafe or private artifacts."""

from __future__ import annotations

import ast
import csv
import json
import re
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
MAX_PUBLIC_FILE_BYTES = 1_500_000
TEXT_SUFFIXES = {
    ".csv",
    ".ini",
    ".json",
    ".md",
    ".pine",
    ".py",
    ".toml",
    ".txt",
    ".yaml",
    ".yml",
}
ALLOWED_SUFFIXES = TEXT_SUFFIXES | {".png"}
ALLOWED_EXTENSIONLESS = {".gitignore", "LICENSE"}
FORBIDDEN_SUFFIXES = {
    ".db",
    ".feather",
    ".gz",
    ".h5",
    ".hdf5",
    ".ipynb",
    ".joblib",
    ".jpg",
    ".jpeg",
    ".key",
    ".p12",
    ".parquet",
    ".pem",
    ".pickle",
    ".pkl",
    ".sqlite",
    ".sqlite3",
    ".tar",
    ".webp",
    ".xls",
    ".xlsx",
    ".zip",
}
FORBIDDEN_FILENAMES = {
    ".netrc",
    ".npmrc",
    ".pypirc",
    "credentials.json",
    "id_ed25519",
    "id_rsa",
    "secrets.toml",
}
IGNORED_PARTS = {".git", ".venv", "__pycache__", ".pytest_cache", "output"}
RAW_SNAPSHOT_KEYS = {
    "account_id",
    "broker_account",
    "close",
    "email",
    "entry",
    "exit",
    "high",
    "low",
    "open",
    "phone",
    "stop",
    "target",
    "timestamp",
    "trade_day",
    "volume",
    "wallet",
}
ALLOWED_PUBLIC_DATA_FILES = {
    "data/public_snapshot.json",
    "data/forward_validation.json",
    "data/backtests/orb_sym_v4_1_mnq_monthly.csv",
    "data/backtests/orb_sym_v4_1_mnq_qa.csv",
    "data/backtests/orb_sym_v4_1_mnq_windows.csv",
}
BACKTEST_CSV_SCHEMAS = {
    "data/backtests/orb_sym_v4_1_mnq_monthly.csv": [
        "month",
        "trades",
        "winning_trades",
        "losing_trades",
        "win_rate_pct",
        "net_pnl_usd",
        "cumulative_pnl_usd",
        "gross_profit_usd",
        "gross_loss_usd",
        "profit_factor",
        "within_month_max_drawdown_usd",
    ],
    "data/backtests/orb_sym_v4_1_mnq_qa.csv": [
        "check",
        "status",
        "value",
        "interpretation",
    ],
    "data/backtests/orb_sym_v4_1_mnq_windows.csv": [
        "window",
        "start_month",
        "end_month",
        "trades",
        "net_pnl_usd",
        "mean_trade_usd",
        "win_rate_pct",
        "profit_factor",
        "max_drawdown_usd",
    ],
}
FORBIDDEN_RUNTIME_MODULES = {
    "ftplib",
    "httpx",
    "paramiko",
    "requests",
    "socket",
    "subprocess",
    "urllib",
}
FORBIDDEN_RUNTIME_SURFACES = {
    "st.camera_input": "camera input",
    "st.connection": "external connection",
    "st.file_uploader": "file upload",
    "st.secrets": "runtime secrets",
}
PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"
PNG_PRIVATE_CHUNKS = {b"eXIf", b"iTXt", b"tEXt", b"zTXt"}


def _secret_patterns() -> list[tuple[str, re.Pattern[str]]]:
    # Construct signature fragments so this scanner never flags its own source.
    return [
        ("GitHub token", re.compile("gh" + r"[pousr]_[A-Za-z0-9]{20,}")),
        ("GitLab token", re.compile("gl" + r"pat-[A-Za-z0-9_-]{20,}")),
        ("AWS access key", re.compile("AK" + r"IA[0-9A-Z]{16}")),
        ("Google API key", re.compile("AI" + r"za[0-9A-Za-z_-]{32,}")),
        ("Slack token", re.compile("xo" + r"x[baprs]-[A-Za-z0-9-]{20,}")),
        ("Stripe live key", re.compile("sk" + r"_live_[A-Za-z0-9]{16,}")),
        ("OpenAI-style key", re.compile("sk" + r"-(?:proj-)?[A-Za-z0-9_-]{20,}")),
        ("JWT", re.compile("ey" + r"J[A-Za-z0-9_-]{20,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}")),
        (
            "private key block",
            re.compile("BEGIN " + r"(?:RSA |EC |OPENSSH )?PRIVATE KEY"),
        ),
        (
            "assigned secret",
            re.compile(
                r"(?i)(api[_-]?key|access[_-]?token|client[_-]?secret|password)"
                r"\s*[:=]\s*['\"](?!\[|<|example|dummy|test|your_)[^'\"]{8,}['\"]"
            ),
        ),
        (
            "credential-bearing URL",
            re.compile(r"https?://[^/\s:@]+:[^/\s@]+@[^\s]+"),
        ),
    ]


EMAIL_PATTERN = re.compile(r"(?i)\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b")
LOCAL_PATH_PATTERNS = [
    re.compile(r"/Users/[^/\s]+"),
    re.compile(r"/home/(?!runner(?:/|\b))[^/\s]+"),
    re.compile(r"[A-Za-z]:\\Users\\"),
]


def _walk_keys(value):
    if isinstance(value, dict):
        for key, child in value.items():
            yield str(key)
            yield from _walk_keys(child)
    elif isinstance(value, list):
        for child in value:
            yield from _walk_keys(child)


def _text_problems(relative: Path, text: str) -> list[str]:
    problems: list[str] = []
    if any(pattern.search(text) for pattern in LOCAL_PATH_PATTERNS):
        problems.append(f"local machine path found: {relative}")
    emails = [match.group(0) for match in EMAIL_PATTERN.finditer(text)]
    private_emails = [email for email in emails if not email.lower().endswith("@example.com")]
    if private_emails:
        problems.append(f"email address found: {relative}")
    for label, pattern in _secret_patterns():
        if pattern.search(text):
            problems.append(f"possible {label}: {relative}")
    return problems


def _png_metadata_chunks(data: bytes) -> set[str]:
    if not data.startswith(PNG_SIGNATURE):
        return {"invalid-signature"}
    offset = len(PNG_SIGNATURE)
    private: set[str] = set()
    while offset + 12 <= len(data):
        length = int.from_bytes(data[offset : offset + 4], "big")
        kind = data[offset + 4 : offset + 8]
        end = offset + 12 + length
        if end > len(data):
            return private | {"malformed"}
        if kind in PNG_PRIVATE_CHUNKS:
            private.add(kind.decode("ascii"))
        offset = end
        if kind == b"IEND":
            return private
    return private | {"missing-IEND"}


def _runtime_surface_problems(root: Path) -> list[str]:
    problems: list[str] = []
    runtime_paths = [
        root / "streamlit_app.py",
        *sorted((root / "app_pages").glob("*.py")),
        *sorted((root / "src").glob("*.py")),
    ]
    for path in runtime_paths:
        relative = path.relative_to(root)
        source = path.read_text(encoding="utf-8")
        tree = ast.parse(source, filename=str(relative))
        imported: set[str] = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imported.update(alias.name.split(".")[0] for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                imported.add(node.module.split(".")[0])
        for module in sorted(imported.intersection(FORBIDDEN_RUNTIME_MODULES)):
            problems.append(f"network/process module in public runtime ({module}): {relative}")
        for token, label in FORBIDDEN_RUNTIME_SURFACES.items():
            if token in source:
                problems.append(f"{label} enabled in public runtime: {relative}")
    return problems


def _workflow_security_problems(root: Path) -> list[str]:
    problems: list[str] = []
    workflow_root = root / ".github" / "workflows"
    for path in sorted([*workflow_root.glob("*.yml"), *workflow_root.glob("*.yaml")]):
        relative = path.relative_to(root)
        text = path.read_text(encoding="utf-8")
        if not re.search(r"(?m)^permissions:\s*$", text):
            problems.append(f"workflow lacks explicit permissions: {relative}")
        for action, reference in re.findall(
            r"(?m)^\s*-\s*uses:\s*([^@\s]+)@([^\s#]+)", text
        ):
            if action.startswith("./"):
                continue
            if not re.fullmatch(r"[0-9a-f]{40}", reference):
                problems.append(f"GitHub Action is not commit-pinned: {relative} ({action})")
    return problems


def _snapshot_problems(root: Path) -> list[str]:
    problems: list[str] = []
    data_root = root / "data"
    data_files = {
        path.relative_to(root).as_posix()
        for path in data_root.rglob("*")
        if path.is_file()
    } if data_root.exists() else set()
    if data_files != ALLOWED_PUBLIC_DATA_FILES:
        problems.append(
            "public data directory differs from the aggregate-only allowlist: "
            f"{sorted(data_files)}"
        )

    snapshot_path = data_root / "public_snapshot.json"
    if not snapshot_path.exists():
        return problems + ["missing data/public_snapshot.json"]
    try:
        snapshot = json.loads(snapshot_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return problems + [f"invalid public snapshot JSON: {exc}"]

    present_raw_keys = RAW_SNAPSHOT_KEYS.intersection(_walk_keys(snapshot))
    if present_raw_keys:
        problems.append(f"raw/trade-level snapshot keys found: {sorted(present_raw_keys)}")
    meta = snapshot.get("meta", {})
    if meta.get("raw_market_data_included") is not False:
        problems.append("snapshot does not explicitly exclude raw market data")
    if meta.get("trade_level_records_included") is not False:
        problems.append("snapshot does not explicitly exclude trade-level records")
    granularity = str(meta.get("data_granularity", "")).lower()
    if "monthly" not in granularity or "aggregate" not in granularity:
        problems.append("snapshot granularity is not explicitly monthly and aggregate-only")
    hashes = meta.get("source_artifact_hashes")
    if not isinstance(hashes, dict) or not hashes:
        problems.append("snapshot source hashes are missing")
    elif any(not re.fullmatch(r"[0-9a-f]{64}", str(value)) for value in hashes.values()):
        problems.append("snapshot contains an invalid source SHA-256")
    return problems


def _forward_validation_problems(root: Path) -> list[str]:
    problems: list[str] = []
    path = root / "data" / "forward_validation.json"
    if not path.exists():
        return ["missing data/forward_validation.json"]
    try:
        status = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return [f"invalid forward-validation JSON: {exc}"]

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
        problems.append(f"forward-validation status missing sections: {sorted(missing)}")
        return problems

    reporting = status.get("public_reporting", {})
    if reporting.get("live_signals") is not False:
        problems.append("forward-validation status does not exclude live signals")
    if reporting.get("trade_level_records") is not False:
        problems.append("forward-validation status does not exclude trade-level records")
    if str(reporting.get("granularity", "")).lower() != "aggregate monthly":
        problems.append("forward-validation public granularity is not aggregate monthly")

    evidence = status.get("evidence", {})
    if status.get("status") == "not_started" and (
        evidence.get("public_observation_count") != 0
        or evidence.get("complete_months") != 0
    ):
        problems.append("not-started forward-validation status reports observations")

    candidate = status.get("candidate", {})
    manifest_path = root / "pinescript" / "manifest.json"
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        current = next(version for version in manifest["versions"] if version["current"])
    except (FileNotFoundError, json.JSONDecodeError, KeyError, StopIteration) as exc:
        problems.append(f"cannot validate forward candidate against Pine manifest: {exc}")
        return problems
    if candidate.get("version") != current.get("version"):
        problems.append("forward candidate version differs from current Pine version")
    if candidate.get("source_sha256") != current.get("sha256"):
        problems.append("forward candidate hash differs from current Pine source hash")
    return problems


def _backtest_csv_problems(root: Path) -> list[str]:
    problems: list[str] = []
    raw_header_tokens = {
        "date and time",
        "entry",
        "exit",
        "price",
        "quantity",
        "signal",
        "stop",
        "target",
        "timestamp",
        "trade_number",
        "volume",
    }
    for relative_name, expected_header in BACKTEST_CSV_SCHEMAS.items():
        path = root / relative_name
        if not path.exists():
            problems.append(f"missing aggregate backtest CSV: {relative_name}")
            continue
        try:
            with path.open(encoding="utf-8", newline="") as handle:
                reader = csv.DictReader(handle)
                rows = list(reader)
        except (UnicodeDecodeError, csv.Error) as exc:
            problems.append(f"invalid aggregate backtest CSV ({exc}): {relative_name}")
            continue
        if reader.fieldnames != expected_header:
            problems.append(f"aggregate backtest CSV schema mismatch: {relative_name}")
            continue
        normalized_header = {field.lower().replace(" ", "_") for field in reader.fieldnames}
        if normalized_header.intersection(raw_header_tokens):
            problems.append(f"trade-level field found in aggregate backtest CSV: {relative_name}")
        if not rows or len(rows) > 200:
            problems.append(f"aggregate backtest CSV row count outside public bounds: {relative_name}")
        if any(value is None or value == "" for row in rows for value in row.values()):
            problems.append(f"blank cell found in aggregate backtest CSV: {relative_name}")
        if any(
            str(value).lstrip().startswith(("=", "+", "@"))
            for row in rows
            for value in row.values()
        ):
            problems.append(f"spreadsheet formula prefix found in aggregate backtest CSV: {relative_name}")
    return problems


def scan_project(root: Path = PROJECT_ROOT) -> list[str]:
    problems: list[str] = []
    scanner_path = Path(__file__).resolve()

    for path in sorted(root.rglob("*")):
        if any(part in IGNORED_PARTS for part in path.parts):
            continue
        relative = path.relative_to(root)
        if path.is_symlink():
            problems.append(f"symlink prohibited in public release: {relative}")
            continue
        if not path.is_file():
            continue

        lower_name = path.name.lower()
        suffix = path.suffix.lower()
        if lower_name == ".env" or lower_name.startswith(".env."):
            problems.append(f"environment file prohibited: {relative}")
        if lower_name in FORBIDDEN_FILENAMES:
            problems.append(f"credential file prohibited: {relative}")
        if suffix in FORBIDDEN_SUFFIXES:
            problems.append(f"forbidden file type: {relative}")
        if suffix not in ALLOWED_SUFFIXES and path.name not in ALLOWED_EXTENSIONLESS:
            problems.append(f"unsupported public artifact type: {relative}")
        if path.stat().st_size > MAX_PUBLIC_FILE_BYTES:
            problems.append(f"file exceeds public size cap: {relative}")
        if suffix == ".png":
            metadata = _png_metadata_chunks(path.read_bytes())
            if metadata:
                problems.append(f"PNG metadata or malformed structure found ({sorted(metadata)}): {relative}")
            continue
        if path.resolve() == scanner_path or suffix not in TEXT_SUFFIXES:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            problems.append(f"non-text content in text artifact: {relative}")
            continue
        problems.extend(_text_problems(relative, text))

    problems.extend(_runtime_surface_problems(root))
    problems.extend(_workflow_security_problems(root))
    problems.extend(_snapshot_problems(root))
    problems.extend(_forward_validation_problems(root))
    problems.extend(_backtest_csv_problems(root))
    return sorted(set(problems))


def main() -> int:
    problems = scan_project()
    if problems:
        print("Public-release preflight FAILED:")
        for problem in problems:
            print(f"- {problem}")
        return 1
    print(
        "Public-release preflight passed: aggregate-only evidence, metadata-clean artifacts, "
        "commit-pinned automation, and no common secret, PII, path, upload, network, or raw-data leaks found."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
