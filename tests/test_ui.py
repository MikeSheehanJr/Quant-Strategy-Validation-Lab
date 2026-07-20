from __future__ import annotations

from pathlib import Path

from src.ui import visual_css


ROOT = Path(__file__).resolve().parents[1]


def test_visual_system_uses_ivory_canvas_and_reviewed_palette():
    css = visual_css()
    for color in ("#2D3436", "#0A3D62", "#D4AF37", "#F9F9F9"):
        assert color in css.upper()
    assert "background: var(--qsvl-ivory)" in css
    assert "background-image" not in css
    assert "data:image" not in css
    assert "gradient" not in css.lower()


def test_visual_system_removes_glass_and_respects_reduced_motion():
    css = visual_css()
    assert "--qsvl-panel: #F0F3F4" in css
    assert "backdrop-filter" not in css
    assert "box-shadow: none" in css
    assert "prefers-reduced-motion: reduce" in css
    assert "unsafe_allow_javascript" not in css


def test_information_first_layout_and_scroll_focus_are_present():
    css = visual_css()
    assert "--qsvl-space: clamp(0.9rem, 1.45vw, 1.25rem)" in css
    assert "border-radius: 0 !important" in css
    assert '[class*="st-key-section_"] {' in css
    assert "position: sticky" in css
    assert "scroll-margin-top: 7rem" in css
    assert ':has([data-testid="stVegaLiteChart"])' in css
    assert "background: transparent !important" in css
    assert "border-left: 3px solid var(--qsvl-navy)" in css
    assert ".st-key-page_status" in css
    assert "font-size: 1.8rem" in css
    assert "stToolbarActionButtonLabel" in css


def test_work_status_uses_material_symbol_without_emoji():
    ui_source = (ROOT / "src" / "ui.py").read_text(encoding="utf-8")
    assert 'st.markdown(":material/handyman:"' in ui_source
    assert "\U0001F6E0" not in ui_source


def test_research_context_is_left_aligned_and_vertically_centered():
    ui_source = (ROOT / "src" / "ui.py").read_text(encoding="utf-8")
    boundary_source = ui_source.split("def render_research_boundary", maxsplit=1)[1]
    boundary_source = boundary_source.split("def render_section_header", maxsplit=1)[0]
    assert 'text_alignment="left"' in boundary_source
    assert 'vertical_alignment="center"' in boundary_source


def test_theme_uses_light_square_geometry_and_accessible_palette():
    config = (ROOT / ".streamlit" / "config.toml").read_text(encoding="utf-8")
    assert 'font = "\'IBM Plex Sans\':' in config
    assert 'headingFont = "\'Space Grotesk\':' in config
    assert 'base = "light"' in config
    assert 'baseRadius = "none"' in config
    assert 'buttonRadius = "none"' in config
    assert 'backgroundColor = "#F9F9F9"' in config
    assert 'secondaryBackgroundColor = "#F0F3F4"' in config
    assert 'linkColor = "#0A3D62"' in config
    assert 'textColor = "#2D3436"' in config
