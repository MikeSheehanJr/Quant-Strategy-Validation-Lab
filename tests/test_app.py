from __future__ import annotations

from pathlib import Path

from streamlit.testing.v1 import AppTest


ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "streamlit_app.py"
ROBUSTNESS = ROOT / "app_pages" / "robustness.py"
IMPLEMENTATION = ROOT / "app_pages" / "implementation.py"
FORWARD_VALIDATION = ROOT / "app_pages" / "forward_validation.py"


def test_default_research_brief_renders():
    app = AppTest.from_file(str(APP), default_timeout=30).run()
    assert not app.exception
    assert app.title[0].value == "Quant strategy validation lab"
    assert any(item.value == "Strategy in plain English" for item in app.subheader)
    assert any(metric.label == "Cost-adjusted trades" for metric in app.metric)


def test_robustness_views_render():
    app = AppTest.from_file(str(ROBUSTNESS), default_timeout=30).run()
    assert not app.exception
    assert any(metric.label == "Annualized P&L" for metric in app.metric)

    app.segmented_control[0].set_value("Monte Carlo").run()
    assert not app.exception
    assert any(metric.label == "Terminal P&L above zero" for metric in app.metric)

    app.segmented_control[0].set_value("Parameters").run()
    assert not app.exception
    assert any(metric.label == "Reviewed 2D cells" for metric in app.metric)

    app.segmented_control[0].set_value("Validation").run()
    assert not app.exception
    assert any(metric.label == "Displayed execution cells" for metric in app.metric)


def test_implementation_page_renders():
    app = AppTest.from_file(str(IMPLEMENTATION), default_timeout=30).run()
    assert not app.exception
    assert app.title[0].value == "Pine Script implementation"
    assert any(metric.label == "Reviewed MNQ trades" for metric in app.metric)
    assert any(metric.label == "2026 YTD net P&L" for metric in app.metric)


def test_forward_page_states_that_evidence_has_not_started():
    app = AppTest.from_file(str(FORWARD_VALIDATION), default_timeout=30).run()
    assert not app.exception
    assert app.title[0].value == "Forward validation"
    assert any(metric.label == "Public observations" and metric.value == "0" for metric in app.metric)
    assert any(item.value == "Next required gate" for item in app.subheader)
