# Changelog

## v0.3.0-beta.1 (unreleased)

- **In-app updates**: checks the latest *stable* release; shows release notes with Download and install / Later / Skip this version.
  Downloads with a progress bar and Cancel, verifies size and SHA-256 against the release's `SHA256SUMS.txt`, backs up the ledger, then installs and restarts:
  Windows installer runs silently (no admin prompt, per-user install); Ubuntu `.deb` asks for your password via the system dialog; macOS opens the disk image for drag-and-drop.
  Portable and source copies are pointed to the release page instead.
- Clear messages for offline, timeout, HTTPS/proxy failures, GitHub rate limits and server errors, with Try again. Startup checks stay silent when offline.
- Fixed: the update check always reported "unavailable" with current PySide6 (`NoError` is truthy), so updates were never detected.
- Release automation: draft GitHub releases with checksums from tags (pre-releases) and from `main` (stable); version defined once in `glassbalance/__init__.py`.
- Testers can opt into pre-release updates with the environment variable `GLASSBALANCE_UPDATE_CHANNEL=prerelease`.

## v0.3.0-alpha.2

- Native Windows installer (Inno Setup) and Ubuntu/Debian `.deb`, alongside portable ZIPs.
- **Transaction categories**: set from the bottom bar or right-click; stored in SQLite; never change balances. Searchable from the Transactions filter. Included in CSV/XLSX export and re-import.
- **Categories & charts** tab: native Qt expense bar chart plus income/expense/net per category. Totals always reconcile with the ledger (Uncategorized included).
- **Undo deletion**: restores the most recent deleted transaction in the current session with its original ID, comment, category and recurring-post record. Loan-linked transactions can no longer be deleted (previously deletion silently cascaded away loan history).
- **Recurring templates**: manual, confirmed posting for the current month only; one post per template per month (guard survives restart); day-of-month clamps to short months; removing a template keeps posted transactions; deleting a posted transaction makes that month postable again.
- Restoring an older backup now recreates missing feature tables (comments, loans, categories, recurring).
- **Experimental macOS `.dmg`** (Apple Silicon, ad-hoc signed, not notarized) built by GitHub Actions.
- Removed committed `__pycache__` files. 37 automated tests (was 17).

## v0.2.0-alpha.2

- Dedicated Balance Search tab with in/out/net totals.
- Opt-in Unbalanced loan tracker; user confirmation required for every repayment match.
- Partial repayments and unlinking; no effect on ledger balance.
- About dialog image support and build-time low-resolution GitHub avatar fetch.
- Regression tests for loan accounting and settlement safeguards.

## v0.2.0-alpha

- Native Qt glass-inspired interface redesign, balance trend chart and creator credit.

### UI fixes for alpha.2 (test build)
- Sidebar navigation scrolls on shorter windows and with larger text scaling, preventing footer controls from being clipped.
- About window allows the maintainer to select an avatar locally; it is resized to 128 pixels and saved in the app's local data directory for offline use.
- The packaged GitHub avatar is still used as the default when available.

## v0.2.0-alpha.3
- G + Wallet branding and official executable/window icon assets.
- Explicit Windows-safe dark sidebar viewport, scrolling area, and content backgrounds.
- Portable GitHub packaging script chooses Linux PNG or Windows ICO.
- Preserve data format and all prior alpha.2 behavior.
