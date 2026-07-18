# Quant strategy validation lab

> **Work in progress:** a robustness-first quant research and software-engineering portfolio project.

This project asks a deliberately narrow question:

> Can a simple intraday strategy survive realistic costs, out-of-sample testing, parameter perturbation, and adversarial review?

The headline case study is a 30-minute opening-range breakout on MNQ. A separate Pine Script evidence track preserves the real `v1`–`v4.1` evolution of a related 15-minute symmetric ORB and its reviewed aggregate TradingView results. The tracks are labeled separately and their metrics are never combined. The project contains no raw market data, credentials, brokerage information, live signals, or trade-level records.

## Current research snapshot

- 729 historical, cost-adjusted trades
- 58.8% win rate
- 1.315 profit factor
- 1.317 calendar-honest daily Sharpe
- 45/45 CPCV splits positive out of sample
- 24/24 fill-resolution × cost stress cells profitable
- Research window: June 2021 through June 2026

These are historical research results, not expected returns. The sample begins in June 2021, the 2026 result is partial, and paper forward-testing is still outstanding.

## What this demonstrates

- Bias-aware backtest design and independent lookahead checks
- Transaction-cost and execution-resolution modeling
- Combinatorial purged cross-validation
- Permutation and multiple-testing controls
- Parameter and regime stability analysis
- Aggregate monthly moving-block Monte Carlo with terminal and drawdown distributions
- Dollar-based Sortino, volatility, VaR, CVaR, skewness, kurtosis, and recovery diagnostics
- Three reviewed two-dimensional parameter surfaces with frozen-cell markers
- Explicit failure documentation
- Five hash-pinned Pine Script versions with a change/evidence ledger
- Reviewed TradingView-derived monthly, window, and QA CSV downloads
- Hash-pinned forward-validation status with an explicit "not started" evidence state
- Aggregate-only public data design
- Streamlit, pandas, Altair, pytest, and GitHub Actions
- Fail-closed safeguards for secrets, PII, local paths, artifact metadata, raw data, runtime network surfaces, GitHub Actions, and vulnerable dependencies

## Run locally

Use Python 3.12 to match the recommended Streamlit Community Cloud deployment environment.

```bash
uv venv --python 3.12
source .venv/bin/activate
uv pip install --requirement requirements.txt
streamlit run streamlit_app.py
```

Run the complete release and security gate before sharing:

```bash
python scripts/release_gate.py
```

## Project map

```text
streamlit_app.py              Top navigation and shared app frame
app_pages/                    Four focused Streamlit research pages
src/data.py                   Aggregate snapshot contract and loading
src/metrics.py                Testable calculations
src/charts.py                 Explicit Altair chart specifications
src/forward.py                Forward-status and candidate-hash validation
data/public_snapshot.json     Public-safe, aggregate-only evidence
data/forward_validation.json  Machine-readable forward evidence state
data/backtests/               Aggregate TradingView-derived CSV evidence
pinescript/                   Hash-pinned Pine Script v1–v4.1 archive
scripts/build_public_snapshot.py
                              Optional exporter requiring licensed source data
scripts/preflight_public_release.py
                              Fail-closed artifact and runtime scan
scripts/release_gate.py       One-command tests, scan, compile, and dependency audit
scripts/configure_github_security.py
                              One-time remote security configuration
tests/                        Data, chart, app, and safety tests
docs/                         Methodology, roadmap, and publishing guide
```

## App structure

- **Research brief:** plain-English strategy, headline evidence, historical path, and the current research conclusion
- **Robustness:** one focused control for historical risk, Monte Carlo, parameter stability, validation evidence, and rejected ideas
- **Implementation:** inspectable Pine Script v1–v4.1 evolution, reviewed TradingView aggregates, downloadable CSV evidence, and open acceptance checks
- **Forward validation:** the hash-pinned v4.1 paper candidate, aggregate-only reporting protocol, and an explicit not-started evidence state

The Monte Carlo uses 59 complete monthly P&L aggregates and a fixed public seed. It is a resampling stress view—not a forecast—and cannot create regimes absent from the historical sample.

## Work-in-progress roadmap

The current MVP and safety boundary are complete. Remaining launch work includes:

1. GitHub and Streamlit deployment after the automated gate passes.
2. Logged-out verification of the two public URLs.
3. Register the forward-test sample, integrity checks, and decision rule before collection begins.
4. Complete and reconcile the paper forward-test.
5. Add pre-2021 MNQ/NQ validation under an appropriate data license.

See [PLAN.md](PLAN.md) for the full build plan, [docs/GITHUB_LAUNCH_COPY.md](docs/GITHUB_LAUNCH_COPY.md) for plain-English GitHub copy, and [docs/PUBLISHING_GUIDE.md](docs/PUBLISHING_GUIDE.md) for safe launch instructions.

## Data and risk boundary

The checked-in JSON and CSVs are derived aggregate research artifacts. They cannot reproduce either underlying backtest without separately licensed source data. The Pine Script track is a related implementation study and is not the exact engine behind the dashboard headline snapshot. The forward page currently contains no observations or performance claim. See [DATA_NOTICE.md](DATA_NOTICE.md), [docs/PINESCRIPT_EVIDENCE.md](docs/PINESCRIPT_EVIDENCE.md), [docs/FORWARD_VALIDATION.md](docs/FORWARD_VALIDATION.md), and [SECURITY.md](SECURITY.md).

## Disclaimer

This repository is for education, research, and software-engineering demonstration only. It is not investment advice, a solicitation, or a live trading system. Historical simulations are hypothetical and can differ materially from real execution.
