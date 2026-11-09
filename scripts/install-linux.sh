#!/usr/bin/env bash
# User-level GlassBalance desktop integration. No sudo required.
set -euo pipefail
SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
SOURCE="$SCRIPT_DIR/GlassBalance"
if [[ ! -f "$SOURCE/GlassBalance" ]]; then
  echo "Could not find GlassBalance executable next to this script." >&2
  exit 1
fi
ICON="$SCRIPT_DIR/glassbalance-icon.png"
if [[ ! -f "$ICON" ]]; then
  echo "Could not find glassbalance-icon.png next to this script." >&2
  exit 1
fi
DATA_HOME="${XDG_DATA_HOME:-$HOME/.local/share}"
APP_DIR="$HOME/.local/opt/glassbalance"
DESKTOP_DIR="$DATA_HOME/applications"
ICON_DIR="$DATA_HOME/icons/hicolor/256x256/apps"
mkdir -p "$(dirname "$APP_DIR")" "$DESKTOP_DIR" "$ICON_DIR"
# Keep financial information untouched: only copy the release bundle.
if [[ -d "$APP_DIR" ]]; then
  echo "Replacing the previous program files in $APP_DIR (your ledger data is not touched)."
  rm -rf -- "$APP_DIR"
fi
cp -a -- "$SOURCE" "$APP_DIR"
chmod u+x "$APP_DIR/GlassBalance"
cp -- "$ICON" "$ICON_DIR/io.github.Onimee58.GlassBalance.png"
DESKTOP_FILE="$DESKTOP_DIR/io.github.Onimee58.GlassBalance.desktop"
# Escaping literal percent and backslashes avoids malformed desktop files.
# Paths with quotes or newlines cannot be represented safely here.
if [[ "$APP_DIR" == *$'\n'* || "$APP_DIR" == *'"'* || "$APP_DIR" == *'\\'* || "$APP_DIR" == *'%'* ]]; then
  echo 'Unsupported special character in home directory path.' >&2
  exit 1
fi
cat > "$DESKTOP_FILE" <<DESKTOP
[Desktop Entry]
Type=Application
Version=1.0
Name=GlassBalance
Comment=Offline-first personal finance tracker
Exec="$APP_DIR/GlassBalance"
Icon=io.github.Onimee58.GlassBalance
Terminal=false
Categories=Office;Finance;
StartupNotify=true
StartupWMClass=GlassBalance
DESKTOP
chmod 644 "$DESKTOP_FILE"
command -v update-desktop-database >/dev/null 2>&1 && update-desktop-database "$DESKTOP_DIR" >/dev/null 2>&1 || true
command -v gtk-update-icon-cache >/dev/null 2>&1 && gtk-update-icon-cache -f -t "$DATA_HOME/icons/hicolor" >/dev/null 2>&1 || true
echo "Installed GlassBalance. Open the application menu, search GlassBalance, and launch it from there."
echo "To pin it to Ubuntu Dock, right-click its running icon and select Add to Favorites."
