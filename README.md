# NorthTone Commander

NorthTone Commander (NTC) is a minimal two-panel terminal file manager inspired by classic Norton Commander.

## Features

- Two equal-width file panels with active/inactive state.
- Keyboard-first navigation (`Tab`, arrows, `Enter`, `Backspace`).
- Multi-select with `Space`; copy, move, and delete operate on marked items.
- `F1` to `F10` commands plus fallback `Esc` + digit shortcuts.
- Core file operations: copy, move/rename, mkdir, delete.
- File view (`less`) and edit (`$EDITOR`, fallback `nano`).
- Session config remembers left/right panel folders between launches.
- Retro blue Textual UI.

## Requirements

- Python 3.9+
- macOS terminal (Terminal.app, iTerm2, or similar)

## Install

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install textual[dev] pytest
```

## Run

```bash
python -m northtone.app
```

or:

```bash
./run.sh
```

After installing the package, you can also run:

```bash
northtone
```

Session state is saved to:

```text
~/.config/northtone-commander/config.json
```

## macOS Install

Install into your user Python environment:

```bash
./scripts/install_macos.sh
```

Create a standalone executable in `dist/northtone`:

```bash
./scripts/build_standalone_macos.sh
```

Create a drag-and-drop DMG with `NorthTone Commander.app`:

```bash
./scripts/build_dmg_macos.sh
```

You can also double-click `NorthTone Commander.command` in Finder to run the app from this project folder.

## Test

```bash
pytest
```
