# NorthTone Commander

**NorthTone Commander** is a retro two-panel file manager for macOS, inspired by the classic Norton Commander experience from the DOS era.

It keeps the familiar commander workflow: left and right panels, keyboard-first navigation, function-key actions, fast copy/move/delete operations, and a blue terminal UI. Under the hood it is a modern Python + Textual application.

## Download

The latest macOS build is available on the GitHub Releases page:

[Download NorthTone Commander v0.1.0](https://github.com/dixinode/NORTHTONE_COMMANDER/releases/tag/v0.1.0)

Available release files:

- `northtone-commander-0.1.0-macos-arm64.dmg` - drag-and-drop macOS app installer.
- `northtone-commander-0.1.0-macos-arm64.zip` - standalone terminal executable archive.

The `.app` opens Terminal and launches NorthTone Commander inside it, because this is a terminal UI application.

## Features

- Two equal-width file panels with active/inactive panel highlighting.
- Keyboard-first navigation with `Tab`, arrows, `Enter`, `Backspace`, and `Left`.
- Function key actions `F1` to `F10`.
- macOS-friendly fallback shortcuts with `Esc + 1..0`.
- Multi-select with `Space`; copy, move, and delete operate on marked items.
- File operations: copy, move/rename, create directory, delete.
- File viewing with `less`.
- File editing through `$EDITOR`, with `nano` as fallback.
- Session restore: left/right panel paths and active panel are remembered between launches.
- Classic blue retro terminal theme.
- Small, focused codebase with tests.

## Controls

| Key | Action |
|---|---|
| `Tab` | Switch active panel |
| `Up` / `Down` | Move cursor |
| `Enter` | Open directory or run executable file |
| `Backspace` / `Left` | Go to parent directory |
| `Space` | Mark / unmark current item |
| `F1` | Help |
| `F3` | View selected file with `less` |
| `F4` | Edit selected file with `$EDITOR` or `nano` |
| `F5` | Copy selected or marked items |
| `F6` | Move / rename selected or marked items |
| `F7` | Create directory |
| `F8` | Delete selected or marked items |
| `F9` | Top menu placeholder |
| `F10` | Quit |
| `Ctrl+Q` | Quit |
| `Ctrl+R` | Refresh active panel |

On Mac keyboards, function keys may require `Fn + F1` through `Fn + F10`.

Fallback shortcuts:

| Shortcut | Action |
|---|---|
| `Esc + 1` | Help |
| `Esc + 3` | View |
| `Esc + 4` | Edit |
| `Esc + 5` | Copy |
| `Esc + 6` | Move |
| `Esc + 7` | Mkdir |
| `Esc + 8` | Delete |
| `Esc + 0` | Quit |

## macOS Install

### Option 1: DMG

Download the `.dmg` from the release page, open it, and drag `NorthTone Commander.app` to `Applications`.

The app is currently ad-hoc signed, not notarized. If macOS Gatekeeper blocks the first launch, use:

```bash
xattr -dr com.apple.quarantine "/Applications/NorthTone Commander.app"
```

Then launch it again.

### Option 2: Standalone Executable

Download the `.zip`, unpack it, and run:

```bash
./northtone
```

### Option 3: From Source

```bash
git clone https://github.com/dixinode/NORTHTONE_COMMANDER.git
cd NORTHTONE_COMMANDER
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -e ".[dev]"
./run.sh
```

After installing the package, you can also run:

```bash
northtone
```

## Configuration

NorthTone Commander remembers the last left/right panel directories and active panel.

Session state is saved to:

```text
~/.config/northtone-commander/config.json
```

If a saved folder no longer exists, the app falls back to the user home directory.

## Build

Create the standalone executable:

```bash
./scripts/build_standalone_macos.sh
```

Create the release zip:

```bash
./scripts/package_release_macos.sh
```

Create the drag-and-drop DMG:

```bash
./scripts/build_dmg_macos.sh
```

Build outputs are written to:

```text
dist/
release/
```

## Test

```bash
pytest
```

Current test coverage focuses on filesystem operations, formatting helpers, session config, and app helper behavior.

## Project Structure

```text
northtone/
  app.py                 Main Textual application
  core/
    config.py            Session config load/save
    filesystem.py        Filesystem operations
  utils/
    formatter.py         Size/date/path/type formatting
    keymap.py            Function-key fallback mapping
  widgets/
    file_list.py         DataTable-based file list
    file_panel.py        One commander panel
    footer.py            Function key footer
  styles.tcss            Retro blue Textual theme
scripts/
  build_standalone_macos.sh
  build_dmg_macos.sh
  package_release_macos.sh
tests/
```

## Roadmap

- Real `F9` top menu.
- Built-in file viewer.
- Built-in text editor.
- Sorting modes and panel options.
- File search.
- Directory bookmarks.
- Archive support.
- More polished macOS app icon and notarized releases.

## License

MIT
