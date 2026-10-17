# GlassBalance v0.3.0-alpha.1 — update-checker testing

This package implements update checking only; it does **not** download or install updates.

## Setup

- [ ] Back up the GlassBalance ledger before using an alpha build.
- [ ] Create `develop/v0.3.0` from your current `main` branch.
- [ ] Upload the package contents and let GitHub Actions build Linux and Windows packages.
- [ ] Confirm the About dialog identifies this build as **v0.3.0-alpha.1**.

## Windows and Linux

- [ ] **Manual online check:** About > Check for updates displays installed and latest stable versions.
- [ ] **No false alert:** when the latest stable release is older than v0.3.0-alpha.1, it displays "You're up to date" and no dot appears.
- [ ] **Update found:** on a future newer stable release, a dot appears on the main sidebar; About shows both versions and a working GitHub release link. (May need a test with mocked metadata.)
- [ ] **Startup check ON:** after starting the application while online, it checks in the background without freezing the main window.
- [ ] **Startup check OFF:** in About, set Startup checks: Off; restart and confirm no automatic lookup; manual check still works.
- [ ] **Setting persistence:** change startup-check preference, restart, reopen About; choice persists.
- [ ] **Offline case:** disable network temporarily; manual check reports unavailable; no crash or blocking popup; ledger remains usable.
- [ ] **Financial safety:** add/edit a test transaction and confirm balance stays correct after checking; no transaction data is transmitted by the updater.
- [ ] **Release link:** when offered, it opens the official `Onimee58/GlassBalance` GitHub release.
- [ ] **No automatic download/installation:** confirming checks never downloads application binaries or changes app files.
- [ ] **UI:** About text and buttons fit without clipping on Windows and Ubuntu.

## Technical notes

- The updater deliberately targets the GitHub `releases/latest` endpoint (stable releases only; no draft or pre-release alerts).
- Since the test build is **v0.3.0-alpha.1**, the currently released **v0.2.0** is correctly considered older. Therefore, without publishing a newer stable release or mocking a newer one, the dot cannot be tested end-to-end yet.
- A small HTTPS request to GitHub reveals your public IP to GitHub but never uploads ledger records.
- Current GUI testing must be done on your machines; unit tests cover version parsing and release metadata validation.
