#!/usr/bin/env python3
"""Enable supported GitHub security controls after the repository is public."""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys


API_VERSION = "2026-03-10"


def _gh(*arguments: str, payload: dict | None = None) -> None:
    command = [
        "gh",
        "api",
        "-H",
        "Accept: application/vnd.github+json",
        "-H",
        f"X-GitHub-Api-Version:{API_VERSION}",
        *arguments,
    ]
    subprocess.run(
        command,
        input=json.dumps(payload) if payload is not None else None,
        text=True,
        check=True,
    )


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Enable dependency alerts, automated security fixes, secret scanning, push protection, and private vulnerability reporting."
    )
    parser.add_argument("repository", help="GitHub repository in OWNER/REPO form")
    args = parser.parse_args()
    if not re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", args.repository):
        parser.error("repository must use OWNER/REPO form")
    if not shutil.which("gh"):
        print("GitHub CLI (gh) is not installed.", file=sys.stderr)
        return 1

    try:
        subprocess.run(["gh", "auth", "status"], check=True)
        _gh("--method", "PUT", f"repos/{args.repository}/vulnerability-alerts")
        _gh("--method", "PUT", f"repos/{args.repository}/automated-security-fixes")
        _gh("--method", "PUT", f"repos/{args.repository}/private-vulnerability-reporting")
        _gh(
            "--method",
            "PATCH",
            f"repos/{args.repository}",
            "--input",
            "-",
            payload={
                "security_and_analysis": {
                    "secret_scanning": {"status": "enabled"},
                    "secret_scanning_push_protection": {"status": "enabled"},
                }
            },
        )
        _gh(f"repos/{args.repository}")
        _gh(f"repos/{args.repository}/private-vulnerability-reporting")
    except subprocess.CalledProcessError as exc:
        print(f"GitHub security configuration FAILED: {exc}", file=sys.stderr)
        return 1

    print(
        "GitHub security configuration PASSED: dependency alerts, automated fixes, "
        "secret scanning, push protection, and private vulnerability reporting are enabled."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
