from __future__ import annotations

from pathlib import Path

from src.ui import BACKGROUND_ASSET, background_data_uri, visual_css


ROOT = Path(__file__).resolve().parents[1]


def test_visual_system_uses_a_local_reviewed_asset():
    assert BACKGROUND_ASSET.is_file()
    assert BACKGROUND_ASSET.suffix == ".png"
    assert background_data_uri().startswith("data:image/png;base64,")


def test_visual_system_uses_complete_palette_and_respects_reduced_motion():
    css = visual_css()
    for color in ("#003049", "#D62828", "#F77F00", "#FCBF49", "#EAE2B7"):
        assert color in css.upper()
    assert "prefers-reduced-motion: reduce" in css
    assert "unsafe_allow_javascript" not in css


def test_glass_is_clearer_at_rest_and_blurs_on_hover():
    css = visual_css()
    assert "--qsvl-glass: rgba(0, 31, 46, 0.44)" in css
    assert "--qsvl-glass-hover: rgba(0, 31, 46, 0.62)" in css
    assert "backdrop-filter: blur(10px) saturate(108%)" in css
    assert "backdrop-filter: blur(16px) saturate(118%)" in css


def test_widget_mosaic_has_consistent_spacing_and_compact_status():
    css = visual_css()
    assert "--qsvl-space: clamp(0.78rem, 1.25vw, 1rem)" in css
    assert "--qsvl-radius: 0.4rem" in css
    assert "border-radius: var(--qsvl-radius) !important" in css
    assert ".st-key-page_status" in css
    assert "font-size: 2rem" in css
    assert "background: transparent !important" in css
    assert "stToolbarActionButtonLabel" in css
    assert ".st-key-app_footer" in css
    assert ".st-key-research_context {" in css
    assert "padding: 0.68rem 0.95rem !important" in css
    assert ".st-key-brief_path_chart::before" in css
    assert "background: var(--qsvl-gradient-warm)" in css


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


def test_theme_uses_the_reviewed_display_and_body_fonts():
    config = (ROOT / ".streamlit" / "config.toml").read_text(encoding="utf-8")
    assert 'font = "\'IBM Plex Sans\':' in config
    assert 'headingFont = "\'Space Grotesk\':' in config
    assert 'baseRadius = "6px"' in config
    assert 'buttonRadius = "6px"' in config
