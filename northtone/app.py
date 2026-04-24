"""NorthTone Commander Textual application."""

from __future__ import annotations

import os
import shlex
import subprocess
from pathlib import Path
from typing import Optional

from textual import events
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Container, Horizontal
from textual.screen import ModalScreen
from textual.timer import Timer
from textual.widgets import Button, Input, Label, Static

from northtone.core.config import AppConfig, SessionState
from northtone.core.filesystem import FileEntry, FileSystem, FileSystemError
from northtone.utils.keymap import action_from_esc_digit
from northtone.widgets.file_panel import FilePanel
from northtone.widgets.footer import CommandFooter


class MessageDialog(ModalScreen[None]):
    """Simple information dialog."""

    BINDINGS = [Binding("escape", "close", show=False), Binding("enter", "close", show=False)]

    def __init__(self, title: str, message: str) -> None:
        super().__init__()
        self.title = title
        self.message = message

    def compose(self) -> ComposeResult:
        with Container(classes="dialog"):
            yield Label(self.title, classes="dialog-title")
            yield Static(self.message, classes="dialog-body")
            with Horizontal(classes="dialog-buttons"):
                yield Button("OK", id="ok", variant="primary")

    def on_button_pressed(self, _event: Button.Pressed) -> None:
        self.dismiss(None)

    def action_close(self) -> None:
        self.dismiss(None)


class ConfirmDialog(ModalScreen[bool]):
    """Yes/no confirmation dialog."""

    BINDINGS = [Binding("escape", "cancel", show=False)]

    def __init__(self, title: str, message: str) -> None:
        super().__init__()
        self.title = title
        self.message = message

    def compose(self) -> ComposeResult:
        with Container(classes="dialog"):
            yield Label(self.title, classes="dialog-title")
            yield Static(self.message, classes="dialog-body")
            with Horizontal(classes="dialog-buttons"):
                yield Button("Cancel", id="cancel")
                yield Button("Confirm", id="confirm", variant="error")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        self.dismiss(event.button.id == "confirm")

    def action_cancel(self) -> None:
        self.dismiss(False)


class InputDialog(ModalScreen[Optional[str]]):
    """Text input dialog."""

    BINDINGS = [Binding("escape", "cancel", show=False)]

    def __init__(self, title: str, prompt: str, value: str = "") -> None:
        super().__init__()
        self.title = title
        self.prompt = prompt
        self.value = value

    def compose(self) -> ComposeResult:
        with Container(classes="dialog"):
            yield Label(self.title, classes="dialog-title")
            yield Static(self.prompt, classes="dialog-body")
            yield Input(value=self.value, id="input", classes="dialog-input")
            with Horizontal(classes="dialog-buttons"):
                yield Button("Cancel", id="cancel")
                yield Button("OK", id="ok", variant="primary")

    def on_mount(self) -> None:
        self.query_one(Input).focus()

    def on_input_submitted(self, event: Input.Submitted) -> None:
        self.dismiss(event.value.strip())

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "ok":
            value = self.query_one(Input).value.strip()
            self.dismiss(value)
            return
        self.dismiss(None)

    def action_cancel(self) -> None:
        self.dismiss(None)


class NorthToneApp(App[None]):
    """Main NorthTone Commander application."""

    CSS_PATH = Path(__file__).with_name("styles.tcss")
    TITLE = "NorthTone Commander"

    BINDINGS = [
        Binding("tab", "switch_panel", show=False),
        Binding("f1", "help", show=False),
        Binding("f2", "user_menu", show=False),
        Binding("f3", "view_file", show=False),
        Binding("f4", "edit_file", show=False),
        Binding("f5", "copy_item", show=False),
        Binding("f6", "move_item", show=False),
        Binding("f7", "mkdir", show=False),
        Binding("f8", "delete_item", show=False),
        Binding("f9", "top_menu", show=False),
        Binding("f10", "quit_app", show=False),
        Binding("ctrl+q", "quit_app", show=False),
        Binding("ctrl+r", "refresh_active", show=False),
        Binding("backspace", "go_parent", show=False),
        Binding("left", "go_parent", show=False),
    ]

    def __init__(self) -> None:
        super().__init__()
        self.config = AppConfig()
        self.session_state = self.config.load_session_state()
        self.filesystem = FileSystem()
        self._active_panel_id = self.session_state.active_panel_id
        self._esc_pending = False
        self._esc_timer: Timer | None = None

    def compose(self) -> ComposeResult:
        yield Static(self.config.app_name, id="topbar")
        with Horizontal(id="panes"):
            yield FilePanel(self.filesystem, self.session_state.left_path, id="left-panel")
            yield Static("", id="divider")
            yield FilePanel(self.filesystem, self.session_state.right_path, id="right-panel")
        yield CommandFooter(id="footer")

    def on_mount(self) -> None:
        self._sync_active_panel_state()

    async def on_key(self, event: events.Key) -> None:
        if event.key == "tab":
            self.action_switch_panel()
            event.stop()
            return

        if event.key == "escape":
            self._start_esc_sequence()
            event.stop()
            return

        if self._esc_pending:
            self._clear_esc_sequence()
            action = action_from_esc_digit(event.key)
            if action is not None:
                event.stop()
                await self.run_action(action)

    def on_file_panel_error_raised(self, message: FilePanel.ErrorRaised) -> None:
        self.call_after_refresh(self._show_error, message.error)

    def on_file_panel_panel_selected(self, message: FilePanel.PanelSelected) -> None:
        panel_id = message.panel.id
        if panel_id in {"left-panel", "right-panel"}:
            self._active_panel_id = panel_id
            self._sync_active_panel_state()

    async def on_file_panel_item_activated(self, message: FilePanel.ItemActivated) -> None:
        panel_id = message.panel.id
        if panel_id in {"left-panel", "right-panel"} and panel_id != self._active_panel_id:
            self._active_panel_id = panel_id
            self._sync_active_panel_state()
        await self._activate_entry(message.panel, message.entry)

    def action_switch_panel(self) -> None:
        self._active_panel_id = "right-panel" if self._active_panel_id == "left-panel" else "left-panel"
        self._sync_active_panel_state()

    def action_refresh_active(self) -> None:
        self.active_panel.refresh_entries()

    def action_go_parent(self) -> None:
        self.active_panel.go_parent()

    async def action_activate_item(self) -> None:
        entry = self.active_panel.get_selected_entry()
        if entry is None:
            return
        await self._activate_entry(self.active_panel, entry)

    def action_help(self) -> None:
        self.push_screen(
            MessageDialog(
                "Help",
                "Tab switch panel\n"
                "Space mark / unmark item\n"
                "Enter open dir / run executable\n"
                "Backspace or Left parent dir\n"
                "F5 copy marked/current, F6 move marked/current\n"
                "F7 mkdir, F8 delete marked/current\n"
                "F10 or Ctrl+Q quit\n"
                "Fallback: Esc + 1..0",
            )
        )

    def action_user_menu(self) -> None:
        self.push_screen(MessageDialog("User Menu", "MVP placeholder."))

    def action_top_menu(self) -> None:
        self.push_screen(MessageDialog("Top Menu", "MVP placeholder."))

    def action_quit_app(self) -> None:
        self.exit()

    def exit(self, result=None, return_code: int = 0, message=None) -> None:
        self._save_session_state(show_error=False)
        super().exit(result=result, return_code=return_code, message=message)

    async def action_view_file(self) -> None:
        entry = self._selected_regular_file()
        if entry is None:
            return
        await self._run_external_command(["less", str(entry.path)])
        self.active_panel.refresh_entries()

    async def action_edit_file(self) -> None:
        entry = self._selected_regular_file()
        if entry is None:
            return
        editor_raw = os.environ.get("EDITOR", "nano")
        editor_cmd = shlex.split(editor_raw)
        await self._run_external_command([*editor_cmd, str(entry.path)])
        self.active_panel.refresh_entries()

    def action_copy_item(self) -> None:
        self.run_worker(self._copy_item_flow(), group="file-op", exclusive=True, exit_on_error=False)

    async def _copy_item_flow(self) -> None:
        entries = self._operable_entries()
        if not entries:
            return

        default_dst = self._default_copy_destination(entries)
        prompt = "Destination path:" if len(entries) == 1 else "Destination directory:"
        user_input = await self.push_screen_wait(InputDialog("Copy", prompt, str(default_dst)))
        if not user_input:
            return

        try:
            targets = self._copy_targets(user_input, entries)
        except FileSystemError as exc:
            self._show_error(str(exc))
            return

        overwrite = any(self.filesystem.path_exists(destination) for _, destination in targets)
        message = self._operation_message("Copy", entries, targets)
        if overwrite:
            message += "\n\nExisting destinations will be replaced."
        confirmed = await self.push_screen_wait(ConfirmDialog("Confirm Copy", message))
        if not confirmed:
            return

        try:
            for entry, destination in targets:
                self.filesystem.copy(entry.path, destination, overwrite=self.filesystem.path_exists(destination))
        except FileSystemError as exc:
            self._show_error(str(exc))
            return

        self._finish_file_operation()

    def action_move_item(self) -> None:
        self.run_worker(self._move_item_flow(), group="file-op", exclusive=True, exit_on_error=False)

    async def _move_item_flow(self) -> None:
        entries = self._operable_entries()
        if not entries:
            return

        default_dst = self._default_move_destination(entries)
        prompt = "New name or destination path:" if len(entries) == 1 else "Destination directory:"
        user_input = await self.push_screen_wait(
            InputDialog("Move / Rename", prompt, str(default_dst))
        )
        if not user_input:
            return

        try:
            targets = self._move_targets(user_input, entries)
        except FileSystemError as exc:
            self._show_error(str(exc))
            return

        overwrite = any(self.filesystem.path_exists(destination) for _, destination in targets)
        message = self._operation_message("Move", entries, targets)
        if overwrite:
            message += "\n\nExisting destinations will be replaced."
        confirmed = await self.push_screen_wait(ConfirmDialog("Confirm Move", message))
        if not confirmed:
            return

        try:
            for entry, destination in targets:
                self.filesystem.move(entry.path, destination, overwrite=self.filesystem.path_exists(destination))
        except FileSystemError as exc:
            self._show_error(str(exc))
            return

        self._finish_file_operation()

    def action_mkdir(self) -> None:
        self.run_worker(self._mkdir_flow(), group="file-op", exclusive=True, exit_on_error=False)

    async def _mkdir_flow(self) -> None:
        user_input = await self.push_screen_wait(InputDialog("Create Directory", "Directory name:"))
        if not user_input:
            return

        target = Path(user_input).expanduser()
        if not target.is_absolute():
            target = self.active_panel.current_path / target

        try:
            self.filesystem.mkdir(target)
        except FileSystemError as exc:
            self._show_error(str(exc))
            return

        self._refresh_both_panels()

    def action_delete_item(self) -> None:
        self.run_worker(self._delete_item_flow(), group="file-op", exclusive=True, exit_on_error=False)

    async def _delete_item_flow(self) -> None:
        entries = self._operable_entries()
        if not entries:
            return

        names = self._format_entry_names(entries)
        confirmed = await self.push_screen_wait(
            ConfirmDialog("Confirm Delete", f"Delete {names}? This cannot be undone.")
        )
        if not confirmed:
            return

        try:
            for entry in entries:
                self.filesystem.delete(entry.path)
        except FileSystemError as exc:
            self._show_error(str(exc))
            return

        self._finish_file_operation()

    @property
    def left_panel(self) -> FilePanel:
        return self.query_one("#left-panel", FilePanel)

    @property
    def right_panel(self) -> FilePanel:
        return self.query_one("#right-panel", FilePanel)

    @property
    def active_panel(self) -> FilePanel:
        return self.left_panel if self._active_panel_id == "left-panel" else self.right_panel

    @property
    def inactive_panel(self) -> FilePanel:
        return self.right_panel if self._active_panel_id == "left-panel" else self.left_panel

    def _sync_active_panel_state(self) -> None:
        self.left_panel.set_active(self._active_panel_id == "left-panel")
        self.right_panel.set_active(self._active_panel_id == "right-panel")
        self.active_panel.focus_list()

    def _save_session_state(self, *, show_error: bool = True) -> None:
        try:
            state = SessionState(
                left_path=self.left_panel.current_path,
                right_path=self.right_panel.current_path,
                active_panel_id=self._active_panel_id,
            )
            self.config.save_session_state(state)
        except OSError as exc:
            if show_error:
                self._show_error(f"Cannot save config: {exc}")
        except Exception:
            if show_error:
                self._show_error("Cannot save config")

    async def _activate_entry(self, panel: FilePanel, entry: FileEntry) -> None:
        if entry.name == ".." or entry.is_dir:
            panel.go_to(entry.path)
            return

        if entry.is_executable:
            await self._run_external_command([str(entry.path)])
            panel.refresh_entries()

    def _selected_operable_entry(self) -> FileEntry | None:
        entry = self.active_panel.get_selected_entry()
        if entry is None:
            return None
        if entry.name == "..":
            self._show_error("Operation is not available for parent directory entry")
            return None
        return entry

    def _operable_entries(self) -> list[FileEntry]:
        entries = self.active_panel.get_operable_entries()
        if not entries:
            return []
        if any(entry.name == ".." for entry in entries):
            self._show_error("Operation is not available for parent directory entry")
            return []
        return entries

    def _selected_regular_file(self) -> FileEntry | None:
        entry = self._selected_operable_entry()
        if entry is None:
            return None
        if entry.is_dir:
            self._show_error("Cannot open file: selected item is a directory")
            return None
        return entry

    def _resolve_input_path(self, user_input: str) -> Path:
        candidate = Path(user_input).expanduser()
        if candidate.is_absolute():
            return candidate
        return self.active_panel.current_path / candidate

    def _resolve_copy_destination(self, user_input: str, entry: FileEntry) -> Path:
        destination = self._resolve_input_path(user_input)
        if destination.exists() and destination.is_dir():
            return destination / entry.name
        return destination

    def _resolve_move_destination(self, user_input: str, entry: FileEntry) -> Path:
        raw = user_input.strip()
        if "/" not in raw and not raw.startswith("~"):
            destination = self.active_panel.current_path / raw
        else:
            destination = self._resolve_input_path(raw)
        if destination.exists() and destination.is_dir():
            return destination / entry.name
        return destination

    def _default_copy_destination(self, entries: list[FileEntry]) -> Path:
        if len(entries) == 1:
            return self.inactive_panel.current_path / entries[0].name
        return self.inactive_panel.current_path

    def _default_move_destination(self, entries: list[FileEntry]) -> Path:
        if len(entries) == 1:
            return self.inactive_panel.current_path / entries[0].name
        return self.inactive_panel.current_path

    def _copy_targets(self, user_input: str, entries: list[FileEntry]) -> list[tuple[FileEntry, Path]]:
        if len(entries) == 1:
            entry = entries[0]
            return [(entry, self._resolve_copy_destination(user_input, entry))]
        destination_dir = self._resolve_batch_destination_dir(user_input, "Copy failed")
        return [(entry, destination_dir / entry.name) for entry in entries]

    def _move_targets(self, user_input: str, entries: list[FileEntry]) -> list[tuple[FileEntry, Path]]:
        if len(entries) == 1:
            entry = entries[0]
            return [(entry, self._resolve_move_destination(user_input, entry))]
        destination_dir = self._resolve_batch_destination_dir(user_input, "Move failed")
        return [(entry, destination_dir / entry.name) for entry in entries]

    def _resolve_batch_destination_dir(self, user_input: str, prefix: str) -> Path:
        destination = self._resolve_input_path(user_input)
        if not destination.exists():
            raise FileSystemError(f"{prefix}: destination directory does not exist ({destination})")
        if not destination.is_dir():
            raise FileSystemError(f"{prefix}: destination is not a directory ({destination})")
        return destination

    def _operation_message(
        self,
        verb: str,
        entries: list[FileEntry],
        targets: list[tuple[FileEntry, Path]],
    ) -> str:
        if len(entries) == 1:
            entry, destination = targets[0]
            return f"{verb} '{entry.name}' to '{destination}'?"
        names = self._format_entry_names(entries)
        destination_dir = targets[0][1].parent
        return f"{verb} {names} to '{destination_dir}'?"

    @staticmethod
    def _format_entry_names(entries: list[FileEntry]) -> str:
        if len(entries) == 1:
            return f"'{entries[0].name}'"
        return f"{len(entries)} selected items"

    def _refresh_both_panels(self) -> None:
        self.left_panel.refresh_entries()
        self.right_panel.refresh_entries()

    def _finish_file_operation(self) -> None:
        self.left_panel.clear_marks()
        self.right_panel.clear_marks()
        self._refresh_both_panels()

    def _start_esc_sequence(self) -> None:
        self._esc_pending = True
        if self._esc_timer is not None:
            self._esc_timer.stop()
        self._esc_timer = self.set_timer(1.0, self._clear_esc_sequence)

    def _clear_esc_sequence(self) -> None:
        self._esc_pending = False
        if self._esc_timer is not None:
            self._esc_timer.stop()
            self._esc_timer = None

    def _show_error(self, message: str) -> None:
        self.push_screen(MessageDialog("Error", message))

    async def _run_external_command(self, command: list[str]) -> None:
        try:
            with self.suspend():
                subprocess.run(command, check=False)
        except FileNotFoundError:
            self._show_error(f"Cannot launch command: {command[0]} not found")
        except OSError as exc:
            self._show_error(f"Cannot launch command: {exc}")


def main() -> None:
    app = NorthToneApp()
    app.run()


if __name__ == "__main__":
    main()
