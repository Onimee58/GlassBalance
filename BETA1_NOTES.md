# GlassBalance v0.2.0-beta.1 (candidate)

This is a stabilization release, not a feature release.

## Changes
- Added native Linux desktop integration to the packaged Linux ZIP: `install-linux.sh`, `uninstall-linux.sh`, and the bundled G + Wallet PNG.
- Registered the Linux Qt desktop file name `io.github.Onimee58.GlassBalance` to help GNOME match running windows to the launcher.
- Changed Balance Search placeholder text from `Try: ammu` to `Try: walmart`; search logic is unchanged.
- Enabled GitHub Actions for the `release/v0.2.0-beta` branch.
- Preserved the SQLite ledger schema and all financial features.

## Installation on Ubuntu from the Linux build artifact
1. Extract the **inner** `GlassBalance-Linux.zip` from GitHub Actions.
2. In a terminal inside the extracted directory, run `bash install-linux.sh` (no sudo).
3. Open Ubuntu's application menu, search for **GlassBalance**, and launch it using the new application entry.
4. Pin its running icon to your dock if desired. Do not launch the old unpacked executable if you want the dock to associate the installed app.
5. To remove only the installed application and launcher, run `bash uninstall-linux.sh` from the extracted directory. Your database is not removed.

The installation copies the build to `~/.local/opt/glassbalance`, registers a `.desktop` entry under `~/.local/share/applications`, and installs the icon under `~/.local/share/icons/hicolor/256x256/apps`. XDG_DATA_HOME is supported for desktop entries/icons.

## Beta testing
Back up your ledger before testing. Verify balance values, search, repayment confirmations, backup/restore, import/export, and restart persistence on both Windows and Linux. Windows packages remain unsigned and may show SmartScreen prompts.

GitHub Actions builds must still be tested on actual Ubuntu 26.04 and Windows machines. The executable and Ubuntu dock icon have not been visually tested in this environment.
