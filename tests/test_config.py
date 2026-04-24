from __future__ import annotations

import json
from pathlib import Path

from northtone.core.config import AppConfig, SessionState


def test_session_state_roundtrip(tmp_path: Path) -> None:
    left = tmp_path / "left"
    right = tmp_path / "right"
    left.mkdir()
    right.mkdir()
    config = AppConfig(default_path=tmp_path, config_path=tmp_path / "config.json")

    config.save_session_state(
        SessionState(
            left_path=left,
            right_path=right,
            active_panel_id="right-panel",
        )
    )
    state = config.load_session_state()

    assert state.left_path == left
    assert state.right_path == right
    assert state.active_panel_id == "right-panel"


def test_session_state_falls_back_for_missing_paths(tmp_path: Path) -> None:
    config_path = tmp_path / "config.json"
    config_path.write_text(
        json.dumps(
            {
                "left_path": str(tmp_path / "missing-left"),
                "right_path": str(tmp_path / "missing-right"),
                "active_panel_id": "missing-panel",
            }
        ),
        encoding="utf-8",
    )
    config = AppConfig(default_path=tmp_path, config_path=config_path)

    state = config.load_session_state()

    assert state.left_path == tmp_path
    assert state.right_path == tmp_path
    assert state.active_panel_id == "left-panel"


def test_session_state_ignores_invalid_json(tmp_path: Path) -> None:
    config_path = tmp_path / "config.json"
    config_path.write_text("{not-json", encoding="utf-8")
    config = AppConfig(default_path=tmp_path, config_path=config_path)

    state = config.load_session_state()

    assert state.left_path == tmp_path
    assert state.right_path == tmp_path
    assert state.active_panel_id == "left-panel"
