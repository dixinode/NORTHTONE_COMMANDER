"""Key mapping helpers for function keys and Esc-digit fallback."""

from __future__ import annotations

FKEY_ACTIONS: dict[str, str] = {
    "f1": "help",
    "f2": "user_menu",
    "f3": "view_file",
    "f4": "edit_file",
    "f5": "copy_item",
    "f6": "move_item",
    "f7": "mkdir",
    "f8": "delete_item",
    "f9": "top_menu",
    "f10": "quit_app",
}

ESC_DIGIT_ACTIONS: dict[str, str] = {
    "1": "help",
    "2": "user_menu",
    "3": "view_file",
    "4": "edit_file",
    "5": "copy_item",
    "6": "move_item",
    "7": "mkdir",
    "8": "delete_item",
    "9": "top_menu",
    "0": "quit_app",
}


def action_from_function_key(key: str) -> str | None:
    """Map an f-key token to an app action name."""
    return FKEY_ACTIONS.get(key.lower())


def action_from_esc_digit(key: str) -> str | None:
    """Map Esc-digit fallback token to an app action name."""
    return ESC_DIGIT_ACTIONS.get(key)
