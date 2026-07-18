# Forward-validation protocol

The public forward-validation track is intentionally small and currently **not started**. It applies to the hash-pinned `v4.1` Pine Script companion, not the separate 30-minute Python engine behind the dashboard headline metrics.

## Current state

- Candidate: `v4.1` MNQ paper-control build
- Freeze date: July 16, 2026
- Source SHA-256: `e240d1259a0343ad92aee521004f977ed1c7cd01f6b6795b881dc34fcd423275`
- Public observations: 0
- Complete public months: 0
- Forward conclusion: none

The machine-readable status is stored in [`data/forward_validation.json`](../data/forward_validation.json) and is validated against the current Pine manifest.

## Discipline

1. The source version and hash are fixed before observation begins.
2. Any rule change creates a new version and a new record; prior observations are not reassigned.
3. Observation-only alerts, missing events, duplicate events, and corrections are reconciled privately.
4. Public reporting occurs only after a complete calendar month closes.
5. The public record is aggregate-only and excludes live signals, timestamps, prices, quantities, brokerage data, and account information.
6. No performance chart or forward claim is published before reconciled observations exist.

## Next gate

Before collection begins, the minimum sample, integrity checks, and decision rule must be registered in version control. Until then, the page is protocol-only and cannot be described as forward evidence.

## Planned public fields

| Field | Meaning |
| --- | --- |
| `month` | Closed calendar month covered by the record |
| `eligible_sessions` | Sessions that passed the frozen rules |
| `resolved_observations` | Paper observations fully reconciled |
| `net_pnl_r` | Aggregate outcome in risk units, not dollars |
| `max_drawdown_r` | Aggregate forward drawdown in risk units |
| `tracking_errors` | Missed, duplicate, or unreconciled events |
| `status` | Complete, corrected, or withheld with reason |

This protocol is research documentation, not investment advice or a live signal service.
