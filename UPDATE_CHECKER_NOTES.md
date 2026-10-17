# Update Checker (v0.3.0-alpha.1)

Adds `glassbalance/update_check.py` with strict version and release metadata validation. The Qt UI performs a nonblocking HTTPS request to the official GitHub Releases API, shows a discreet update indicator for newer stable releases, and has an About > Check for updates button with installed/latest values and a manual link to GitHub. Startup checks can be disabled in About; all ledger features remain offline-capable. This iteration deliberately contains **no download, replacement or installer logic**.

Base source: the supplied **v0.2.0-beta.1 source package**, the latest locally available complete source archive, not a live checkout of the user's `main` branch. If `main` contains changes made after beta.1, compare the files before uploading instead of overwriting them blindly.
