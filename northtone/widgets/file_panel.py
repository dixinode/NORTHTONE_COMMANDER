"""One file panel widget with path header and file list."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

from textual import events
from textual.app import ComposeResult
from textual.message import Message
from textual.widget import Widget
from textual.widgets import Static

from northtone.core.filesystem import FileEntry, FileSystem, FileSystemError
from northtone.utils.formatter import shorten_path
from northtone.widgets.file_list import FileList


class FilePanel(Widget):
    """A single panel that displays directory contents."""

    class PanelSelected(Message):
        """Posted when user interacts with this panel."""

        def __init__(self, panel: "FilePanel") -> None:
            self.panel = panel
            super().__init__()

    class ItemActivated(Message):
        """Posted when an entry is activated in this panel."""

        def __init__(self, panel: "FilePanel", entry: FileEntry) -> None:
            self.panel = panel
            self.entry = entry
            super().__init__()

    class ErrorRaised(Message):
        """Posted when this panel fails to refresh directory entries."""

        def __init__(self, panel: "FilePanel", error: str) -> None:
            self.panel = panel
            self.error = error
            super().__init__()

    def __init__(self, filesystem: FileSystem, start_path: Path, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.filesystem = filesystem
        self.current_path = start_path.expanduser()
        self._is_active = False

    def compose(self) -> ComposeResult:
        yield Static("", classes="panel-header")
        yield FileList(classes="file-list")

    def on_mount(self) -> None:
        self.refresh_entries()

    def on_resize(self, _event: events.Resize) -> None:
        self._update_header()

    def set_active(self, active: bool) -> None:
        self._is_active = active
        if active:
            self.add_class("active")
        else:
            self.remove_class("active")
        self._update_header()

    def focus_list(self) -> None:
        self.query_one(FileList).focus()

    def refresh_entries(self) -> None:
        try:
            items = self.filesystem.list_dir(self.current_path)
        except FileSystemError as exc:
            self.post_message(self.ErrorRaised(self, str(exc)))
            return

        entries: list[FileEntry] = []
        if self.current_path.parent != self.current_path:
            entries.append(
                FileEntry(
                    path=self.current_path.parent,
                    name="..",
                    is_dir=True,
                    is_file=False,
                    is_symlink=False,
                    is_executable=False,
                    size=0,
                    modified=datetime.now(),
                )
            )

        entries.extend(items)
        self.query_one(FileList).set_entries(entries)
        self._update_header()

    def go_to(self, path: Path) -> None:
        target = path.expanduser()
        if not target.is_dir():
            self.post_message(self.ErrorRaised(self, f"Cannot open directory: not a directory ({target})"))
            return
        self.current_path = target
        self.refresh_entries()

    def go_parent(self) -> None:
        if self.current_path.parent != self.current_path:
            self.go_to(self.current_path.parent)

    def get_selected_entry(self) -> FileEntry | None:
        return self.query_one(FileList).get_selected_entry()

    def get_operable_entries(self) -> list[FileEntry]:
        file_list = self.query_one(FileList)
        marked = file_list.get_marked_entries()
        if marked:
            return marked

        selected = file_list.get_selected_entry()
        if selected is None:
            return []
        return [selected]

    def clear_marks(self) -> None:
        self.query_one(FileList).clear_marks()

    def on_file_list_item_activated(self, message: FileList.ItemActivated) -> None:
        message.stop()
        self.post_message(self.ItemActivated(self, message.entry))

    def on_click(self, _event: events.Click) -> None:
        self.post_message(self.PanelSelected(self))

    def _update_header(self) -> None:
        width = max(self.size.width - 4, 10)
        header = self.query_one(".panel-header", Static)
        short_path = shorten_path(self.current_path, width)
        marker = "=>" if self._is_active else "  "
        header.update(f"{marker} {short_path}")
