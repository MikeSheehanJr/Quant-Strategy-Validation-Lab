# TradingView paper acceptance matrix

**Current result: pending.** No row below is an observed pass. These cases must be run on the exact source and settings planned for collection. Save dated, reviewable evidence privately for each case, then update its `status` and set `evidence_ref` to the SHA-256 of that private evidence in [`data/forward_validation.json`](../data/forward_validation.json). A compile or historical trade-list match alone does not pass interactive operation.

| Case ID | Required observed behavior |
| --- | --- |
| `wrong_symbol` | On a non-MNQ chart, the script identifies the invalid symbol and generates no paper orders or alerts. Return to the intended MNQ continuous contract and confirm the lock clears. |
| `wrong_timeframe` | On a timeframe other than 15 minutes, no paper orders or alerts are produced. Restore 15 minutes and verify normal behavior. |
| `rth_eth_missing_post_session_bar` | Replay both RTH and ETH chart settings around the 16:00 ET boundary, including a path with no post-session bar. Confirm the final position is flat within the rule and no carry is silently created. Record any chart-session dependency. |
| `early_close` | On a verified CME early-close replay date, check the exact date-list input, entry cutoff, force-flat bar, and flat position before the exchange halt. Check an ordinary day separately. A calendar list merely present in code is not a pass. |
| `opening_range_missing` | Replay missing or incomplete 09:30–10:00 ET bars. Confirm no opening range is inferred from incomplete data and no entry occurs. |
| `entry_exit` | Observe long and short entry timing, one decision per session, opposite-range stop, 1R target, and session flat on representative bars; reconcile the broker emulator order list to chart markers. |
| `brackets` | Confirm stop and target orders exist with the expected side and quantity after each entry, update or cancel correctly, and never leave an unprotected position. |
| `fees` | Reconcile one entry and exit against the configured $0.91 per-side commission and one adverse tick per fill; retain the actual TradingView settings screen. |
| `sizing` | Recompute dynamic quantity from the $300 risk budget, opening-range stop distance, and 10-micro cap for narrow and wide ranges; verify zero-size skips and no drift to fixed mode. |
| `alerts` | Observe alerts for intended paper decisions, absence of alerts on invalid charts or skipped sessions, no duplicates, and no account or live-order automation. |

Record the TradingView version, chart symbol and session setting, timezone, exact script source hash, settings hash, reviewed CME calendar source and hash, replay date, expected behavior, actual behavior, and evidence reference privately. Do not publish screenshots or logs with account details, timestamps, prices, quantities, or trade-level records. A failure remains `failed` until corrected and replayed under a new reviewed candidate where the source or rules change. Do not assign a collection start while any case is pending or failed.

This matrix covers the operational acceptance gate only. Passing it does not establish strategy profitability, reliable execution, or live-trading readiness.
