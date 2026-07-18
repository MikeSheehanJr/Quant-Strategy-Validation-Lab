# Security and responsible disclosure

## Public boundary

This app is static and aggregate-only. It has no credentials, API keys, database connection, network client, brokerage connection, user upload, or live execution path.

The automated release gate rejects:

- Environment, credential, private-key, archive, notebook, database, spreadsheet, serialized-model, raw-market, and unknown binary artifacts
- Symlinks, oversized files, metadata-bearing PNGs, local machine paths, personal email addresses, and common token formats
- Trade-level fields or raw OHLCV fields in the public JSON snapshot
- Runtime uploads, secrets, external connections, networking modules, and process-spawning modules
- GitHub Actions that are not pinned to immutable commits
- Python dependencies with known vulnerabilities reported by `pip-audit`

Run the complete local gate with one command:

```bash
python scripts/release_gate.py
```

CI runs the same gate. Dependabot, dependency review, and CodeQL configuration are checked into `.github/`. After the repository becomes public, enable the remaining repository-side controls with:

```bash
python scripts/configure_github_security.py OWNER/quant-strategy-validation-lab
```

The remote command enables dependency alerts, automated security fixes, secret scanning, push protection, and private vulnerability reporting, then reads the settings back. It is intentionally not run before a GitHub repository exists.

## If sensitive information is found

Stop publishing and rotate any exposed credential immediately. Deleting a file in a later commit does not remove it from Git history. Use GitHub’s sensitive-data removal procedure and report repository vulnerabilities through private vulnerability reporting rather than a public issue.
