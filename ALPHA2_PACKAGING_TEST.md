# GlassBalance v0.3.0-alpha.2 - installer test build

This is the **first Alpha 2 development increment**, focused on Windows and Ubuntu installation. It is **not** a published alpha release. Transaction categories, undo-delete, and expanded charts are still pending.

## GitHub Actions

Upload the source files to `develop/v0.3.0`, then run **Build desktop packages** from that branch. The workflow should create four artifacts: Windows portable ZIP, Windows Setup EXE, Linux portable ZIP, and Ubuntu amd64 DEB.

## Windows testing

1. Back up your data from your existing installation.
2. Run `GlassBalance-Setup-v0.3.0-alpha.2-Windows-x64.exe`.
3. Verify Start menu search, Installed Apps listing, app icon, optional desktop shortcut, and launch.
4. Edit a disposable transaction; close and relaunch to confirm it persists.
5. Install a second build over the first; confirm the data and settings survive.
6. Uninstall through Installed Apps; confirm the financial database and backups are **not removed**.

## Ubuntu testing

1. Back up your data before installation.
2. Install `sudo apt install ./glassbalance_0.3.0~alpha2_amd64.deb`.
3. Launch with `glassbalance` or from the application menu; verify the dock icon.
4. Check `dpkg -s glassbalance`, and then reinstall the same package.
5. Verify the ledger survives upgrade and removal (`sudo apt remove glassbalance`).
6. If you previously used `scripts/install-linux.sh`, uninstall the old user-local copy with that version's `uninstall-linux.sh` to avoid duplicate launchers, **only after confirming the new package works**. Never delete application data.

## Known limitations

- Builds need real Windows and Ubuntu GUI testing. This environment only verifies source and packaging configuration.
- Windows installation is per-user, without administrator privileges. Windows SmartScreen may warn because binaries are unsigned.
- `.deb` is currently **amd64 Ubuntu/Debian** only, not all Linux distributions.
- Package replacement does not automatically migrate a database stored in an unexpected location. Confirm the database path before deleting old program files.
- No user-data deletion commands appear in either installer definition.
