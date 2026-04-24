"""Formatting helpers for sizes, dates, and paths."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

from northtone.core.filesystem import FileEntry


def format_size(size: int) -> str:
    """Format file size using B/KB/MB/GB units."""
    if size < 1024:
        return f"{size} B"

    units = ["KB", "MB", "GB"]
    value = float(size)
    for unit in units:
        value /= 1024.0
        if value < 1024.0 or unit == "GB":
            return f"{value:.1f} {unit}"

    return f"{value:.1f} GB"


def format_date(value: datetime) -> str:
    """Format datetime in a compact style."""
    return value.strftime("%y-%m-%d %H:%M")


def shorten_path(path: Path, width: int) -> str:
    """Shorten a path to fit a fixed width."""
    raw = str(path)
    if width <= 0:
        return ""
    if len(raw) <= width:
        return raw
    if width <= 3:
        return "." * width
    return f"...{raw[-(width - 3):]}"


def format_type(entry: FileEntry) -> str:
    """Format file type label for panel display."""
    if entry.name == ".." or entry.is_dir:
        return "DIR"
    if entry.is_symlink:
        return "LNK"
    if entry.is_executable:
        return "EXE"
    return "FILE"
