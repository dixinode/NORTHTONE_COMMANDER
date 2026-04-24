"""Bottom command hint line."""

from __future__ import annotations

from textual.widgets import Static


class CommandFooter(Static):
    """Shows NC-style function key hints."""

    DEFAULT_TEXT = (
        "Space Mark  F1 Help  F3 View  F4 Edit  F5 Copy  "
        "F6 Move  F7 Mkdir  F8 Delete  F9 Top  F10 Quit"
    )

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(self.DEFAULT_TEXT, *args, **kwargs)
