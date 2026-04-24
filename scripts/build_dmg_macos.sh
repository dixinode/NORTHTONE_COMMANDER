#!/usr/bin/env bash
set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PYTHON_BIN="${PYTHON_BIN:-$PROJECT_DIR/.venv/bin/python}"
APP_NAME="NorthTone Commander"
BINARY_NAME="northtone"
VERSION="$("$PYTHON_BIN" -c 'from northtone import __version__; print(__version__)')"

APP_BUNDLE="$PROJECT_DIR/dist/$APP_NAME.app"
STAGING_DIR="$PROJECT_DIR/build/dmg-staging"
RELEASE_DIR="$PROJECT_DIR/release"
DMG_PATH="$RELEASE_DIR/northtone-commander-$VERSION-macos-arm64.dmg"

if [[ ! -x "$PROJECT_DIR/dist/$BINARY_NAME" ]]; then
  "$PROJECT_DIR/scripts/build_standalone_macos.sh"
fi

rm -rf "$APP_BUNDLE" "$STAGING_DIR" "$DMG_PATH"
mkdir -p \
  "$APP_BUNDLE/Contents/MacOS" \
  "$APP_BUNDLE/Contents/Resources" \
  "$STAGING_DIR" \
  "$RELEASE_DIR"

cp "$PROJECT_DIR/dist/$BINARY_NAME" "$APP_BUNDLE/Contents/Resources/$BINARY_NAME"
chmod +x "$APP_BUNDLE/Contents/Resources/$BINARY_NAME"

cat > "$APP_BUNDLE/Contents/Info.plist" <<PLIST
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN"
  "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>CFBundleDevelopmentRegion</key>
  <string>en</string>
  <key>CFBundleDisplayName</key>
  <string>$APP_NAME</string>
  <key>CFBundleExecutable</key>
  <string>northtone-launcher</string>
  <key>CFBundleIdentifier</key>
  <string>com.dixinode.northtonecommander</string>
  <key>CFBundleInfoDictionaryVersion</key>
  <string>6.0</string>
  <key>CFBundleName</key>
  <string>$APP_NAME</string>
  <key>CFBundlePackageType</key>
  <string>APPL</string>
  <key>CFBundleShortVersionString</key>
  <string>$VERSION</string>
  <key>CFBundleVersion</key>
  <string>$VERSION</string>
  <key>LSMinimumSystemVersion</key>
  <string>10.13</string>
</dict>
</plist>
PLIST

cat > "$APP_BUNDLE/Contents/MacOS/northtone-launcher" <<'LAUNCHER'
#!/usr/bin/env bash
set -euo pipefail

APP_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
NORTHTONE_BIN="$APP_DIR/Resources/northtone"

osascript <<APPLESCRIPT
tell application "Terminal"
  activate
  do script quoted form of "$NORTHTONE_BIN"
end tell
APPLESCRIPT
LAUNCHER

chmod +x "$APP_BUNDLE/Contents/MacOS/northtone-launcher"

codesign --force --deep --sign - "$APP_BUNDLE" >/dev/null 2>&1 || true

cp -R "$APP_BUNDLE" "$STAGING_DIR/"
ln -s /Applications "$STAGING_DIR/Applications"

hdiutil create \
  -volname "$APP_NAME" \
  -srcfolder "$STAGING_DIR" \
  -ov \
  -format UDZO \
  "$DMG_PATH"

echo
echo "macOS app created:"
echo "  $APP_BUNDLE"
echo
echo "DMG created:"
echo "  $DMG_PATH"
