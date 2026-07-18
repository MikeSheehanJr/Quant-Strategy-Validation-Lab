# Data notice

This repository does **not** include raw market data, resampled OHLCV data, trade-level records, credentials, account records, or live signals.

`data/public_snapshot.json` contains monthly P&L aggregates plus reviewed execution, parameter-surface, gate, cutoff, and validation summaries. It does not contain daily observations, intraday timestamps, or trade records. The optional exporter requires a separate private workspace and separately licensed source data.

The Monte Carlo paths shown in the app are generated at runtime from the 59 complete public monthly aggregates. They are synthetic resamples, contain no additional private observations, and are not written back into the snapshot.

`data/backtests/` contains three aggregate CSV derivatives of a reviewed TradingView v4.1 MNQ export: monthly results, selected descriptive windows, and structural QA/provenance. The source trade list is pinned by SHA-256 but is not distributed. The public CSVs exclude exact timestamps, signal labels, prices, quantities, and individual trade outcomes.

`pinescript/versions/` contains the user's versioned Pine Script source artifacts. These are code, not market data. `pinescript/manifest.json` pins their hashes and identifies the evidence state and limitations of each version.

Before publishing any regenerated snapshot:

1. Confirm that your data-provider agreement permits publication of the intended derived statistics.
2. Run `python scripts/release_gate.py`.
3. Inspect the full staged diff and every file size.
4. Verify that no intraday timestamp, bar, trade, credential, or local path is present.
5. Publish only the allowlisted aggregate artifacts—not the source data directory or full TradingView trade list.

The dashboard reference images supplied during design were used only as visual mood references. They are not included, copied, or redistributed here.
