# LinkedIn launch post

## Post settings

| Field | Recommended value |
|---|---|
| Audience | Anyone, only if you want the post indexed and shareable outside LinkedIn |
| Post type | Text with three images |
| Image order | Research brief, Monte Carlo paths, parameter stability |
| Comments | On |
| Notify network | On |

## Ready to paste

I have been working on a passion project around a question I keep coming back to: how can the discipline behind quantitative research be made more accessible to people who start with retail trading tools and strategy ideas?

Quant Strategy Validation Lab is my attempt to bridge part of that gap. It takes a familiar 30 minute opening range breakout and treats it as a research problem, not a finished trading system.

Instead of stopping at the equity curve, I tested the historical result against transaction costs, lookahead risk, purged out of sample splits, permutation and multiple testing controls, execution stress, parameter changes, and Monte Carlo resampling. I also kept rejected ideas and missing evidence visible.

The current research sample covers 729 cost adjusted historical trades from June 2021 through June 2026. The project remains a work in progress. Paper forward testing and pre 2021 validation are still outstanding, and I am not making a live performance claim.

I built the public project with Python, pandas, Altair, Streamlit, pytest, and GitHub Actions. AI helped me iterate on code, documentation, and the interface. I remained responsible for the research question, modeling decisions, validation criteria, evidence boundary, and every published claim.

If you work in quantitative research, systematic trading, data science, or research engineering, I would be interested to hear what you would stress next.

Live project: https://quant-strategy-validation-lab.streamlit.app/

GitHub: https://github.com/MikeSheehanJr/Quant-Strategy-Validation-Lab

Historical research and software engineering demonstration only. Not investment advice or a live trading system.

#QuantitativeResearch #Python #SystematicTrading #DataScience

## Image titles and alt text

### Image 1

**Title:** Research brief and current decision

**Alt text:** Quant Strategy Validation Lab research brief showing the historical research decision, cost adjusted trade count, win rate, profit factor, and the start of the historical P&L chart.

### Image 2

**Title:** Monte Carlo path stress test

**Alt text:** Monte Carlo chart showing individual resampled cumulative P&L paths and a median path across a selectable simulation horizon.

### Image 3

**Title:** Parameter stability surface

**Alt text:** Parameter heat map using one light blue to navy scale to compare profit factor across reward to risk and filter settings, with the frozen specification marked.

## Final review before posting

1. Upload only the three reviewed PNG files in `docs/linkedin/assets/`.
2. Confirm the image order matches the post settings table.
3. Add the supplied alt text if LinkedIn presents the option.
4. Open both links in a private browser window.
5. Confirm the work in progress and historical research language appears before the post is expanded.
6. Do not attach raw backtest exports, terminal screenshots, account screenshots, or a resume containing an address or private contact details.
