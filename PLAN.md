# In-depth build plan

Status date: July 18, 2026  
Project state: **Work in progress — MVP implemented locally, not yet published**

## 1. Objective

Build a public portfolio project that demonstrates quantitative research judgment and production-minded Python skills without exposing licensed raw data, private strategy infrastructure, credentials, account information, or claims that historical results are live performance.

The intended audience is a quant researcher, quant developer, systematic-trading, or data-science hiring manager. The default experience must answer three questions in under one minute:

1. What was tested?
2. What survived serious validation?
3. What remains uncertain or incomplete?

## 2. Positioning

### Core message

“I built the research process to reject fragile strategies, not to maximize a backtest screenshot.”

### Work-in-progress framing

The project must never imply that the research program is finished. “Work in progress” appears in the README, app header, app sidebar, roadmap, LinkedIn copy, and resume entry. The status can change only after the launch and forward-validation exit criteria are met.

### Non-goals

- No live trading or order execution
- No account-purchase or prop-firm economics
- No raw intraday data distribution
- No guarantee, recommendation, or forecast
- No strategy retuning for a better public headline
- No use of third-party dashboard reference images as publishable assets

## 3. Dashboard brief

### Audience

Quant and engineering recruiters who may spend 30–90 seconds on the first visit, plus technical reviewers who may inspect the repository.

### Primary question

Does a simple MNQ opening-range breakout remain positive after realistic costs and adversarial validation?

### Hero metrics

| Metric | Definition | Public value |
|---|---|---:|
| Cost-adjusted trades | Completed historical trades under the frozen specification | 729 |
| Win rate | Winning trades ÷ completed trades | 58.8% |
| Profit factor | Gross profit ÷ absolute gross loss | 1.315 |
| Daily Sharpe | Calendar-honest daily mean ÷ standard deviation × √252; zero on no-trade sessions | 1.317 |
| CPCV OOS-positive | Embargoed combinatorial splits with positive out-of-sample Sharpe | 45/45 |

### Default layout

1. Work-in-progress status and research question
2. Four hero metrics
3. Monthly cumulative P&L and calendar-year comparison
4. Validation summary and missing evidence
5. Aggregate monthly Monte Carlo with terminal and drawdown distributions
6. Parameter lab with three two-dimensional surfaces and one-dimensional sensitivity views
7. Validation ledger and failure journal
8. Build log, architecture, and limitations

### Visual system

- Near-black and deep-navy surfaces with high-contrast white information text
- Controlled blue-to-white analytical accents for active controls, percentile bands, heatmaps, and frozen-setting markers
- A restrained single-root blue palette across charts, controls, tables, and navigation
- No gradients inside chart marks
- No fake cards, balances, wallets, or brokerage controls
- No custom CSS; use Streamlit’s native theme and components
- Mobile-friendly stacking and no more than four fixed columns

## 4. Public data contract

### Allowed

- Monthly P&L aggregates
- Year-level performance summaries
- Side-level aggregate statistics
- Parameter and execution stress summaries
- Gate-length and entry-window aggregate sensitivity summaries
- Validation results already reviewed in the private research record
- Source-artifact hashes for provenance

### Prohibited

- Raw or resampled OHLCV files
- Intraday timestamps or bar-level records
- Trade-level entries, exits, stops, or targets
- API keys, data-provider credentials, or `.env` files
- Account balances, payment data, or brokerage identifiers
- Absolute local machine paths
- Private workspace files copied wholesale

### Verification

`scripts/preflight_public_release.py` rejects raw-data and serialized artifacts, archives, notebooks, symlinks, unknown binaries, metadata-bearing PNGs, secrets, PII, private-key blocks, local paths, oversized files, runtime upload/network surfaces, unpinned GitHub Actions, and raw/trade-level keys in the public snapshot. `scripts/release_gate.py` adds compilation, the full test suite, and a live dependency-vulnerability audit.

## 5. Architecture

```text
Private licensed research workspace
        |
        | optional aggregate exporter
        v
data/public_snapshot.json
        |
        +--> src/data.py       schema and loading
        +--> src/metrics.py    quant diagnostics
        +--> src/simulations.py aggregate monthly bootstrap
        +--> src/charts.py     visual specifications
        +--> streamlit_app.py presentation and interaction
        |
        +--> tests + release preflight + CI
```

The deployed app has no network connection, secrets, or private source dependency. Its only data dependency is the checked-in aggregate JSON snapshot.

## 6. Workstreams and execution status

### Phase 1 — Isolate the public project

Status: **Complete**

Tasks:

- Create a separate project directory outside any private repository history.
- Add a deny-by-default `.gitignore` for raw and high-resolution data.
- Keep the private strategy and deployment research untouched.
- Re-run the numerical replication gate before using any outputs.

Exit evidence:

- Replication gate returned 729 trades, 58.8% win rate, and 1.315 profit factor for the 30-minute fill baseline.
- No private files are imported by the deployed app.

### Phase 2 — Build the aggregate evidence snapshot

Status: **Complete**

Tasks:

- Export monthly, yearly, side, execution, reward:risk, gate, cutoff, and two-dimensional parameter aggregates.
- Add validation-ledger and failure-journal records.
- Record source-artifact SHA-256 hashes.
- Explicitly declare that raw market and trade-level data are absent.

Exit evidence:

- `data/public_snapshot.json`
- Reconciliation tests for trades and net P&L
- Aggregate-only release preflight

### Phase 3 — Build the dashboard MVP

Status: **Complete**

Tasks:

- Implement Overview, Monte Carlo, Parameter lab, Validation, and Build log views.
- Add metric cards, an honest zero-based cumulative chart, annual bars, execution heatmap, and parameter curve.
- Add aggregate monthly percentile fans, terminal/drawdown distributions, quant risk diagnostics, and reviewed parameter heatmaps.
- Show partial-year and incomplete-evidence labels.
- Use native Streamlit layout, selection, theming, tables, and Altair charts.

Exit evidence:

- App imports and renders in Streamlit’s test harness.
- Every chart compiles to a Vega-Lite specification.

### Phase 4 — Add engineering and public-release QA

Status: **Complete**

Tasks:

- Unit-test metrics and aggregate reconciliation.
- Compile-test all charts.
- Smoke-test the default Streamlit page.
- Add a GitHub Actions workflow on Python 3.12.
- Add a fail-closed release scanner.
- Pin every GitHub Action to an immutable commit.
- Add `pip-audit`, CodeQL, dependency review, and weekly Dependabot updates.
- Add a single local command that runs the complete release and security gate.

Exit evidence:

- `pytest` passes.
- Public-release preflight passes.
- Dependency audit reports no known vulnerabilities.
- Local app boots and charts render.

### Phase 5 — Prepare the publishing kit

Status: **Complete**

Tasks:

- Write safe GitHub initialization and review steps.
- Write Streamlit Community Cloud deployment steps.
- Draft LinkedIn post, Projects-section copy, Featured-section copy, and resume bullets.
- Draft a plain-English GitHub announcement, repository description, profile-pin summary, and first-release notes.
- Create a logged-out review and link-check protocol.

Exit evidence:

- `docs/PUBLISHING_GUIDE.md`
- `docs/PROFILE_AND_RESUME_COPY.md`
- `docs/GITHUB_LAUNCH_COPY.md`

### Phase 6 — Publish and verify

Status: **Pending user action**

Tasks:

- Create the GitHub repository, preferably private first.
- Run `scripts/release_gate.py`; CI independently reruns the same fail-closed gate.
- Make the repository public only after the final audit.
- Run `scripts/configure_github_security.py OWNER/REPO` to enable and verify supported remote controls.
- Deploy the Streamlit app from `main` using Python 3.12 and no secrets.
- Open both URLs in a logged-out/private browser window.
- Add the project to LinkedIn and the resume.

Exit criteria:

- Public GitHub URL works when logged out.
- Live app works when logged out and contains no private content.
- CI is green.
- LinkedIn and resume links resolve correctly.

### Phase 7 — Extend the research evidence

Status: **Planned**

Tasks:

- Complete the predefined paper forward-test and reconciliation log.
- Acquire and test pre-2021 MNQ/NQ data under an appropriate license.
- Add a reproducible notebook that accepts user-supplied data.
- Version each research snapshot and preserve prior results.
- Replace “work in progress” only after the stated exit criteria are satisfied.

Exit criteria:

- Forward-test mismatch rate is within the predeclared tolerance.
- Pre-2021 result and caveats are published regardless of outcome.
- Public release has a tagged version and reproducible changelog.

## 7. Chart contracts

| Section | Question | Form | Data sufficiency | Palette | QA requirement |
|---|---|---|---|---|---|
| Cumulative research P&L | How did the aggregate path evolve? | Monthly line | 61 monthly points | Single blue root | Zero baseline, partial periods labeled |
| Calendar-year outcomes | Was the result isolated to one year? | Ordered bars | 6 periods | Blue + opacity for partial | Bars start at zero; 2021/2026 partial |
| Execution stress | Does the result depend on fill assumptions? | 4×3 heatmap | 12 reviewed cells | Blue sequential | Exact values and units in cells/tooltips |
| Reward:risk sensitivity | Is the selected value a single-point cliff? | Ordered line + points | 9 reviewed settings | Blue root + dark-blue reference | Frozen setting marked; no retuning implication |
| Monthly P&L distribution | What does the complete-month outcome shape look like? | Histogram | 59 complete months | Blue root + neutral zero | Partial edge months excluded |
| Monte Carlo path uncertainty | How wide is the range of resampled cumulative outcomes? | Nested percentile fan | 1,000–5,000 moving-block paths | Navy/blue/ice-white | P05/P25/P50/P75/P95; zero visible |
| Monte Carlo terminal and drawdown risk | What terminal and path losses occur across resamples? | Histograms | One row per simulated path | Blue root + reference rules | Seed and assumptions visible |
| Parameter atlas | Is the frozen specification surrounded by a viable neighborhood? | 2D heatmaps | 81 reviewed cells across 3 surfaces | Blue-to-white sequential | Frozen cell marked; tooltips retain N |
| Gate and entry-window sensitivity | Do neighboring operating choices collapse? | Ordered lines and bars | 17 gate variants + 7 cutoffs | Two blue tones + opacity | Frozen choice marked without retuning claim |
| Validation ledger | What tests were run? | Exact table | 6 reviewed tests | Neutral | Evidence and purpose visible |
| Failure journal | What did not survive? | Exact table | 5 reviewed hypotheses | Neutral | Rejections are not hidden |

## 8. Acceptance criteria

### Research integrity

- All visible numerical claims reconcile to the public snapshot.
- The snapshot reconciles to the verified private source.
- Partial periods and unresolved evidence are visible.
- No public wording equates a backtest with live performance.

### Engineering

- Fresh install succeeds on Python 3.12.
- The app starts from the repository root.
- Default view is useful before interaction.
- At least one chart and one table render in the smoke test.
- CI and release preflight pass.
- Dependency audit, CodeQL configuration, commit-pin validation, and scanner unit tests pass.

### Safety

- No raw market data or trade-level records.
- No credentials, secrets, local paths, or personal financial information.
- Only screenshots of this project may be shared; reference images are excluded.
- The local release boundary is enforced automatically; the only unavoidable human decisions are repository visibility and whether the final public claims reflect the author’s intent.

### Portfolio quality

- A recruiter can identify the question, evidence, limitations, and tech stack quickly.
- README and live app tell the same story.
- GitHub, app, LinkedIn, and resume links are stable and consistent.
- The WIP label remains until forward-validation milestones are met.

## 9. Maintenance cadence

- Re-run `python scripts/release_gate.py` on every commit.
- Update `snapshot_date`, source hashes, and changelog when evidence changes.
- Recheck public links monthly while actively applying.
- Let Dependabot open weekly dependency and GitHub Action updates; merge only after CI, dependency review, and CodeQL pass.
- Never silently replace an unfavorable result; version and explain it.
