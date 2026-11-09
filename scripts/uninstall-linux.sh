#!/usr/bin/env bash
# Remove only application files and desktop registration, never the ledger.
set -euo pipefail
DATA_HOME="${XDG_DATA_HOME:-$HOME/.local/share}"
rm -f -- "$DATA_HOME/applications/io.github.Onimee58.GlassBalance.desktop"
rm -f -- "$DATA_HOME/icons/hicolor/256x256/apps/io.github.Onimee58.GlassBalance.png"
rm -rf -- "$HOME/.local/opt/glassbalance"
command -v update-desktop-database >/dev/null 2>&1 && update-desktop-database "$DATA_HOME/applications" >/dev/null 2>&1 || true
echo 'GlassBalance launcher and application removed. Your ledger and backups were not deleted.'
