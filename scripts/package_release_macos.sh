#!/usr/bin/env bash
set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VERSION="$("$PROJECT_DIR/.venv/bin/python" -c 'from northtone import __version__; print(__version__)')"
RELEASE_DIR="$PROJECT_DIR/release"
EXECUTABLE="$PROJECT_DIR/dist/northtone"
ARCHIVE="$RELEASE_DIR/northtone-commander-$VERSION-macos-arm64.zip"

if [[ ! -x "$EXECUTABLE" ]]; then
  echo "Missing standalone executable: $EXECUTABLE"
  echo "Run scripts/build_standalone_macos.sh first."
  exit 1
fi

mkdir -p "$RELEASE_DIR"
ditto -c -k --keepParent "$EXECUTABLE" "$ARCHIVE"

echo "Release archive created:"
echo "  $ARCHIVE"
