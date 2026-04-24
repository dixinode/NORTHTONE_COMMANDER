from __future__ import annotations

from datetime import datetime
from pathlib import Path

from northtone.utils.formatter import format_date, format_size, shorten_path


def test_format_size_bytes() -> None:
    assert format_size(999) == "999 B"


def test_format_size_kb() -> None:
    assert format_size(2048) == "2.0 KB"


def test_format_size_mb() -> None:
    assert format_size(5 * 1024 * 1024) == "5.0 MB"


def test_format_size_gb() -> None:
    assert format_size(3 * 1024 * 1024 * 1024) == "3.0 GB"


def test_format_date_compact() -> None:
    value = datetime(2026, 4, 17, 8, 30)
    assert format_date(value) == "26-04-17 08:30"


def test_shorten_path_no_truncation() -> None:
    assert shorten_path(Path("/tmp"), 20) == "/tmp"


def test_shorten_path_with_truncation() -> None:
    shortened = shorten_path(Path("/Users/example/very/long/path/here"), 12)
    assert shortened.startswith("...")
    assert len(shortened) == 12
