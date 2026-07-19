from __future__ import annotations

from src.ui import BACKGROUND_ASSET, background_data_uri, visual_css


def test_visual_system_uses_a_local_reviewed_asset():
    assert BACKGROUND_ASSET.is_file()
    assert BACKGROUND_ASSET.suffix == ".png"
    assert background_data_uri().startswith("data:image/png;base64,")


def test_visual_system_excludes_orange_and_respects_reduced_motion():
    css = visual_css()
    assert "#F77F00" not in css.upper()
    assert "prefers-reduced-motion: reduce" in css
    assert "unsafe_allow_javascript" not in css
