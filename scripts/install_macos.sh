#!/usr/bin/env bash
set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PYTHON_BIN="${PYTHON_BIN:-python3}"

cd "$PROJECT_DIR"

"$PYTHON_BIN" -m pip install --upgrade pip
"$PYTHON_BIN" -m pip install --user .

USER_BIN="$("$PYTHON_BIN" -m site --user-base)/bin"

echo
echo "NorthTone Commander installed."
echo "Run it with:"
echo "  $USER_BIN/northtone"
echo
echo "If your shell cannot find it, add this to ~/.zshrc:"
echo "  export PATH=\"$USER_BIN:\$PATH\""
