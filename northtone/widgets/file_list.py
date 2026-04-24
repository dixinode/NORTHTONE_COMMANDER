"""File list widget based on Textual DataTable."""

from __future__ import annotations

from rich.text import Text
from textual import events
from textual.message import Message
from textual.widgets import DataTable

from northtone.core.filesystem import FileEntry
from northtone.utils.formatter import format_date, format_size, format_type


class FileList(DataTable):
    """A table widget that displays file entries."""

    class ItemActivated(Message):
        """Posted when the user activates an item."""

        def __init__(self, sender: "FileList", entry: FileEntry) -> None:
            self.entry = entry
            super().__init__()

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.cursor_type = "row"
        self.show_header = True
        self.show_row_labels = False
        self.zebra_stripes = False
        self.entries: list[FileEntry] = []
        self.marked_paths: set[str] = set()

    def on_mount(self) -> None:
        self.add_columns("Name", "Size", "Date", "Type")

    def set_entries(self, entries: list[FileEntry]) -> None:
        self.entries = entries
        existing_paths = {self._entry_key(entry) for entry in entries if entry.name != ".."}
        self.marked_paths.intersection_update(existing_paths)
        self.clear(columns=False)
        for entry in entries:
            name = self._format_name(entry)
            size = "" if entry.name == ".." or entry.is_dir else format_size(entry.size)
            date = "" if entry.name == ".." else format_date(entry.modified)
            kind = format_type(entry)
            self.add_row(name, size, date, kind)

        if entries:
            first_row = 1 if len(entries) > 1 and entries[0].name == ".." else 0
            self.move_cursor(row=first_row)

    def get_selected_entry(self) -> FileEntry | None:
        row_index = self.cursor_row
        if row_index is None:
            return None
        if row_index < 0 or row_index >= len(self.entries):
            return None
        return self.entries[row_index]

    def get_marked_entries(self) -> list[FileEntry]:
        """Return marked entries in their current display order."""
        return [entry for entry in self.entries if self.is_marked(entry)]

    def is_marked(self, entry: FileEntry) -> bool:
        if entry.name == "..":
            return False
        return self._entry_key(entry) in self.marked_paths

    def on_key(self, event: events.Key) -> None:
        if event.key == "enter":
            entry = self.get_selected_entry()
            if entry is not None:
                self.post_message(self.ItemActivated(self, entry))
            event.stop()
        elif event.key == "space":
            self.toggle_current_mark()
            event.stop()

    def on_click(self, event: events.Click) -> None:
        chain = getattr(event, "chain", 1)
        if chain >= 2:
            entry = self.get_selected_entry()
            if entry is not None:
                self.post_message(self.ItemActivated(self, entry))

    def toggle_current_mark(self) -> None:
        entry = self.get_selected_entry()
        if entry is None or entry.name == "..":
            return

        key = self._entry_key(entry)
        if key in self.marked_paths:
            self.marked_paths.remove(key)
        else:
            self.marked_paths.add(key)
        self._redraw_entries(keep_row=self.cursor_row)

    def clear_marks(self) -> None:
        if not self.marked_paths:
            return
        self.marked_paths.clear()
        self._redraw_entries(keep_row=self.cursor_row)

    def _redraw_entries(self, keep_row: int | None = None) -> None:
        entries = self.entries
        self.clear(columns=False)
        for entry in entries:
            name = self._format_name(entry)
            size = "" if entry.name == ".." or entry.is_dir else format_size(entry.size)
            date = "" if entry.name == ".." else format_date(entry.modified)
            kind = format_type(entry)
            self.add_row(name, size, date, kind)

        if entries:
            row = keep_row if keep_row is not None else 0
            row = max(0, min(row, len(entries) - 1))
            self.move_cursor(row=row)

    def _format_name(self, entry: FileEntry) -> Text:
        marker = "[x] " if self.is_marked(entry) else "    "
        if entry.name == "..":
            return Text("..", style="bold cyan")
        if entry.is_dir:
            return Text(f"{marker}{entry.name}/", style="bold cyan")
        if entry.is_symlink:
            return Text(f"{marker}{entry.name}", style="bright_magenta")
        if entry.is_executable:
            return Text(f"{marker}{entry.name}", style="bold bright_green")
        return Text(f"{marker}{entry.name}")

    @staticmethod
    def _entry_key(entry: FileEntry) -> str:
        return str(entry.path)
