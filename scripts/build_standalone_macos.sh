#!/usr/bin/env bash
set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PYTHON_BIN="${PYTHON_BIN:-$PROJECT_DIR/.venv/bin/python}"

cd "$PROJECT_DIR"

if [[ ! -x "$PYTHON_BIN" ]]; then
  PYTHON_BIN="python3"
fi

"$PYTHON_BIN" -m pip install --upgrade pip
"$PYTHON_BIN" -m pip install pyinstaller

"$PYTHON_BIN" -m PyInstaller \
  --name northtone \
  --clean \
  --onefile \
  --add-data "northtone/styles.tcss:." \
  --add-data "northtone/styles.tcss:northtone" \
  northtone/app.py

echo
echo "Standalone executable created:"
echo "  $PROJECT_DIR/dist/northtone"
