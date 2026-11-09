from __future__ import annotations

from pathlib import Path

from streamlit.testing.v1 import AppTest


ROOT = Path(__file__).resolve().parents[1]


def test_research_brief_distinguishes_snapshot_and_review_dates_and_statuses():
    app = AppTest.from_file(str(ROOT / "streamlit_app.py"), default_timeout=30).run()

    assert not app.exception
    visible_text = "\n".join(
        [item.value for item in app.subheader]
        + [item.value for item in app.caption]
        + [item.value for item in app.markdown]
    )
    assert "July 18, 2026" in visible_text
    assert "November 8, 2026" in visible_text
    assert "Evidence status and next gates" in visible_text

    displayed_tables = [item.value for item in app.dataframe]
    status_table = next(table for table in displayed_tables if "Hosted app" in str(table))
    status_text = status_table.to_string(index=False)
    assert "Negative 2026 YTD retained" in status_text
    assert "No observations collected" in status_text
    assert "unverified" in status_text.lower()


def test_pine_page_explains_bar_resolution_and_preserves_open_evidence():
    app = AppTest.from_file(
        str(ROOT / "app_pages" / "implementation.py"), default_timeout=30
    ).run()

    assert not app.exception
    visible_text = "\n".join(
        [item.value for item in app.caption]
        + [item.value for item in app.markdown]
        + [item.value for item in app.subheader]
    )
    table_text = "\n".join(frame.value.to_string(index=False) for frame in app.dataframe)
    assert "15-minute chart lock; two bars define the range" in table_text
    assert "09:30–10:00 ET range spans two bars" in visible_text
    ytd_metric = next(metric for metric in app.metric if metric.label == "2026 YTD net P&L")
    assert ytd_metric.value.startswith("$-")
    assert any("Acceptance and release boundary" == item.value for item in app.subheader)
    acceptance = next(
        frame.value
        for frame in app.dataframe
        if "Wrong symbol and timeframe lock" in frame.value.to_string(index=False)
    )
    assert "Open" in acceptance.to_string(index=False)
