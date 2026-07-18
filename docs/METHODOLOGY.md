# Methodology and metric definitions

## Research question

The project evaluates whether a deliberately simple MNQ opening-range breakout remains positive after realistic costs and a battery of adversarial validation checks.

The strategy case study uses:

- A 30-minute opening range from the regular-session open
- Bar-close breakout confirmation
- At most one trade per session
- A symmetric 1:1 stop/target geometry
- A strictly prior trend gate for shorts
- A strictly prior range filter that skips the widest opening ranges
- $1.20 round-turn commission and 0.5-tick modeled slippage in the headline snapshot

This is enough specification to understand the experiment. The public project does not distribute raw data or operate as a live signal service.

## Headline metric definitions

### Trade count

Completed historical trades that passed all frozen entry filters.

### Win rate

Winning trades divided by completed trades. Breakeven-after-cost trades are not counted as wins.

### Profit factor

Gross profit divided by the absolute value of gross loss.

### Calendar-honest daily Sharpe

The mean daily P&L divided by its population standard deviation, annualized by √252. Sessions with no trade are included as zero rather than dropped.

### Monthly aggregate drawdown

Peak-to-trough drawdown calculated from monthly P&L aggregates. This is intentionally labeled as monthly aggregate drawdown because it understates intramonth path risk and is not a substitute for the private intraday drawdown model.

### Dollar-based monthly risk diagnostics

The public dashboard calculates distributional diagnostics from the 59 explicitly complete monthly P&L observations. June 2021 and June 2026 are excluded because they are partial edge months. Annualized P&L and volatility scale the monthly mean by 12 and the monthly population standard deviation by √12. The monthly Sortino uses zero P&L as the minimum acceptable outcome. Historical VaR is the fifth percentile; CVaR is the average of observations at or below that threshold. These are dollar-based P&L diagnostics, not percentage investment returns.

### Aggregate monthly Monte Carlo

The public simulation is a moving-block bootstrap of complete monthly P&L aggregates. The viewer can select a 12-, 24-, or 36-month horizon; 1-, 3-, or 6-month contiguous blocks; and 1,000–5,000 paths. A fixed seed of 2026 makes the public output reproducible. Each path begins at zero, resamples historical blocks with replacement, and records cumulative P&L, terminal P&L, and maximum aggregate drawdown.

The simulation preserves limited dependence within each selected block but cannot create market regimes absent from the June 2021–June 2026 sample. It also conceals intramonth path dependence. It is a distributional stress view, not a forecast or probability statement about future performance.

## Validation methods

### Lookahead audit

Opening ranges, the range filter, and the trend gate were independently reconstructed from information available before entry. The audit also used a deliberate leakage probe to confirm that including current-session information would change the result.

### Probabilistic and deflated Sharpe ratios

The probabilistic Sharpe ratio adjusts for non-normal returns. The deflated Sharpe ratio additionally penalizes multiple testing and model search.

### Combinatorial purged cross-validation

Ten time blocks produce 45 train/test combinations with an embargo around the boundary. The headline model remained positive out of sample in all 45 reviewed splits. This does not make future profitability certain; it is evidence against a single lucky chronological split.

### Permutation tests

Breakout direction was randomized under the null. The actual result exceeded the randomization distribution with p < 0.0005 in the reviewed test.

### Execution stress

The strategy was evaluated across multiple fill resolutions, slippage assumptions, and commissions. The public app displays 12 resolution × slippage cells; the full private battery contains 24 resolution × slippage × commission cells.

### Parameter sensitivity

Nearby reward:risk settings were evaluated to distinguish a broad positive neighborhood from a single-point cliff. Higher full-sample values were not adopted when they failed the predeclared cross-validation bar.

The public parameter lab adds three reviewed two-dimensional surfaces from the five-minute execution audit: reward:risk × range-filter strength, opening-range length × reward:risk, and range-filter strength × lookback. It also displays 17 trend-gate variants and seven entry-window cutoffs. Each cell contains only aggregate trade count, win rate, profit factor, daily Sharpe, and net P&L. The frozen 30-minute opening range, 1.0 reward:risk, 10% range exclusion, 60-session lookback, and SMA50 short gate are marked explicitly. The highest full-sample cell is not treated as an adopted specification.

## Public snapshot provenance

The optional exporter runs inside the licensed private research workspace and writes only aggregate fields. It records hashes of the controlling engine, parameter atlas, and stress report. Those hashes show which reviewed inputs produced a release without publishing the private files.

The public snapshot cannot reproduce the underlying backtest by itself. A full reproduction requires separately licensed market data.

## Material limitations

- The sample begins in June 2021.
- The 2026 result ends in June and is partial.
- Historical simulations can remain overfit after extensive testing.
- Monthly aggregates conceal intramonth path dependence.
- Cross-provider differences may change stop/target sequencing.
- Paper forward-testing remains outstanding.
- No result is evidence of guaranteed or expected future return.
