"""Altair chart specifications for the Streamlit dashboard."""

from __future__ import annotations

import math

import altair as alt
import pandas as pd


CHARCOAL = "#2D3436"
NAVY = "#0A3D62"
GOLD = "#D4AF37"
IVORY = "#F9F9F9"
WHITE = "#FFFFFF"
MUTED = "#657179"
GRID = "#D8DEE1"
LIGHT_BLUE = "#A9BEC9"
PALE_BLUE = "#E6EEF2"
PALE_GOLD = "#FBF4D7"
LIGHT_GRAY = "#F0F3F4"
DARK_INK = CHARCOAL
HEATMAP_PALETTES = {
    "profit_factor": [PALE_BLUE, NAVY],
    "daily_sharpe": [PALE_GOLD, GOLD],
    "net_pnl_usd": [LIGHT_GRAY, CHARCOAL],
}
ANNUAL_BAR_PALETTE = [NAVY, GOLD, CHARCOAL, LIGHT_BLUE, NAVY, GOLD]


def _heatmap_text_color(frame: pd.DataFrame, metric: str) -> alt.ValueDef | alt.ConditionalDef:
    """Keep cell labels readable across each metric's dedicated color scale."""

    if metric not in HEATMAP_PALETTES:
        raise ValueError(f"Unsupported heat map metric: {metric}")
    if metric == "daily_sharpe":
        return alt.value(DARK_INK)

    minimum = float(frame[metric].min())
    maximum = float(frame[metric].max())
    threshold = minimum + ((maximum - minimum) * 0.55)
    return alt.condition(
        f"datum['{metric}'] >= {threshold}",
        alt.value(WHITE),
        alt.value(DARK_INK),
    )


def _focused_currency_domain(values: pd.Series) -> list[float]:
    """Keep cumulative paths honest without wasting a full tick below zero."""

    minimum = float(values.min())
    maximum = float(values.max())
    lower = min(0.0, math.floor(minimum / 500.0) * 500.0)
    upper = max(500.0, math.ceil(maximum / 1000.0) * 1000.0)
    return [lower, upper]


def _base(chart: alt.Chart, *, height: int = 300) -> alt.Chart:
    return (
        chart.properties(height=height, background=IVORY)
        .configure_axis(
            gridColor=GRID,
            gridOpacity=0.72,
            domainColor=GRID,
            domainOpacity=1.0,
            tickColor=MUTED,
            tickOpacity=0.5,
            labelColor=MUTED,
            labelOpacity=1.0,
            titleColor=CHARCOAL,
            titleOpacity=1.0,
        )
        .configure_view(strokeOpacity=0)
        .configure_legend(
            labelColor=CHARCOAL,
            labelOpacity=1.0,
            titleColor=CHARCOAL,
            titleOpacity=1.0,
            orient="top",
        )
    )


def equity_curve(monthly: pd.DataFrame) -> alt.Chart:
    """Monthly cumulative research P&L with explicit zero baseline."""

    domain = _focused_currency_domain(monthly["cumulative_pnl_usd"])
    line = (
        alt.Chart(monthly)
        .mark_line(color=NAVY, strokeWidth=3.0)
        .encode(
            x=alt.X("month:T", title="Month", axis=alt.Axis(format="%b %Y", labelAngle=0)),
            y=alt.Y(
                "cumulative_pnl_usd:Q",
                title="Cumulative P&L (USD)",
                scale=alt.Scale(domain=domain, zero=False, nice=False),
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
    zero = (
        alt.Chart(pd.DataFrame({"y": [0]}))
        .mark_rule(color=CHARCOAL, opacity=0.42, strokeWidth=1.2)
        .encode(y="y:Q")
    )
    return _base(line + zero, height=320)


def pinescript_equity_curve(monthly: pd.DataFrame) -> alt.Chart:
    """Aggregate TradingView v4.1 MNQ path with monthly evidence tooltips."""

    line = (
        alt.Chart(monthly)
        .mark_line(color=NAVY, strokeWidth=2.8)
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
    zero = alt.Chart(pd.DataFrame({"y": [0]})).mark_rule(color=CHARCOAL, opacity=0.42).encode(y="y:Q")
    return _base(line + zero, height=330)


def annual_pnl(yearly: pd.DataFrame) -> alt.Chart:
    """Annual aggregate P&L; partial periods use lower opacity."""

    annual_max = max(float(yearly["pnl_usd"].max()), 1.0)
    annual_min = min(float(yearly["pnl_usd"].min()), 0.0)
    y_domain = [
        annual_min - abs(annual_min) * 0.16,
        annual_max + annual_max * 0.16,
    ]
    year_domain = yearly["year"].tolist()
    year_range = [
        ANNUAL_BAR_PALETTE[index % len(ANNUAL_BAR_PALETTE)]
        for index in range(len(year_domain))
    ]

    bars = (
        alt.Chart(yearly)
        .mark_bar()
        .encode(
            x=alt.X("year:O", title="Calendar year", sort=None),
            y=alt.Y(
                "pnl_usd:Q",
                title="P&L per contract (USD)",
                scale=alt.Scale(domain=y_domain, zero=True, nice=False),
            ),
            opacity=alt.Opacity(
                "period_status:N",
                title="Period",
                scale=alt.Scale(domain=["Complete", "Partial"], range=[0.92, 0.72]),
                legend=None,
            ),
            color=alt.Color(
                "year:O",
                scale=alt.Scale(domain=year_domain, range=year_range),
                legend=None,
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
    labels = (
        alt.Chart(yearly)
        .mark_text(
            baseline="bottom",
            clip=False,
            color=CHARCOAL,
            dy=-7,
            fontSize=11,
            fontWeight=600,
        )
        .encode(
            x=alt.X("year:O", sort=None),
            y=alt.Y("pnl_usd:Q", scale=alt.Scale(domain=y_domain, zero=True, nice=False)),
            text=alt.Text("pnl_usd:Q", format="$,.0f"),
        )
    )
    return _base(bars + labels, height=320)


def monthly_pnl_distribution(monthly: pd.DataFrame) -> alt.Chart:
    """Distribution of complete-month aggregate P&L with a zero reference."""

    sample = monthly.loc[monthly["period_status"] == "Complete"].copy()
    bars = (
        alt.Chart(sample)
        .mark_bar(color=NAVY, opacity=0.86)
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
    zero = alt.Chart(pd.DataFrame({"x": [0]})).mark_rule(color=CHARCOAL, opacity=0.5).encode(x="x:Q")
    return _base(bars + zero, height=270)


def execution_heatmap(execution: pd.DataFrame, metric: str) -> alt.Chart:
    """Fill-resolution by slippage stress matrix."""

    label = {
        "profit_factor": "Profit factor",
        "daily_sharpe": "Daily Sharpe",
        "net_pnl_usd": "Net P&L (USD)",
    }[metric]
    fmt = ".3f" if metric != "net_pnl_usd" else "$,.0f"
    palette = HEATMAP_PALETTES[metric]
    heatmap = (
        alt.Chart(execution)
        .mark_rect(stroke=WHITE, strokeOpacity=0.92)
        .encode(
            x=alt.X("slippage_ticks:O", title="Modeled slippage (ticks)"),
            y=alt.Y("fill_minutes:O", title="Fill resolution (minutes)", sort="ascending"),
            color=alt.Color(
                f"{metric}:Q",
                title=label,
                scale=alt.Scale(range=palette),
                legend=alt.Legend(
                    orient="top",
                    direction="horizontal",
                    gradientLength=220,
                    gradientThickness=10,
                ),
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
        color=_heatmap_text_color(execution, metric),
    )
    return _base(heatmap + text, height=300)


def rr_sensitivity(rr: pd.DataFrame) -> alt.Chart:
    """Ordered parameter-sensitivity curve with the frozen value marked."""

    curve = (
        alt.Chart(rr)
        .mark_line(color=NAVY, strokeWidth=2.8)
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
        .mark_rule(color=GOLD, strokeDash=[5, 4], strokeWidth=1.5)
        .encode(x="reward_risk:Q")
    )
    return _base(curve + frozen, height=300)


def monte_carlo_paths(
    paths: pd.DataFrame,
    fan: pd.DataFrame,
    *,
    max_display_paths: int = 180,
) -> alt.Chart:
    """Show distinct cumulative bootstrap paths with the full sample median."""

    required = {
        "path_id",
        "cumulative_pnl_path",
    }
    if missing := required.difference(paths.columns):
        raise ValueError(f"Missing Monte Carlo path columns: {sorted(missing)}")
    if max_display_paths < 1:
        raise ValueError("max_display_paths must be positive")

    path_count = len(paths)
    display_count = min(path_count, max_display_paths)
    if display_count == 1:
        positions = [0]
    else:
        positions = sorted(
            {
                round(index * (path_count - 1) / (display_count - 1))
                for index in range(display_count)
            }
        )

    trajectory_rows: list[dict[str, float | int]] = []
    for row in paths.iloc[positions].itertuples(index=False):
        trajectory_rows.extend(
            {
                "path_id": int(row.path_id),
                "month": month,
                "cumulative_pnl_usd": float(value),
            }
            for month, value in enumerate(row.cumulative_pnl_path)
        )
    trajectories = pd.DataFrame(trajectory_rows)

    individual_paths = (
        alt.Chart(trajectories)
        .mark_line(color=LIGHT_BLUE, opacity=0.28, strokeWidth=0.8)
        .encode(
            x=alt.X("month:Q", title="Simulated month", scale=alt.Scale(zero=True)),
            y=alt.Y(
                "cumulative_pnl_usd:Q",
                title="Cumulative P&L per contract (USD)",
            ),
            detail=alt.Detail("path_id:N"),
            tooltip=[
                alt.Tooltip("path_id:N", title="Simulation path"),
                alt.Tooltip("month:Q", title="Month"),
                alt.Tooltip(
                    "cumulative_pnl_usd:Q",
                    title="Cumulative P&L",
                    format="$,.0f",
                ),
            ],
        )
    )
    median = (
        alt.Chart(fan)
        .mark_line(color=GOLD, strokeWidth=3.0)
        .encode(
            x="month:Q",
            y="p50:Q",
            tooltip=[
                alt.Tooltip("month:Q", title="Month"),
                alt.Tooltip("p50:Q", title="Median", format="$,.0f"),
            ],
        )
    )
    zero = alt.Chart(pd.DataFrame({"y": [0]})).mark_rule(color=CHARCOAL, opacity=0.42).encode(y="y:Q")
    return _base(individual_paths + median + zero, height=390)


def terminal_distribution(paths: pd.DataFrame, summary: dict[str, float | int]) -> alt.Chart:
    """Terminal P&L distribution with zero, P05, and median references."""

    bars = (
        alt.Chart(paths)
        .mark_bar(color=NAVY, opacity=0.84)
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
                    range=[CHARCOAL, GOLD, NAVY],
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
        .mark_bar(color=GOLD, opacity=0.82)
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
    palette = HEATMAP_PALETTES[metric]
    heatmap = (
        alt.Chart(frame)
        .mark_rect(stroke=WHITE, strokeOpacity=0.92)
        .encode(
            x=alt.X(f"{x_field}:O", title=x_title, sort="ascending"),
            y=alt.Y(f"{y_field}:O", title=y_title, sort="ascending"),
            color=alt.Color(
                f"{metric}:Q",
                title=label,
                scale=alt.Scale(range=palette),
                legend=alt.Legend(
                    orient="top",
                    direction="horizontal",
                    gradientLength=220,
                    gradientThickness=10,
                ),
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
        color=_heatmap_text_color(frame, metric),
    )
    frozen = (
        alt.Chart(frame.loc[frame["is_frozen"]])
        .mark_point(
            shape="diamond",
            size=150,
            filled=False,
            stroke=CHARCOAL if metric == "daily_sharpe" else GOLD,
            strokeWidth=2.2,
        )
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
        .mark_line(strokeWidth=2.5)
        .encode(
            x=alt.X("gate_length:Q", title="Trend-gate length (sessions)", scale=alt.Scale(zero=False)),
            y=alt.Y(f"{metric}:Q", title=label, scale=alt.Scale(zero=False)),
            color=alt.Color(
                "gate_kind:N",
                title="Gate",
                scale=alt.Scale(domain=["SMA", "EMA"], range=[NAVY, GOLD]),
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
        .mark_rule(color=CHARCOAL, strokeDash=[5, 4], strokeWidth=1.5)
        .encode(x="gate_length:Q")
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
        .mark_bar()
        .encode(
            x=alt.X(
                "entry_cutoff:N",
                title="Last allowed entry",
                sort=alt.SortField("display_order", order="ascending"),
                axis=alt.Axis(labelAngle=-35),
            ),
            y=alt.Y(f"{metric}:Q", title=label, scale=alt.Scale(zero=True)),
            color=alt.condition(
                "datum.is_frozen",
                alt.value(NAVY),
                alt.value(LIGHT_BLUE),
            ),
            opacity=alt.condition("datum.is_frozen", alt.value(1.0), alt.value(0.46)),
            tooltip=[
                alt.Tooltip("entry_cutoff:N", title="Last entry"),
                alt.Tooltip(f"{metric}:Q", title=label, format=fmt),
                alt.Tooltip("trades:Q", title="Trades"),
                alt.Tooltip("is_frozen:N", title="Frozen"),
            ],
        )
    )
    return _base(bars, height=300)
