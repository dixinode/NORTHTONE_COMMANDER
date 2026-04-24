"""Application configuration objects."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass
class SessionState:
    """Persisted UI state from the previous run."""

    left_path: Path
    right_path: Path
    active_panel_id: str = "left-panel"


@dataclass
class AppConfig:
    """Runtime configuration for the application."""

    app_name: str = "NorthTone Commander"
    default_path: Path = Path.home()
    config_path: Path = Path.home() / ".config" / "northtone-commander" / "config.json"

    def load_session_state(self) -> SessionState:
        """Load persisted panel state, falling back to sensible defaults."""
        data = self._read_config()
        left_path = self._valid_directory(data.get("left_path"), self.default_path)
        right_path = self._valid_directory(data.get("right_path"), self.default_path)
        active_panel_id = data.get("active_panel_id")
        if active_panel_id not in {"left-panel", "right-panel"}:
            active_panel_id = "left-panel"

        return SessionState(
            left_path=left_path,
            right_path=right_path,
            active_panel_id=active_panel_id,
        )

    def save_session_state(self, state: SessionState) -> None:
        """Persist panel paths and active side for the next run."""
        payload = {
            "left_path": str(state.left_path.expanduser()),
            "right_path": str(state.right_path.expanduser()),
            "active_panel_id": state.active_panel_id,
        }
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        self.config_path.write_text(
            json.dumps(payload, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )

    def _read_config(self) -> dict[str, Any]:
        try:
            raw = self.config_path.read_text(encoding="utf-8")
        except OSError:
            return {}

        try:
            data = json.loads(raw)
        except json.JSONDecodeError:
            return {}
        if not isinstance(data, dict):
            return {}
        return data

    @staticmethod
    def _valid_directory(value: Any, fallback: Path) -> Path:
        if not isinstance(value, str) or not value:
            return fallback.expanduser()

        candidate = Path(value).expanduser()
        if candidate.is_dir():
            return candidate
        return fallback.expanduser()
