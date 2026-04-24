# NorthTone Commander — Technical Specification

**Document version:** 1.0  
**Date:** April 17, 2026  
**Application name:** `NorthTone Commander`  
**Short name:** `NTC`  
**Target platform:** macOS  
**Application type:** terminal-based TUI application  
**Goal:** a minimal but fully working two-panel file manager inspired by classic Norton Commander 5.x.

---

## 1. Project Overview

**NorthTone Commander** is a modern minimalist implementation of the classic **Norton Commander 5.x** concept for the macOS terminal.

The application should visually and behaviorally resemble the original Norton Commander:

- two independent file panels;
- active and inactive panel states;
- keyboard-driven navigation;
- support for function keys `F1–F10`;
- fallback shortcuts via `Esc + 1…0`;
- mouse support;
- classic blue retro terminal style;
- file operations implemented in Python.

The application should be simple, fast, stable, and suitable for future extension.

---

## 2. Target Platform

The application must run in the macOS terminal:

- macOS Tahoe;
- macOS Sequoia;
- macOS Ventura;
- newer macOS versions, as long as a compatible Python version is available.

Default working directory:

```text
~/
```

Terminal window title:

```text
NorthTone Commander
```

---

## 3. Technology Stack

### 3.1. Core Technologies

| Component | Requirement |
|---|---|
| Programming language | Python 3.9+ |
| TUI framework | Textual 0.85+ or the latest stable version |
| Path handling | `pathlib` |
| File operations | `shutil`, `os`, `pathlib` |
| UI rendering | Textual + Rich |
| Testing | `pytest` |

### 3.2. Allowed Dependencies

Required:

```bash
textual
```

Development dependencies:

```bash
textual[dev]
pytest
```

Additional Python standard-library modules:

```python
pathlib
shutil
os
platform
subprocess
dataclasses
datetime
typing
```

### 3.3. Dependency Restrictions

The MVP must not use external dependencies other than:

- `textual`;
- `rich`, which is already part of the Textual ecosystem;
- `pytest` for testing.

---

## 4. Development Installation

```bash
python3 -m venv .venv
source .venv/bin/activate

pip install --upgrade pip
pip install textual[dev] pytest
```

Run the application:

```bash
python -m northtone.app
```

Or use the helper script:

```bash
./run.sh
```

---

## 5. MVP Core Features

## 5.1. General Interface

The application must provide a classic two-panel interface:

```text
┌──────────────────────────── NorthTone Commander ────────────────────────────┐
│ /Users/user/projects                         │ /Users/user/downloads        │
├──────────────────────────────────────────────┼─────────────────────────────┤
│ ..                                           │ ..                          │
│ src/                                         │ file.txt                    │
│ README.md                                    │ archive.zip                 │
│ pyproject.toml                               │ image.png                   │
│                                              │                             │
├──────────────────────────────────────────────┴─────────────────────────────┤
│ F1 Help  F2 Menu  F3 View  F4 Edit  F5 Copy  F6 Move  F7 Mkdir  F8 Del ... │
└────────────────────────────────────────────────────────────────────────────┘
```

### Interface Requirements

- two panels of equal width;
- panels separated by a vertical divider;
- each panel displays its current path;
- long paths must be shortened gracefully;
- the active panel must be visually brighter or more prominent;
- the current row must be highlighted;
- the bottom line must display `F1–F10` hints;
- the top line must display the application name;
- classic NC-style blue theme support;
- proper behavior in dark terminal environments.

---

## 5.2. File Panel Contents

Each panel must display the contents of its current directory.

### Each entry must display

| Field | Description |
|---|---|
| Name | File or directory name |
| Size | File size in human-readable format |
| Date | Last modification date |
| Type / attributes | Directory, regular file, executable file, symlink, etc. |

### Display Rules

- directories should be displayed above files;
- the `..` entry must always be displayed first if a parent directory exists;
- long file names must be truncated gracefully;
- sizes must be formatted as `B`, `KB`, `MB`, `GB`;
- dates must be formatted compactly;
- access errors must be shown as clear user-facing messages.

---

## 6. Keyboard Shortcuts

Keyboard control is a mandatory part of the MVP.

On macOS, the primary way to use function keys is:

```text
Fn + F1 … Fn + F10
```

Fallback option:

```text
Esc + 1 … Esc + 0
```

---

## 6.1. Main F1–F10 Commands

| Action | Primary key | Fallback | Description |
|---|---:|---:|---|
| Help | `Fn + F1` | `Esc + 1` | Show a simple help message for now |
| User menu | `Fn + F2` | `Esc + 2` | Placeholder |
| View file | `Fn + F3` | `Esc + 3` | Open file using `less` or built-in viewer |
| Edit file | `Fn + F4` | `Esc + 4` | Open file in `$EDITOR` |
| Copy | `Fn + F5` | `Esc + 5` | Copy selected file or directory |
| Move / Rename | `Fn + F6` | `Esc + 6` | Move or rename selected item |
| Mkdir | `Fn + F7` | `Esc + 7` | Create a directory |
| Delete | `Fn + F8` | `Esc + 8` | Delete with confirmation |
| Top menu | `Fn + F9` | `Esc + 9` | Not implemented in MVP |
| Quit | `Fn + F10` | `Esc + 0`, `Ctrl + Q` | Exit the application |

---

## 6.2. Additional Keys

| Key | Action |
|---|---|
| `Tab` | Switch active panel |
| `↑` | Move cursor up |
| `↓` | Move cursor down |
| `Enter` | Enter directory or execute file if executable |
| `Backspace` | Go to parent directory |
| `←` | Go to parent directory |
| `Ctrl + R` | Refresh active panel |
| `Ctrl + Q` | Exit application |

---

## 6.3. Mouse Support

Basic mouse support is required.

| Mouse action | Result |
|---|---|
| Single click on item | Select item |
| Double click on directory | Enter directory |
| Double click on file | Same behavior as `Enter` |

---

## 7. File Operations

All file operations must be implemented in Python using:

- `pathlib`;
- `shutil`;
- `os`.

All operations are executed with the current user's permissions.

---

## 7.1. Required MVP Operations

| Operation | Key | Requirement |
|---|---:|---|
| Directory listing | Automatic | Display current directory contents |
| Copy | `F5` | Copy file or directory |
| Move | `F6` | Move selected item |
| Rename | `F6` | Rename if destination is in the same directory |
| Create directory | `F7` | Create a new directory |
| Delete | `F8` | Delete with confirmation |
| View file | `F3` | Use `less` or built-in viewer |
| Edit file | `F4` | Use `$EDITOR` |

---

## 7.2. Copy

When copying:

- source is taken from the active panel;
- default destination is the current directory of the opposite panel;
- show a confirmation dialog before copying;
- show a ProgressBar for large files when practical;
- refresh both panels after completion.

For files use:

```python
shutil.copy2()
```

For directories use:

```python
shutil.copytree()
```

---

## 7.3. Move and Rename

When `F6` is pressed:

- if the user enters a new name in the same directory, perform rename;
- if the user enters a path in another directory, perform move;
- refresh both panels after the operation.

Use:

```python
shutil.move()
```

---

## 7.4. Delete

When `F8` is pressed:

- always show a confirmation dialog;
- confirmation must be explicit;
- accidental keypress must not immediately delete anything;
- on error, show a clear message.

For files:

```python
Path.unlink()
```

For directories:

```python
shutil.rmtree()
```

---

## 7.5. Create Directory

When `F7` is pressed:

- show an input dialog;
- user enters the new directory name;
- directory is created in the active panel's current directory;
- panel is refreshed after creation.

Use:

```python
Path.mkdir()
```

---

## 7.6. View File

When `F3` is pressed:

MVP option:

```bash
less <file>
```

Alternative option:

- built-in Textual viewer;
- separate viewer screen;
- exit viewer with `Esc`.

For MVP, using external `less` is acceptable.

---

## 7.7. Edit File

When `F4` is pressed:

- open the file in the editor defined by `$EDITOR`;
- if `$EDITOR` is not set, use `nano`;
- if `code` is available, Visual Studio Code may be supported as an optional behavior.

Editor selection logic:

```python
editor = os.environ.get("EDITOR", "nano")
```

Launch:

```python
subprocess.run([editor, str(path)])
```

---

## 8. Error Handling

Any file operation may fail. The application must not crash.

### Errors must be shown clearly

Example error cases:

- permission denied;
- file already exists;
- path does not exist;
- directory is not empty;
- system file cannot be removed;
- file cannot be opened;
- copy operation failed.

### Message Format

Messages should be short and understandable:

```text
Copy failed: permission denied
```

or:

```text
Cannot open file: file does not exist
```

---

## 9. Project Architecture

Recommended project structure:

```text
northtone-commander/
├── northtone/
│   ├── __init__.py
│   ├── app.py              # Main NorthToneApp class
│   ├── widgets/
│   │   ├── __init__.py
│   │   ├── file_panel.py   # Custom widget for one panel
│   │   ├── file_list.py    # File table / list widget
│   │   └── footer.py       # Bottom F1–F10 command line
│   ├── core/
│   │   ├── __init__.py
│   │   ├── filesystem.py   # All file operations
│   │   └── config.py       # Application settings
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── keymap.py       # Fn/Esc shortcut handling
│   │   └── formatter.py    # Size, date, and path formatting
│   └── styles.tcss         # Textual styles, classic NC blue theme
├── tests/
│   ├── test_filesystem.py
│   └── test_formatter.py
├── pyproject.toml
├── README.md
├── tech_spec.md            # This file
└── run.sh
```

---

## 10. Main Classes

## 10.1. `NorthToneApp`

File:

```text
northtone/app.py
```

Responsibilities:

- start the Textual application;
- create the layout;
- manage the active panel;
- handle global shortcuts;
- invoke file operations;
- show dialogs and errors.

---

## 10.2. `FilePanel`

File:

```text
northtone/widgets/file_panel.py
```

Responsibilities:

- store the panel's current path;
- display the panel header;
- contain the `FileList`;
- refresh the file list;
- know whether the panel is active.

---

## 10.3. `FileList`

File:

```text
northtone/widgets/file_list.py
```

Responsibilities:

- display a list of `FileEntry` objects;
- support cursor movement;
- handle item selection;
- emit events on Enter / double-click.

Can be implemented using:

- `DataTable`;
- or `ListView`.

Recommended MVP option:

```text
DataTable
```

---

## 10.4. `FileSystem`

File:

```text
northtone/core/filesystem.py
```

Responsibilities:

- all filesystem access;
- no UI logic;
- clean business logic only.

Minimum methods:

```python
list_dir(path: Path) -> list[FileEntry]
copy(src: Path, dst: Path) -> None
move(src: Path, dst: Path) -> None
delete(path: Path) -> None
mkdir(path: Path) -> None
```

---

## 10.5. `FileEntry`

Recommended dataclass:

```python
from dataclasses import dataclass
from pathlib import Path
from datetime import datetime

@dataclass
class FileEntry:
    path: Path
    name: str
    is_dir: bool
    is_file: bool
    is_symlink: bool
    is_executable: bool
    size: int
    modified: datetime
```

---

## 11. Step-by-Step Implementation Plan for an AI Agent

## Stage 0 — Project Setup

Tasks:

- create project structure;
- create `pyproject.toml`;
- create virtual environment;
- install Textual;
- create basic `NorthToneApp`;
- verify that an empty application starts.

Expected result:

```bash
python -m northtone.app
```

starts an empty Textual application.

---

## Stage 1 — Basic TUI

Tasks:

- create two panels;
- place panels horizontally;
- add vertical divider;
- add header;
- add footer with `F1–F10` hints;
- implement active panel switching via `Tab`.

Expected result:

- two empty panels are visible;
- active panel is highlighted;
- `Tab` switches focus.

---

## Stage 2 — Filesystem Layer

Tasks:

- implement `FileEntry`;
- implement `FileSystem.list_dir()`;
- implement sorting: directories above files;
- implement size retrieval;
- implement modification date retrieval;
- implement access error handling.

Expected result:

- application can retrieve a file list from `~/`.

---

## Stage 3 — FileList Widget

Tasks:

- implement `FileList` using `DataTable` or `ListView`;
- display name, size, date, and type;
- add `..` row;
- add current row highlighting;
- synchronize cursor with selected item.

Expected result:

- both panels display real files;
- user can move the cursor up and down with arrow keys.

---

## Stage 4 — Shortcuts and Navigation

Tasks:

- implement `Fn + F1 … Fn + F10`;
- implement fallback `Esc + 1 … Esc + 0`;
- implement `Enter`;
- implement `Backspace`;
- implement `←`;
- implement `Ctrl + R`;
- implement `Ctrl + Q`.

Expected result:

- user can navigate directories;
- user can switch panels;
- user can refresh the file list;
- user can exit the application.

---

## Stage 5 — File Operations

Tasks:

- `F5` — copy;
- `F6` — move / rename;
- `F7` — create directory;
- `F8` — delete;
- `F3` — view file;
- `F4` — edit file;
- refresh panels after operations;
- handle errors.

Expected result:

- all basic file operations work for files and directories.

---

## Stage 6 — UI Polish

Tasks:

- add classic blue theme;
- improve active panel highlighting;
- improve footer;
- add clean error messages;
- add confirmation dialogs;
- add input dialogs;
- add basic mouse support.

Expected result:

- the application visually resembles Norton Commander;
- navigation feels intuitive;
- errors do not break the application.

---

## Stage 7 — Testing and Launch

Tasks:

- write tests for `FileSystem`;
- write tests for size formatting;
- write tests for date formatting;
- verify launch on macOS;
- verify behavior in Terminal.app;
- verify behavior in iTerm2;
- verify function keys;
- verify fallback shortcuts via `Esc + digit`.

---

## 12. Styles and Visual Direction

Stylesheet file:

```text
northtone/styles.tcss
```

### Main Colors

| Element | Color |
|---|---|
| Panel background | `#000080` |
| Active panel background | slightly brighter blue |
| Text | light gray / white |
| Selected row | white text on bright blue background |
| Borders | light blue / gray |
| Footer | blue background, white labels |
| Errors | contrasting color, but not visually aggressive |

### Style Requirements

- overall look should be close to Norton Commander 5.0;
- monospaced font;
- high contrast;
- minimal decoration;
- functionality is more important than visual beauty;
- visual style should feel retro, but clean.

Example CSS direction:

```css
Screen {
    background: #000080;
    color: white;
}

FilePanel {
    background: #000080;
    border: solid #00ffff;
}

FilePanel.active {
    border: heavy #ffffff;
}

DataTable {
    background: #000080;
    color: white;
}

DataTable > .datatable--cursor {
    background: white;
    color: #000080;
}
```

---

## 13. macOS-Specific Requirements

### 13.1. Function Keys

On macOS, function keys often require:

```text
Fn + F1 … Fn + F10
```

Therefore the application must support:

- regular key events such as `f1`, `f2`, `f3`, etc.;
- fallback shortcuts via `Esc + 1 … Esc + 0`.

---

## 13.2. Filesystem Safety

The application works only with the current user's permissions.

Do not:

- bypass SIP;
- request root access;
- change permissions of system files;
- modify protected system directories.

If access is denied, show an error message.

---

## 13.3. Extended Attributes

macOS uses extended attributes (`xattr`).

When copying files, metadata should not be destroyed unnecessarily.

Recommended option:

```python
shutil.copy2()
```

This is sufficient for the MVP.

---

## 13.4. Terminals to Test

Minimum required testing:

- Terminal.app;
- iTerm2.

Recommended additional testing:

- VS Code integrated terminal.

---

## 14. Out of Scope for MVP

Do not implement the following in the MVP:

- built-in editor;
- FTP;
- SFTP;
- plugins;
- archive support;
- `.zip`, `.rar`, `.7z` handling;
- full-text file search;
- complex bookmarks;
- tabs;
- themes other than the main NC-blue theme;
- drag & drop;
- complex configuration file;
- dedicated Windows/Linux support.

---

## 15. Possible Post-MVP Improvements

After the MVP is complete, the following features can be added:

- built-in viewer;
- built-in text editor;
- file search;
- full-text search;
- directory bookmarks;
- user themes;
- configuration file;
- archive support;
- quick path jump;
- Norton Commander-style command line;
- command history;
- panel synchronization;
- directory comparison;
- batch operations;
- terminal drag & drop where supported.

---

## 16. MVP Acceptance Criteria

The MVP is considered complete when:

- the application starts on macOS;
- two file panels are displayed;
- both panels show real directories;
- panels can be switched with `Tab`;
- cursor can be moved with arrow keys;
- directories can be opened with `Enter`;
- parent directory can be opened with `Backspace`;
- `F5`, `F6`, `F7`, and `F8` work;
- the application can exit via `F10`, `Esc + 0`, or `Ctrl + Q`;
- fallback shortcuts `Esc + 1…0` work;
- errors are displayed without crashing the application;
- the interface visually resembles Norton Commander.

---

## 17. Code Quality Requirements

The code must be:

- readable;
- modular;
- free of chaotic logic inside UI classes;
- clearly separated between UI and filesystem operations;
- typed with type hints;
- implemented with clear class and method names;
- covered by basic tests for filesystem logic;
- free of unnecessary global state.

---

## 18. Recommended `pyproject.toml`

```toml
[project]
name = "northtone-commander"
version = "0.1.0"
description = "A minimal Norton Commander inspired two-panel terminal file manager for macOS."
readme = "README.md"
requires-python = ">=3.9"
dependencies = [
    "textual>=0.85.0"
]

[project.optional-dependencies]
dev = [
    "textual[dev]",
    "pytest"
]

[tool.pytest.ini_options]
testpaths = ["tests"]
```

---

## 19. Recommended `run.sh`

```bash
#!/usr/bin/env bash
set -e

source .venv/bin/activate
python -m northtone.app
```

After creating the file:

```bash
chmod +x run.sh
```

---

## 20. Short Summary for an AI Coding Agent

Create a terminal-based file manager called **NorthTone Commander** using Python + Textual for macOS.

Core idea:

- two panels;
- classic Norton Commander visual style;
- control via `Fn + F1…F10`;
- fallback control via `Esc + 1…0`;
- basic file operations;
- blue retro theme;
- clean architecture;
- minimal dependencies;
- working MVP without unnecessary extra features.

The first priority is to deliver a stable working two-panel file manager.  
Visual polish and advanced features come after the MVP is functional.
