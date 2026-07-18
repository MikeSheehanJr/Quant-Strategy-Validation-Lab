from __future__ import annotations

from pathlib import Path

from streamlit.testing.v1 import AppTest


APP = Path(__file__).resolve().parents[1] / "streamlit_app.py"


def test_default_app_view_renders():
    app = AppTest.from_file(str(APP), default_timeout=30).run()
    assert not app.exception
    assert app.title[0].value == "Quant strategy validation lab"
    assert any(item.value == "Strategy background" for item in app.subheader)
    assert any(metric.label == "Cost-adjusted trades" for metric in app.metric)


def test_deep_research_views_render():
    app = AppTest.from_file(str(APP), default_timeout=30).run()

    app.radio[0].set_value("Monte Carlo").run()
    assert not app.exception
    assert any(metric.label == "Terminal P&L above zero" for metric in app.metric)

    app.radio[0].set_value("Parameter lab").run()
    assert not app.exception
    assert any(metric.label == "Reviewed 2D cells" for metric in app.metric)

    app.radio[0].set_value("Validation").run()
    assert not app.exception
    assert any(metric.label == "Displayed execution cells" for metric in app.metric)
