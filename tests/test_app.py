from __future__ import annotations

import asyncio
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path

from northtone.app import NorthToneApp
from northtone.core.filesystem import FileEntry, FileSystemError


def test_external_command_uses_textual_suspend_context(monkeypatch) -> None:
    app = NorthToneApp()
    calls: list[tuple[str, object]] = []

    @contextmanager
    def fake_suspend():
        calls.append(("suspend-enter", None))
        yield
        calls.append(("suspend-exit", None))

    def fake_run(command: list[str], *, check: bool) -> None:
        calls.append(("run", (command, check)))

    monkeypatch.setattr(app, "suspend", fake_suspend)
    monkeypatch.setattr("northtone.app.subprocess.run", fake_run)

    asyncio.run(app._run_external_command(["tool", "arg"]))

    assert calls == [
        ("suspend-enter", None),
        ("run", (["tool", "arg"], False)),
        ("suspend-exit", None),
    ]


def test_copy_targets_for_multiple_entries_use_destination_directory(tmp_path: Path) -> None:
    app = NorthToneApp()
    destination = tmp_path / "dst"
    destination.mkdir()
    entries = [_entry(tmp_path / "one.txt"), _entry(tmp_path / "two.txt")]

    targets = app._copy_targets(str(destination), entries)

    assert targets == [
        (entries[0], destination / "one.txt"),
        (entries[1], destination / "two.txt"),
    ]


def test_move_targets_for_multiple_entries_require_existing_directory(tmp_path: Path) -> None:
    app = NorthToneApp()
    entries = [_entry(tmp_path / "one.txt"), _entry(tmp_path / "two.txt")]

    try:
        app._move_targets(str(tmp_path / "missing"), entries)
    except FileSystemError as exc:
        assert "destination directory does not exist" in str(exc)
    else:
        raise AssertionError("Expected FileSystemError")


def _entry(path: Path) -> FileEntry:
    return FileEntry(
        path=path,
        name=path.name,
        is_dir=False,
        is_file=True,
        is_symlink=False,
        is_executable=False,
        size=1,
        modified=datetime(2026, 4, 24, 12, 0),
    )
