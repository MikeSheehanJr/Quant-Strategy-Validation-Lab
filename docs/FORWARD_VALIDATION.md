# Prospective paper forward-validation protocol

The registered `mnq-paper-forward-v1` protocol is **not ready for collection**. It describes a proposed paper observation of the hash-pinned `v4.1` MNQ Pine companion. It does not validate the separate 30-minute Python research engine. The July 16, 2026 v4.1 status remains an archived candidate record; the prospective registration was made on November 8, 2026 and does not retroactively turn July work into forward evidence.

The machine-readable record is [`data/forward_validation.json`](../data/forward_validation.json). It currently has zero public observations, zero complete months, no performance rows, and no forward conclusion. The current candidate has a pinned Pine source hash and registered protocol hash. Its **settings hash, verified calendar source and hash, freeze date, readiness date, and collection start are pending**. The TradingView acceptance cases are pending, not approved.

## Collection gates

Before the first observation, a reviewer must complete every case in [the paper acceptance matrix](PAPER_ACCEPTANCE.md), capture a source reference for each pass, verify the actual CME session calendar and hash the reviewed calendar artifact, and freeze the exact TradingView settings including the early-close date input. The source, settings, calendar, and protocol hashes identify one candidate. The reviewer records readiness on that day and chooses a future first day of a calendar month as the collection start. A missed start needs a new prospective registration; observations cannot be backdated.

States are `not_ready`, `ready`, `collecting`, `under_review`, `inconclusive`, and `completed`. The first two contain no forward observations. Collection can begin only after all gates pass. A new rule or settings version requires a new candidate and protocol record with previous candidates, protocols, month revisions, negative outcomes, and corrections preserved. This release does not automate candidate replacement.

## Observation and first review

Each calendar month is reconciled privately after it closes. Every detected opportunity must be classified as a resolved paper trade, a no-trade decision, or unresolved. Missed, duplicate, late, and corrected events remain visible to the private audit. The public publisher accepts reviewed **month-level aggregates only**. It does not connect to TradingView, a broker, an account, or a live signal feed.

The first review gate is **three complete calendar months and at least 60 resolved trades, with zero unresolved opportunities**. This is a minimum checkpoint, not a promise of statistical power. The registered descriptive decision rule is: any recorded tracking errors yield `inconclusive`; otherwise total net R above zero yields `supports_further_research`, and total net R at or below zero yields `does_not_support`. A positive checkpoint is not a validated alpha claim or expected-return estimate. The review date and decision are recorded only after the threshold is met; until then the conclusion remains “No forward-performance conclusion.”

## Public monthly contract

The public status contains `monthly_records` only after a month has closed. Each record includes `month`, `revision`, `supersedes_revision`, `revision_reason`, `eligible_sessions`, `opportunities_detected`, `resolved_trades`, `no_trade_decisions`, `unresolved_opportunities`, `negative_trades`, `tracking_errors`, `net_pnl_r`, and `within_month_max_drawdown_r`. The drawdown field is within that month, not a continuous cross-month drawdown. Revisions append after previous published records even when they correct an older month; originals and negative values remain visible. All intervening calendar months must be represented.

The offline publisher is [`scripts/build_forward_evidence.py`](../scripts/build_forward_evidence.py). It accepts a separately held JSON reconciliation file with schema version `1.0.0`, the candidate ID and four hashes, and a `months` list using exactly the public month fields above. It refuses unexpected fields, inconsistent opportunity counts, open or future months, identity mismatches, and changed prior revisions. The input is private and must never be copied into this repository. Run it as a module with `python -m scripts.build_forward_evidence --private-input INPUT.json --public-status data/forward_validation.json --output OUTPUT.json --as-of YYYY-MM-DD`; review the output before replacing the checked-in status. The public application reads only the reviewed JSON and has no upload or network ingestion path.

This is research documentation, not investment advice or a live signal service.
