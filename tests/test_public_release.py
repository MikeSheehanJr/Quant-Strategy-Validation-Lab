from __future__ import annotations

from pathlib import Path
import json

from scripts.preflight_public_release import (
    PROJECT_ROOT,
    _configuration_security_problems,
    _png_metadata_chunks,
    _text_problems,
    _workflow_security_problems,
    _snapshot_problems,
    _forward_validation_problems,
    scan_project,
)


def test_public_release_preflight_passes():
    assert scan_project(PROJECT_ROOT) == []


def test_secret_pattern_rejects_openai_style_key():
    token = "sk-" + "proj-" + ("A" * 30)
    problems = _text_problems(Path("leak.txt"), f'api_key = "{token}"')
    assert any("OpenAI-style key" in problem for problem in problems)


def test_personal_email_and_local_path_are_rejected():
    email = "analyst@" + "private-domain.test"
    local_path = "/Us" + "ers/private/research"
    problems = _text_problems(
        Path("notes.md"),
        f"Contact {email} from {local_path}",
    )
    assert any("email address" in problem for problem in problems)
    assert any("local machine path" in problem for problem in problems)


def test_png_text_metadata_is_rejected():
    signature = b"\x89PNG\r\n\x1a\n"
    text_chunk = (4).to_bytes(4, "big") + b"tEXt" + b"note" + (b"0" * 4)
    end_chunk = (0).to_bytes(4, "big") + b"IEND" + (b"0" * 4)
    assert _png_metadata_chunks(signature + text_chunk + end_chunk) == {"tEXt"}


def test_unpinned_github_action_is_rejected(tmp_path):
    workflow_root = tmp_path / ".github" / "workflows"
    workflow_root.mkdir(parents=True)
    (workflow_root / "ci.yml").write_text(
        "permissions:\n  contents: read\njobs:\n  test:\n    steps:\n"
        "      - uses: actions/checkout@v7\n",
        encoding="utf-8",
    )
    problems = _workflow_security_problems(tmp_path)
    assert any("not commit-pinned" in problem for problem in problems)


def test_disabled_streamlit_browser_protection_is_rejected(tmp_path):
    devcontainer = tmp_path / ".devcontainer"
    devcontainer.mkdir()
    (devcontainer / "devcontainer.json").write_text(
        '{"postAttachCommand": "streamlit run streamlit_app.py '
        '--server.enableXsrfProtection false"}',
        encoding="utf-8",
    )
    problems = _configuration_security_problems(tmp_path)
    assert any("XSRF protection disabled" in problem for problem in problems)


def test_release_scan_rejects_semantically_inconsistent_snapshot(tmp_path):
    data = tmp_path / "data"
    data.mkdir()
    snapshot = json.loads((PROJECT_ROOT / "data/public_snapshot.json").read_text())
    snapshot["monthly"][0]["trades"] += 1
    (data / "public_snapshot.json").write_text(json.dumps(snapshot))
    assert any("invalid public snapshot contract" in p for p in _snapshot_problems(tmp_path))


def _forward_fixture(root):
    (root / "data").mkdir()
    (root / "pinescript").mkdir()
    (root / "pinescript/manifest.json").write_bytes(
        (PROJECT_ROOT / "pinescript/manifest.json").read_bytes()
    )
    return json.loads((PROJECT_ROOT / "data/forward_validation.json").read_text())


def test_release_scan_rejects_trade_payload_hidden_in_forward_status(tmp_path):
    status = _forward_fixture(tmp_path)
    status["intraday_records"] = [{"timestamp": "not-public-data"}]
    (tmp_path / "data/forward_validation.json").write_text(json.dumps(status))
    assert any("raw/trade-level forward keys" in p for p in _forward_validation_problems(tmp_path))


def test_release_scan_rejects_unearned_forward_readiness(tmp_path):
    status = _forward_fixture(tmp_path)
    status["status"] = "ready"
    (tmp_path / "data/forward_validation.json").write_text(json.dumps(status))
    assert any("invalid forward-validation contract" in p for p in _forward_validation_problems(tmp_path))
