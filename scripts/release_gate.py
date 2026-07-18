#!/usr/bin/env python3
"""Run the complete local release and security gate with one command."""

from __future__ import annotations

import importlib.util
import shutil
import subprocess
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
PIP_AUDIT_VERSION = "2.10.1"


def _run(label: str, command: list[str]) -> None:
    print(f"\n[{label}]")
    subprocess.run(command, cwd=PROJECT_ROOT, check=True)


def _dependency_audit_command() -> list[str]:
    arguments = [
        "--strict",
        "--progress-spinner=off",
        "--requirement",
        "requirements.txt",
    ]
    if importlib.util.find_spec("pip_audit") is not None:
        return [sys.executable, "-m", "pip_audit", *arguments]
    uvx = shutil.which("uvx")
    if uvx:
        return [
            uvx,
            "--from",
            f"pip-audit=={PIP_AUDIT_VERSION}",
            "pip-audit",
            *arguments,
        ]
    raise RuntimeError(
        "pip-audit is unavailable. Install pip-audit==2.10.1 or install uv, then rerun."
    )


def main() -> int:
    checks = [
        (
            "Compile Python",
            [
                sys.executable,
                "-m",
                "compileall",
                "-q",
                "streamlit_app.py",
                "app_pages",
                "src",
                "scripts",
                "tests",
            ],
        ),
        ("Public-release scan", [sys.executable, "scripts/preflight_public_release.py"]),
        ("Automated tests", [sys.executable, "-m", "pytest", "-q"]),
        ("Dependency vulnerability audit", _dependency_audit_command()),
    ]
    try:
        for label, command in checks:
            _run(label, command)
    except (RuntimeError, subprocess.CalledProcessError) as exc:
        print(f"\nRelease gate FAILED: {exc}", file=sys.stderr)
        return 1
    print("\nRelease gate PASSED. The local artifact is ready for a private-first remote review.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
