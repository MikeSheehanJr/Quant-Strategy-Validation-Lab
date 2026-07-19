"""Altair chart specifications for the Streamlit dashboard."""

from __future__ import annotations

import altair as alt
import pandas as pd


NAVY_DARK = "#003049"
NAVY = "#2F6174"
NAVY_MID = "#5E8390"
CREAM = "#EAE2B7"
GOLD = "#FCBF49"
RED = "#D62828"
INK = CREAM
DARK_INK = "#001722"
MUTED = "#A6A18A"
GRID = "#355965"
WHITE = CREAM


def _base(chart: alt.Chart, *, height: int = 300) -> alt.Chart:
    return (
        chart.properties(height=height)
        .configure_axis(
            gridColor=GRID,
            gridOpacity=0.72,
            domainColor=GRID,
            tickColor=GRID,
            labelColor=MUTED,
            titleColor=MUTED,
        )
        .configure_view(strokeOpacity=0)
        .configure_legend(labelColor=MUTED, titleColor=MUTED, orient="top")
    )


def equity_curve(monthly: pd.DataFrame) -> alt.Chart:
    """Monthly cumulative research P&L with explicit zero baseline."""

    line = (
        alt.Chart(monthly)
        .mark_line(color=GOLD, strokeWidth=2.5, point=alt.OverlayMarkDef(size=24))
        .encode(
            x=alt.X("month:T", title="Month", axis=alt.Axis(format="%b %Y", labelAngle=0)),
            y=alt.Y(
                "cumulative_pnl_usd:Q",
                title="Cumulative P&L per contract (USD)",
                scale=alt.Scale(zero=True),
            ),
            tooltip=[
                alt.Tooltip("month:T", title="Month", format="%B %Y"),
                alt.Tooltip("period_status:N", title="Period"),
                alt.Tooltip("pnl_usd:Q", title="Monthly P&L", format="$,.0f"),
                alt.Tooltip(
                    "cumulative_pnl_usd:Q", title="Cumulative P&L", format="$,.0f"
                ),
                alt.Tooltip("trades:Q", title="Trades"),
            ],
        )
    )
    zero = alt.Chart(pd.DataFrame({"y": [0]})).mark_rule(color=MUTED, opacity=0.65).encode(y="y:Q")
    return _base(line + zero, height=330)


def pinescript_equity_curve(monthly: pd.DataFrame) -> alt.Chart:
    """Aggregate TradingView v4.1 MNQ path with monthly evidence tooltips."""

    line = (
        alt.Chart(monthly)
        .mark_line(color=CREAM, strokeWidth=2.5)
        .encode(
            x=alt.X("month:T", title="Exit month", axis=alt.Axis(format="%b %Y")),
            y=alt.Y(
                "cumulative_pnl_usd:Q",
                title="Cumulative TradingView P&L (USD)",
                scale=alt.Scale(zero=True),
            ),
            tooltip=[
                alt.Tooltip("month:T", title="Month", format="%B %Y"),
                alt.Tooltip("trades:Q", title="Completed trades"),
                alt.Tooltip("win_rate_pct:Q", title="Win rate", format=".2f"),
                alt.Tooltip("net_pnl_usd:Q", title="Monthly P&L", format="$,.2f"),
                alt.Tooltip("cumulative_pnl_usd:Q", title="Cumulative P&L", format="$,.2f"),
            ],
        )
    )
    zero = alt.Chart(pd.DataFrame({"y": [0]})).mark_rule(color=MUTED, opacity=0.65).encode(y="y:Q")
    return _base(line + zero, height=330)


def annual_pnl(yearly: pd.DataFrame) -> alt.Chart:
    """Annual aggregate P&L; partial periods use lower opacity."""

    bars = (
        alt.Chart(yearly)
        .mark_bar(color=NAVY_MID, cornerRadiusTopLeft=4, cornerRadiusTopRight=4)
        .encode(
            x=alt.X("year:O", title="Calendar year", sort=None),
            y=alt.Y("pnl_usd:Q", title="P&L per contract (USD)", scale=alt.Scale(zero=True)),
            opacity=alt.Opacity(
                "period_status:N",
                title="Period",
                scale=alt.Scale(domain=["Complete", "Partial"], range=[0.92, 0.38]),
            ),
            tooltip=[
                alt.Tooltip("year:O", title="Year"),
                alt.Tooltip("period_status:N", title="Period"),
                alt.Tooltip("pnl_usd:Q", title="P&L", format="$,.0f"),
                alt.Tooltip("trades:Q", title="Trades"),
                alt.Tooltip("win_rate_pct:Q", title="Win rate", format=".1f"),
                alt.Tooltip("profit_factor:Q", title="Profit factor", format=".3f"),
            ],
        )
    )
    labels = bars.mark_text(dy=-9, color=INK, fontSize=11).encode(
        text=alt.Text("pnl_usd:Q", format="$,.0f")
    )
    return _base(bars + labels, height=330)


def monthly_pnl_distribution(monthly: pd.DataFrame) -> alt.Chart:
    """Distribution of complete-month aggregate P&L with a zero reference."""

    sample = monthly.loc[monthly["period_status"] == "Complete"].copy()
    bars = (
        alt.Chart(sample)
        .mark_bar(color=NAVY_MID, opacity=0.86)
        .encode(
            x=alt.X(
                "pnl_usd:Q",
                bin=alt.Bin(maxbins=18),
                title="Monthly P&L per contract (USD)",
            ),
            y=alt.Y("count():Q", title="Complete months"),
            tooltip=[
                alt.Tooltip("pnl_usd:Q", bin=True, title="Monthly P&L range"),
                alt.Tooltip("count():Q", title="Months"),
            ],
        )
    )
    zero = alt.Chart(pd.DataFrame({"x": [0]})).mark_rule(color=INK, opacity=0.7).encode(x="x:Q")
    return _base(bars + zero, height=270)


def execution_heatmap(execution: pd.DataFrame, metric: str) -> alt.Chart:
    """Fill-resolution by slippage stress matrix."""

    label = {
        "profit_factor": "Profit factor",
        "daily_sharpe": "Daily Sharpe",
        "net_pnl_usd": "Net P&L (USD)",
    }[metric]
    fmt = ".3f" if metric != "net_pnl_usd" else "$,.0f"
    midpoint = float(execution[metric].min() + execution[metric].max()) / 2
    heatmap = (
        alt.Chart(execution)
        .mark_rect(cornerRadius=4)
        .encode(
            x=alt.X("slippage_ticks:O", title="Modeled slippage (ticks)"),
            y=alt.Y("fill_minutes:O", title="Fill resolution (minutes)", sort="ascending"),
            color=alt.Color(
                f"{metric}:Q",
                title=label,
                scale=alt.Scale(range=[NAVY_DARK, CREAM]),
            ),
            tooltip=[
                alt.Tooltip("fill_minutes:O", title="Fill resolution (min)"),
                alt.Tooltip("slippage_ticks:O", title="Slippage (ticks)"),
                alt.Tooltip(f"{metric}:Q", title=label, format=fmt),
                alt.Tooltip("trades:Q", title="Trades"),
            ],
        )
    )
    text = heatmap.mark_text(fontSize=12).encode(
        text=alt.Text(f"{metric}:Q", format=fmt),
        color=alt.condition(
            f"datum.{metric} >= {midpoint}", alt.value(DARK_INK), alt.value(WHITE)
        ),
    )
    return _base(heatmap + text, height=300)


def rr_sensitivity(rr: pd.DataFrame) -> alt.Chart:
    """Ordered parameter-sensitivity curve with the frozen value marked."""

    curve = (
        alt.Chart(rr)
        .mark_line(color=GOLD, strokeWidth=2.5, point=alt.OverlayMarkDef(size=70, filled=True))
        .encode(
            x=alt.X("reward_risk:Q", title="Reward:risk target", scale=alt.Scale(zero=False)),
            y=alt.Y("daily_sharpe:Q", title="Daily Sharpe", scale=alt.Scale(zero=True)),
            tooltip=[
                alt.Tooltip("reward_risk:Q", title="Reward:risk", format=".2f"),
                alt.Tooltip("daily_sharpe:Q", title="Daily Sharpe", format=".3f"),
                alt.Tooltip("profit_factor:Q", title="Profit factor", format=".3f"),
                alt.Tooltip("net_pnl_usd:Q", title="Net P&L", format="$,.0f"),
                alt.Tooltip("trades:Q", title="Trades"),
            ],
        )
    )
    frozen = (
        alt.Chart(pd.DataFrame({"reward_risk": [1.0]}))
        .mark_rule(color=CREAM, strokeDash=[5, 4], strokeWidth=1.5)
        .encode(x="reward_risk:Q")
    )
    return _base(curve + frozen, height=300)


def monte_carlo_fan(fan: pd.DataFrame) -> alt.Chart:
    """Nested percentile bands for cumulative block-bootstrap P&L."""

    outer = (
        alt.Chart(fan)
        .mark_area(color=NAVY_MID, opacity=0.22)
        .encode(
            x=alt.X("month:Q", title="Simulated month", scale=alt.Scale(zero=True)),
            y=alt.Y("p05:Q", title="Cumulative P&L per contract (USD)"),
            y2="p95:Q",
            tooltip=[
                alt.Tooltip("month:Q", title="Month"),
                alt.Tooltip("p05:Q", title="P05", format="$,.0f"),
                alt.Tooltip("p50:Q", title="Median", format="$,.0f"),
                alt.Tooltip("p95:Q", title="P95", format="$,.0f"),
            ],
        )
    )
    inner = (
        alt.Chart(fan)
        .mark_area(color=CREAM, opacity=0.22)
        .encode(x="month:Q", y="p25:Q", y2="p75:Q")
    )
    median = (
        alt.Chart(fan)
        .mark_line(color=GOLD, strokeWidth=2.6)
        .encode(x="month:Q", y="p50:Q")
    )
    zero = alt.Chart(pd.DataFrame({"y": [0]})).mark_rule(color=MUTED, opacity=0.7).encode(y="y:Q")
    return _base(outer + inner + median + zero, height=360)


def terminal_distribution(paths: pd.DataFrame, summary: dict[str, float | int]) -> alt.Chart:
    """Terminal P&L distribution with zero, P05, and median references."""

    bars = (
        alt.Chart(paths)
        .mark_bar(color=NAVY_MID, opacity=0.86)
        .encode(
            x=alt.X(
                "terminal_pnl_usd:Q",
                bin=alt.Bin(maxbins=32),
                title="Terminal P&L per contract (USD)",
            ),
            y=alt.Y("count():Q", title="Simulated paths"),
            tooltip=[
                alt.Tooltip("terminal_pnl_usd:Q", bin=True, title="Terminal P&L range"),
                alt.Tooltip("count():Q", title="Paths"),
            ],
        )
    )
    references = pd.DataFrame(
        {
            "value": [0.0, float(summary["terminal_p05_usd"]), float(summary["terminal_median_usd"])],
            "reference": ["Zero", "P05", "Median"],
        }
    )
    rules = (
        alt.Chart(references)
        .mark_rule(strokeWidth=1.6)
        .encode(
            x="value:Q",
            color=alt.Color(
                "reference:N",
                scale=alt.Scale(
                    domain=["Zero", "P05", "Median"],
                    range=[WHITE, RED, GOLD],
                ),
                title=None,
            ),
            strokeDash=alt.StrokeDash(
                "reference:N",
                scale=alt.Scale(
                    domain=["Zero", "P05", "Median"],
                    range=[[2, 2], [6, 4], [1, 0]],
                ),
                legend=None,
            ),
        )
    )
    return _base(bars + rules, height=300)


def drawdown_distribution(paths: pd.DataFrame) -> alt.Chart:
    """Distribution of simulated maximum drawdown magnitudes."""

    frame = paths.assign(drawdown_loss_usd=-paths["max_drawdown_usd"])
    bars = (
        alt.Chart(frame)
        .mark_bar(color=RED, opacity=0.68)
        .encode(
            x=alt.X(
                "drawdown_loss_usd:Q",
                bin=alt.Bin(maxbins=30),
                title="Maximum drawdown magnitude per contract (USD)",
            ),
            y=alt.Y("count():Q", title="Simulated paths"),
            tooltip=[
                alt.Tooltip("drawdown_loss_usd:Q", bin=True, title="Drawdown range"),
                alt.Tooltip("count():Q", title="Paths"),
            ],
        )
    )
    return _base(bars, height=300)


def parameter_surface_heatmap(
    frame: pd.DataFrame,
    *,
    x_field: str,
    y_field: str,
    x_title: str,
    y_title: str,
    metric: str,
) -> alt.Chart:
    """Reviewed two-dimensional parameter surface with the frozen cell marked."""

    label = {
        "daily_sharpe": "Daily Sharpe",
        "profit_factor": "Profit factor",
        "net_pnl_usd": "Net P&L (USD)",
    }[metric]
    fmt = ".3f" if metric != "net_pnl_usd" else "$,.0f"
    midpoint = float(frame[metric].min() + frame[metric].max()) / 2
    heatmap = (
        alt.Chart(frame)
        .mark_rect(cornerRadius=3)
        .encode(
            x=alt.X(f"{x_field}:O", title=x_title, sort="ascending"),
            y=alt.Y(f"{y_field}:O", title=y_title, sort="ascending"),
            color=alt.Color(
                f"{metric}:Q",
                title=label,
                scale=alt.Scale(range=[NAVY_DARK, CREAM]),
            ),
            tooltip=[
                alt.Tooltip(f"{x_field}:O", title=x_title),
                alt.Tooltip(f"{y_field}:O", title=y_title),
                alt.Tooltip(f"{metric}:Q", title=label, format=fmt),
                alt.Tooltip("trades:Q", title="Trades"),
                alt.Tooltip("win_rate_pct:Q", title="Win rate", format=".1f"),
                alt.Tooltip("is_frozen:N", title="Frozen cell"),
            ],
        )
    )
    values = heatmap.mark_text(fontSize=10).encode(
        text=alt.Text(f"{metric}:Q", format=fmt),
        color=alt.condition(
            f"datum.{metric} >= {midpoint}", alt.value(DARK_INK), alt.value(WHITE)
        ),
    )
    frozen = (
        alt.Chart(frame.loc[frame["is_frozen"]])
        .mark_point(shape="diamond", size=150, filled=False, stroke=WHITE, strokeWidth=2.2)
        .encode(x=f"{x_field}:O", y=f"{y_field}:O")
    )
    return _base(heatmap + values + frozen, height=360)


def gate_sensitivity_chart(gates: pd.DataFrame, metric: str) -> alt.Chart:
    """SMA/EMA gate-length sensitivity with a frozen-setting marker."""

    frame = gates.loc[gates["gate_kind"].isin(["SMA", "EMA"])].copy()
    label = {
        "daily_sharpe": "Daily Sharpe",
        "profit_factor": "Profit factor",
        "net_pnl_usd": "Net P&L (USD)",
    }[metric]
    fmt = ".3f" if metric != "net_pnl_usd" else "$,.0f"
    lines = (
        alt.Chart(frame)
        .mark_line(strokeWidth=2.3, point=alt.OverlayMarkDef(size=58, filled=True))
        .encode(
            x=alt.X("gate_length:Q", title="Trend-gate length (sessions)", scale=alt.Scale(zero=False)),
            y=alt.Y(f"{metric}:Q", title=label, scale=alt.Scale(zero=False)),
            color=alt.Color(
                "gate_kind:N",
                title="Gate",
                scale=alt.Scale(domain=["SMA", "EMA"], range=[CREAM, GOLD]),
            ),
            strokeDash=alt.StrokeDash(
                "gate_kind:N",
                scale=alt.Scale(domain=["SMA", "EMA"], range=[[1, 0], [6, 3]]),
                legend=None,
            ),
            tooltip=[
                alt.Tooltip("gate_kind:N", title="Gate"),
                alt.Tooltip("gate_length:Q", title="Length"),
                alt.Tooltip(f"{metric}:Q", title=label, format=fmt),
                alt.Tooltip("trades:Q", title="Trades"),
            ],
        )
    )
    frozen = (
        alt.Chart(frame.loc[frame["is_frozen"]])
        .mark_point(shape="diamond", size=170, color=WHITE, filled=True)
        .encode(x="gate_length:Q", y=f"{metric}:Q")
    )
    return _base(lines + frozen, height=300)


def cutoff_sensitivity_chart(cutoffs: pd.DataFrame, metric: str) -> alt.Chart:
    """Ordered entry-window cutoff comparison."""

    label = {
        "daily_sharpe": "Daily Sharpe",
        "profit_factor": "Profit factor",
        "net_pnl_usd": "Net P&L (USD)",
    }[metric]
    fmt = ".3f" if metric != "net_pnl_usd" else "$,.0f"
    bars = (
        alt.Chart(cutoffs)
        .mark_bar(color=NAVY_MID, cornerRadiusTopLeft=4, cornerRadiusTopRight=4)
        .encode(
            x=alt.X(
                "entry_cutoff:N",
                title="Last allowed entry",
                sort=alt.SortField("display_order", order="ascending"),
                axis=alt.Axis(labelAngle=-35),
            ),
            y=alt.Y(f"{metric}:Q", title=label, scale=alt.Scale(zero=True)),
            opacity=alt.condition("datum.is_frozen", alt.value(1.0), alt.value(0.55)),
            tooltip=[
                alt.Tooltip("entry_cutoff:N", title="Last entry"),
                alt.Tooltip(f"{metric}:Q", title=label, format=fmt),
                alt.Tooltip("trades:Q", title="Trades"),
                alt.Tooltip("is_frozen:N", title="Frozen"),
            ],
        )
    )
    return _base(bars, height=300)
