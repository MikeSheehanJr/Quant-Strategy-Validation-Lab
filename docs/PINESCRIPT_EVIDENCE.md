# Pine Script evolution and backtest evidence

## Why this track exists

The Python dashboard shows a 30-minute MNQ opening-range experiment with prior-only filters and a broad robustness battery. The Pine Script archive answers a different engineering question: how a symmetric ORB evaluated on a 15-minute chart moved from a research baseline to a safer TradingView paper-control implementation. Its 09:30–10:00 ET opening range is 30 minutes long and spans the first two 15-minute bars; “15-minute” describes the chart/bar resolution, not the range duration.

Keeping the tracks separate prevents a common portfolio failure: presenting one strategy's code beside another strategy's metrics as if they were the same experiment.

## Version lineage

- **v1, baseline:** one two sided breakout decision per session, fixed contracts, opposite range stop, and 1R target.
- **v2, risk normalization:** adds capped dollar risk sizing without changing the signal path.
- **v3, isolated optional filter:** adds one frozen, default off MGC only margin rule; MNQ cannot arm it.
- **v4, operating control:** adds a user maintained early close calendar and simplifies chart drawings.
- **v4.1, current MNQ paper control:** locks the script to one symbol, updates commission, disables the MGC only rule, and enables the calendar guard by default.

Every source file and hash is listed in `pinescript/manifest.json`.

## TradingView evidence source

The public aggregate CSVs were generated from the reviewed TradingView `v4.1` MNQ List of Trades export dated 2026-07-16. The source artifact contained 2,538 rows forming 1,269 complete entry/exit pairs. Structural QA found zero missing cells, zero duplicate rows, contiguous trade identifiers, exact entry/exit P&L agreement, and exact cumulative-P&L reconciliation. Its SHA-256 is recorded in the QA CSV. These results use the TradingView strategy's dynamic sizing, $1.82 round-turn commission, and one tick of slippage per fill; they do not use the Python headline's one-contract, $1.20 round-turn commission, and 0.5-tick slippage assumptions.

The public derivatives contain monthly and window-level aggregates only. Exact timestamps, signals, prices, quantities, and individual trade outcomes remain excluded. This keeps the evidence inspectable without redistributing raw bars or a signal-level trade list.

## What the export does and does not prove

The export proves that TradingView compiled and ran the current MNQ script, that its 1,269-trade path matched the archived combined-v4 path, and that the reviewed fee arithmetic reconciled. It does not complete wrong-symbol UI testing, chart/alert inspection, or the split-script replay of a historical early-close session.

The default early-close list is a forward operating calendar rather than a full historical calendar. Consequently, the all-time P&L is descriptive implementation evidence, not a funded-rule-compliant historical backtest. The public CSV intentionally includes the negative 2026 year-to-date result rather than hiding it. The displayed full-export and 2026 YTD windows are separate descriptive windows, not independent validation samples. Wrong-symbol/timeframe UI checks, chart and alert inspection, registered half-day replay, and a pre-collection forward decision rule remain open. Paper forward observations have not been collected.

## Rebuild

With a user-supplied TradingView export, rebuild the aggregate evidence with:

```bash
python scripts/build_pinescript_evidence.py \
  --mnq-export /path/to/tradingview-export.csv \
  --expected-trades 1269 \
  --expected-sha256 db022fe527e5ccb06eb38b1fc764110ca1cd461f3c6c50daea93e0112dc56800
```

The builder fails closed on schema drift, missing cells, duplicate rows, incomplete trade pairs, noncontiguous IDs, unsafe spreadsheet formula prefixes, P&L pair disagreement, or cumulative-P&L reconciliation errors.
