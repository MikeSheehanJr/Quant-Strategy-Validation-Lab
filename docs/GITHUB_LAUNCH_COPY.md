# Plain-English GitHub launch copy

Replace the two bracketed URLs only after they work in a logged-out browser.

## Repository description

AI-assisted quant research passion project focused on whether a simple strategy survives costs, bias checks, parameter changes, and out-of-sample validation.

## GitHub profile pin description

I built this AI assisted passion project to show the research process behind a backtest, not just the final equity curve. It combines skeptical validation, an aggregate only public data boundary, interactive Monte Carlo and parameter testing, automated tests, and release security checks.

## Launch post

I’ve published an AI-assisted passion project that brings together two subjects I enjoy: quantitative research and software engineering. It is called **Quant Strategy Validation Lab**, and it remains a work in progress.

The project starts with a deliberately simple intraday futures strategy. The interesting part is not the strategy itself; it is the process used to test whether the result is fragile.

The repository shows how I handled transaction costs, lookahead checks, out-of-sample validation, parameter sensitivity, multiple-testing risk, Monte Carlo resampling, rejected ideas, and unresolved limitations. The Streamlit app presents only reviewed monthly and parameter aggregates. It does not include raw market data, individual trades, credentials, brokerage details, or live signals.

The historical June 2021–June 2026 sample contains 729 cost-adjusted trades with a 58.8% win rate and 1.315 profit factor. Those figures describe the research sample; they are not expected returns. Pre-2021 validation and a completed paper forward-test remain open.

The engineering side includes a modular Python/Altair/Streamlit architecture, deterministic simulations, pytest coverage, commit-pinned GitHub Actions, dependency auditing, CodeQL, Dependabot, and a fail-closed public-release scanner.

I used AI as a development partner for code iteration, documentation, and interface refinement. I remained responsible for the research question, modeling choices, validation criteria, release boundary, and every published claim.

Repository: https://github.com/MikeSheehanJr/Quant-Strategy-Validation-Lab

Live app: https://quant-strategy-validation-lab.streamlit.app/

This is a research and software-engineering demonstration, not investment advice or a live trading system.

## First release notes

### v0.1.0: public work in progress release

- Reorganized the app into four focused pages: research brief, robustness, implementation evidence, and forward validation
- Added a hash-pinned forward-validation status that explicitly reports zero observations and no forward conclusion
- Published an aggregate-only research snapshot with source hashes and no raw or trade-level data
- Added deterministic 12/24/36-month block-bootstrap stress testing
- Added execution, parameter, gate, and entry-window sensitivity views
- Added automated tests, dependency auditing, CodeQL, Dependabot, secret/PII scanning, artifact controls, and commit-pinned automation
- Documented the missing pre-2021 sample and unfinished paper forward-test

## Social-preview caption

Quant Strategy Validation Lab: an AI assisted passion project about testing robustness, documenting failures, and publishing evidence responsibly.

## Language guardrails

Use “historical research sample,” “cost-adjusted simulation,” “work in progress,” and “research demonstration.” Avoid “proven strategy,” “guaranteed edge,” “live returns,” or any statement that turns the Monte Carlo output into a forecast.
