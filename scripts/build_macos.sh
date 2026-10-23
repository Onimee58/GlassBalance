#!/usr/bin/env bash
# EXPERIMENTAL macOS build: .app bundle wrapped in a .dmg. Run on a macOS runner.
# The app is ad-hoc signed only (not notarized): Gatekeeper will block first launch
# until the user allows it in System Settings > Privacy & Security.
set -euo pipefail
cd "$(dirname "$0")/.."
VERSION="$(python -c 'import glassbalance; print(glassbalance.__version__)')"
ARCH="$(uname -m)"
mkdir -p build
ICONSET=build/glassbalance.iconset
rm -rf "$ICONSET" && mkdir -p "$ICONSET"
SRC=glassbalance/assets/glassbalance_icon.png
for size in 16 32 64 128 256 512; do
  sips -z $size $size "$SRC" --out "$ICONSET/icon_${size}x${size}.png" >/dev/null
  half=$((size/2))
  if [[ $half -ge 16 ]]; then cp "$ICONSET/icon_${size}x${size}.png" "$ICONSET/icon_${half}x${half}@2x.png"; fi
done
iconutil -c icns "$ICONSET" -o build/glassbalance_icon.icns
python scripts/build_bundle.py
APP=dist/GlassBalance.app
[[ -d "$APP" ]] || { echo "PyInstaller did not produce $APP" >&2; exit 1; }
PLIST="$APP/Contents/Info.plist"
plutil -replace CFBundleShortVersionString -string "$VERSION" "$PLIST"
plutil -replace CFBundleVersion -string "$VERSION" "$PLIST"
plutil -replace NSHighResolutionCapable -bool true "$PLIST"
plutil -replace LSMinimumSystemVersion -string "12.0" "$PLIST"
# Editing Info.plist invalidates PyInstaller's signature; Apple Silicon requires a valid
# (ad-hoc is enough) signature to run at all.
codesign --force --deep --sign - "$APP"
codesign --verify --deep --strict "$APP"
STAGE=build/dmg
rm -rf "$STAGE" && mkdir -p "$STAGE"
cp -R "$APP" "$STAGE/"
ln -s /Applications "$STAGE/Applications"
DMG="GlassBalance-v${VERSION}-macOS-${ARCH}.dmg"
rm -f "$DMG"
hdiutil create -volname "GlassBalance" -srcfolder "$STAGE" -ov -format UDZO "$DMG"
echo "Built $DMG"
