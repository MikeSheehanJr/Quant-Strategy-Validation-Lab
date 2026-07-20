from __future__ import annotations

from pathlib import Path

from src.ui import visual_css


ROOT = Path(__file__).resolve().parents[1]


def test_visual_system_uses_plain_background_and_reviewed_palette():
    css = visual_css()
    for color in ("#2D3436", "#0A3D62", "#D4AF37", "#F9F9F9"):
        assert color in css.upper()
    assert "background-image" not in css
    assert "data:image" not in css
    assert "gradient" not in css.lower()


def test_selective_glass_is_flat_and_respects_reduced_motion():
    css = visual_css()
    assert "--qsvl-glass: rgba(10, 61, 98, 0.26)" in css
    assert "--qsvl-glass-strong: rgba(10, 61, 98, 0.44)" in css
    assert "backdrop-filter: blur(8px)" in css
    assert "box-shadow: none" in css
    assert "prefers-reduced-motion: reduce" in css
    assert "unsafe_allow_javascript" not in css


def test_rigid_widget_system_and_scroll_focus_are_present():
    css = visual_css()
    assert "--qsvl-space: clamp(0.78rem, 1.25vw, 1rem)" in css
    assert "border-radius: 0 !important" in css
    assert '[class*="st-key-section_"] {' in css
    assert "position: sticky" in css
    assert "scroll-margin-top: 7rem" in css
    assert ':has([data-testid="stVegaLiteChart"])' in css
    assert "border-left: 3px solid var(--qsvl-gold)" in css
    assert ".st-key-page_status" in css
    assert "font-size: 2rem" in css
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


def test_theme_uses_square_geometry_and_four_color_palette():
    config = (ROOT / ".streamlit" / "config.toml").read_text(encoding="utf-8")
    assert 'font = "\'IBM Plex Sans\':' in config
    assert 'headingFont = "\'Space Grotesk\':' in config
    assert 'baseRadius = "none"' in config
    assert 'buttonRadius = "none"' in config
    assert 'backgroundColor = "#2D3436"' in config
    assert 'secondaryBackgroundColor = "#0A3D62"' in config
    assert 'linkColor = "#D4AF37"' in config
    assert 'textColor = "#F9F9F9"' in config
