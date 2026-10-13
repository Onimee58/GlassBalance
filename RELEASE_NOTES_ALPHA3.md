# GlassBalance v0.2.0-alpha.3 — Identity & Windows Theme Fix

## Changes
- Official **G + Wallet** icon in bundled SVG, PNG, and Windows ICO formats.
- Application/window/About icon now uses the new symbol.
- Windows PyInstaller build embeds the ICO; Linux uses PNG.
- Sidebar scroll area, viewport, and content have explicit dark backgrounds to avoid a white Windows system-palette viewport.
- Keeps local ledger, Balance Search, Unbalanced, Excel/CSV import/export, and backup behavior unchanged.
- Keeps the avatar and local replacement feature from alpha.2.
- GitHub Actions builds both platforms from `v0.2.0-*` development branches.

## Testing
- Automated: 11 core tests passed.
- GUI appearance: needs testing on Windows and Linux with GitHub-built artifacts.
- **Back up your ledger before testing any alpha update.**

## Not included yet
- Transaction categories, autocomplete, light theme, and installer packaging remain planned; they have not been implemented in this build.

## Release setup
Tag `v0.2.0-alpha.3` on the commit in the `v0.2.0-alpha.3` branch, after both platform builds and UI tests succeed.
