from __future__ import annotations

from src.ui import BACKGROUND_ASSET, background_data_uri, visual_css


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
    assert "--qsvl-glass: rgba(0, 36, 52, 0.30)" in css
    assert "--qsvl-glass-hover: rgba(0, 31, 46, 0.76)" in css
    assert "backdrop-filter: blur(8px) saturate(112%)" in css
    assert "backdrop-filter: blur(24px) saturate(138%)" in css
