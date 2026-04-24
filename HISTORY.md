# NorthTone Commander - Project History

Last updated: 2026-04-24

## Project Summary

NorthTone Commander is a macOS terminal-based two-panel file manager inspired by classic Norton Commander for DOS.

Tech stack:

- Python 3.9+
- Textual / Rich TUI
- PyInstaller for standalone macOS executable
- `hdiutil` for DMG packaging
- GitHub repository: https://github.com/dixinode/NORTHTONE_COMMANDER
- Latest release: https://github.com/dixinode/NORTHTONE_COMMANDER/releases/tag/v0.1.0

## Current Repository State

GitHub repo:

```text
https://github.com/dixinode/NORTHTONE_COMMANDER
```

Remote:

```text
origin https://github.com/dixinode/NORTHTONE_COMMANDER.git
```

Recent commits:

```text
b164e69 Bundle stylesheet at PyInstaller root
f213dc8 Fix bundled stylesheet path
592b240 Add macOS app icon
c713fbe Improve GitHub project README
a73823d Add macOS DMG packaging
0347776 Initial NorthTone Commander release
```

Release artifacts:

```text
release/northtone-commander-0.1.0-macos-arm64.dmg
release/northtone-commander-0.1.0-macos-arm64.zip
```

The GitHub release `v0.1.0` has both artifacts uploaded.

## Implemented App Features

- Two-panel commander-style file manager.
- Active/inactive panel highlighting.
- Keyboard navigation:
  - `Tab` switches active panel.
  - Arrow keys move cursor.
  - `Enter` opens directories or runs executable files.
  - `Backspace` / `Left` goes to parent directory.
  - `Ctrl+R` refreshes active panel.
  - `Ctrl+Q`, `F10`, or `Esc+0` quits.
- Function key actions:
  - `F1` Help
  - `F3` View file with `less`
  - `F4` Edit file with `$EDITOR`, fallback `nano`
  - `F5` Copy
  - `F6` Move / rename
  - `F7` Create directory
  - `F8` Delete
  - `F9` Top menu placeholder
- macOS fallback shortcuts:
  - `Esc + 1..0`
- Multi-select:
  - `Space` marks/unmarks current item.
  - `[x]` is shown for marked items.
  - Copy, move, and delete operate on marked items.
  - If nothing is marked, operations use the current cursor row.
  - After successful copy/move/delete, marks are cleared on both panels.
- Session restore:
  - Saves left panel path, right panel path, and active panel.
  - Config file: `~/.config/northtone-commander/config.json`
  - Missing saved folders fall back to home directory.
- Retro blue Textual UI.

## Important Fixes Made

### External command launch

Fixed `F3`, `F4`, and executable launch. Textual `App.suspend()` is a regular context manager in the installed version, so the code now uses:

```python
with self.suspend():
    subprocess.run(command, check=False)
```

### Safer filesystem operations

`FileSystem.copy()` and `FileSystem.move()` now support explicit overwrite handling and reject dangerous cases:

- destination already exists unless overwrite is confirmed;
- source and destination are the same;
- copying/moving a directory inside itself;
- missing destination parent.

### Python version metadata

Project metadata changed to Python `>=3.9` because the local `.venv` is Python 3.9.6 and Textual supports it.

### macOS run script

`run.sh` now uses the project venv directly:

```bash
.venv/bin/python -m northtone.app
```

This avoids problems where `python` or `python3` points to the wrong system interpreter.

### Standalone CSS packaging

There were DMG/app launch failures:

```text
StylesheetError: unable to read CSS file .../_MEIxxxx/styles.tcss
```

Fixes:

- `NorthToneApp.CSS_PATH` is now:

```python
CSS_PATH = Path(__file__).with_name("styles.tcss")
```

- PyInstaller now includes `styles.tcss` in both locations:

```bash
--add-data "northtone/styles.tcss:."
--add-data "northtone/styles.tcss:northtone"
```

The standalone binary was smoke-tested after the final fix:

```text
running_after_2s= True
stylesheet_error= False
```

### App icon

User generated `northtone_icon.png` in the repo root.

The DMG build script now converts it to `.icns` using `sips` and `iconutil`, places it in the app bundle, and sets:

```text
CFBundleIconFile = NorthToneCommander
```

## Packaging / Build Scripts

Standalone executable:

```bash
./scripts/build_standalone_macos.sh
```

Release zip:

```bash
./scripts/package_release_macos.sh
```

DMG app installer:

```bash
./scripts/build_dmg_macos.sh
```

Generated outputs:

```text
dist/northtone
dist/NorthTone Commander.app
release/northtone-commander-0.1.0-macos-arm64.zip
release/northtone-commander-0.1.0-macos-arm64.dmg
```

The `.app` opens Terminal and runs:

```text
NorthTone Commander.app/Contents/Resources/northtone
```

This is intentional because Textual needs a real terminal session.

## Tests / Verification

Current test command:

```bash
.venv/bin/python -m pytest
```

Latest known result:

```text
26 passed
```

Other verification used:

```bash
PYTHONPYCACHEPREFIX=/tmp/northtone-pycache .venv/bin/python -m compileall northtone tests
codesign --verify --deep --strict --verbose=2 "dist/NorthTone Commander.app"
hdiutil imageinfo release/northtone-commander-0.1.0-macos-arm64.dmg
```

## GitHub Work Done

Installed and configured GitHub CLI (`gh`) via Homebrew.

Authenticated as:

```text
dixinode
```

Created public GitHub repo:

```text
https://github.com/dixinode/NORTHTONE_COMMANDER
```

Created release:

```text
v0.1.0
```

Updated GitHub repo metadata:

Description:

```text
Retro two-panel Norton Commander-inspired file manager for macOS, built with Python and Textual.
```

Topics:

```text
file-manager, macos, norton-commander, python, retro, terminal, textual, tui
```

Homepage points to the release page.

## Known Notes

- The app is ad-hoc signed, not Apple-notarized.
- If Gatekeeper blocks the app after DMG install, user may need:

```bash
xattr -dr com.apple.quarantine "/Applications/NorthTone Commander.app"
```

- `.DS_Store`, `.venv`, `build`, `dist`, `release`, `*.spec`, and egg-info are ignored by git.
- `F9 Top` is still only a placeholder.
- The project has `SESSION_HISTORY.md` from an earlier session and this newer `HISTORY.md` as the main continuation handoff.

## Good Next Tasks

1. Test freshly downloaded DMG after the final CSS root-bundle fix.
2. Add a real `F9` top menu.
3. Add a built-in viewer instead of relying only on `less`.
4. Add a built-in editor or better editor selection UI.
5. Add sorting modes for name/date/size/type.
6. Add quick search/filter in the active panel.
7. Add bookmarks / favorite folders.
8. Add a polished DMG background and nicer installer window layout.
9. Consider Apple Developer ID signing and notarization later.
