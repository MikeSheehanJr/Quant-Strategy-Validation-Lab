# Pine Script evidence track

This directory preserves five real Pine Script research artifacts from `v1` through the current `v4.1` MNQ paper-control build. The files are included so reviewers can inspect the evolution of the implementation rather than relying on screenshots or prose alone.

This is a **companion implementation track**. It uses 15-minute chart bars and a **30-minute opening range, 09:30–10:00 ET**, defined by two chart bars. Its breakout is symmetric and filter-free. It is related to the filtered Python case study that produces the dashboard's 729-trade headline snapshot, but uses a separate execution model and evidence record. Their metrics must not be combined.

`manifest.json` pins every checked-in version by SHA-256 and records what changed, why it changed, the evidence state, and the remaining limitation. Historical source headers are preserved as contemporaneous research records; later corrections and caveats take precedence over superseded estimates in older headers.

The current `v4.1` source is an observation-only paper control. It is not a live trading system and has not completed every interactive acceptance check.
