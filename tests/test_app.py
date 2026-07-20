from __future__ import annotations

from pathlib import Path

from streamlit.testing.v1 import AppTest


ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "streamlit_app.py"
ROBUSTNESS = ROOT / "app_pages" / "robustness.py"
IMPLEMENTATION = ROOT / "app_pages" / "implementation.py"
FORWARD_VALIDATION = ROOT / "app_pages" / "forward_validation.py"


def has_material_work_status(app: AppTest) -> bool:
    return any(item.value == ":material/handyman:" for item in app.markdown)


def test_default_research_brief_renders():
    app = AppTest.from_file(str(APP), default_timeout=30).run()
    assert not app.exception
    assert app.title[0].value == "Quant strategy validation lab"
    assert any(item.value == "How I’m testing the idea" for item in app.subheader)
    assert any(item.value == "Historical research path" for item in app.subheader)
    assert any(metric.label == "Cost adjusted trades" for metric in app.metric)
    assert any("AI assisted passion project" in item.value for item in app.caption)
    assert has_material_work_status(app)


def test_robustness_views_render():
    app = AppTest.from_file(str(ROBUSTNESS), default_timeout=30).run()
    assert not app.exception
    assert has_material_work_status(app)
    assert any(metric.label == "Annualized P&L" for metric in app.metric)

    app.segmented_control[0].set_value("Monte Carlo").run()
    assert not app.exception
    assert any(metric.label == "Terminal P&L above zero" for metric in app.metric)

    app.segmented_control[0].set_value("Parameters").run()
    assert not app.exception
    assert any(metric.label == "Reviewed 2D cells" for metric in app.metric)

    app.segmented_control[0].set_value("Validation").run()
    assert not app.exception
    assert any(metric.label == "Profitable cost stress cells" for metric in app.metric)


def test_implementation_page_renders():
    app = AppTest.from_file(str(IMPLEMENTATION), default_timeout=30).run()
    assert not app.exception
    assert app.title[0].value == "Pine Script implementation"
    assert has_material_work_status(app)
    assert any(metric.label == "Reviewed MNQ trades" for metric in app.metric)
    assert any(metric.label == "2026 YTD net P&L" for metric in app.metric)


def test_forward_page_states_that_evidence_has_not_started():
    app = AppTest.from_file(str(FORWARD_VALIDATION), default_timeout=30).run()
    assert not app.exception
    assert app.title[0].value == "Forward validation"
    assert has_material_work_status(app)
    assert any(
        metric.label == "Forward observations" and metric.value == "0"
        for metric in app.metric
    )
    assert any(item.value == "Forward test contract" for item in app.subheader)
    assert not any(metric.label == "Evidence state" for metric in app.metric)
    assert any(item.value == "Next required gate" for item in app.subheader)


def test_public_pages_hide_badge_markup_and_source_hashes():
    page_sources = [
        APP.read_text(encoding="utf-8"),
        IMPLEMENTATION.read_text(encoding="utf-8"),
        FORWARD_VALIDATION.read_text(encoding="utf-8"),
        (ROOT / "app_pages" / "research_brief.py").read_text(encoding="utf-8"),
    ]
    visible_source = "\n".join(page_sources)
    for hidden_text in (
        ":blue-badge[",
        ":gray-badge[",
        "Source SHA-256",
        "Snapshot digest",
    ):
        assert hidden_text not in visible_source
