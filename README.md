# GlassBalance

Created and maintained by **[@Onimee58](https://github.com/Onimee58)** · started October 2026.

**A private, open-source balance tracker for Windows and Linux.**

GlassBalance is a **native Qt desktop app**, not a website or Electron/browser wrapper. It reproduces the key behavior of a continuous spreadsheet ledger: each signed transaction increases or decreases a single running balance. It works offline and uses a local SQLite database.

## New in v0.2.0-alpha.2

- **Balance Search** is a dedicated tab: enter a phrase to see all matching ledger descriptions, money in, money out, and net total.
- **Unbalanced** is an opt-in loan tracker. Click **Track selected transaction as loan**, select an original loan transaction, and name the person. Money lent is a negative transaction; money borrowed is positive.
- Select a loan and choose **Review possible refunds** to review matching transactions. Every individual repayment needs explicit confirmation; declining a suggestion keeps it from repeating for the same loan.
- Loan settlement links do **not** alter ledger transactions or your overall balance. You can unlink repayments. Existing histories continue unchanged.
- **About** has maintainer credit and an offline-bundled profile image if GitHub Actions can fetch one at package build time; otherwise there is a fallback mark.

**Current alpha.2 limitations:** Initial registration uses an existing transaction selection list. Refund suggestions look for a person name and the keywords `refund`, `repay`, or `return`. Manual selection of other repayments and deleting loan classifications will follow. Editing an amount linked to a loan is blocked until you unlink it. As always, keep a local backup before upgrading.

## Previously in v0.2.0-alpha

- Rebuilt the Qt desktop interface with a more deliberate glass-inspired visual hierarchy.
- Brand-new navigation sidebar and balance hero.
- Native, dependency-free mini chart of the last 90 running balances.
- Reorganized income and expenses overview and streamlined transaction workspace.
- **About GlassBalance** screen credits [@Onimee58](https://github.com/Onimee58), the founding maintainer.
- Fully reuses the v0.1 SQLite ledger; no migration or reimport is necessary.

This is a **visual redesign alpha**. Automatic sync, new categorization and standalone installers are not included in this milestone. Existing Excel import/export, manual encrypted email backups and transaction editing are preserved.

## Features in 0.2.0-alpha

- **Continuous ledger:** opening balance + signed transactions. The opening balance is not income.
- **Transaction editor:** description, signed amount, calendar date, estimated/confirmed date.
- **Search and date filters:** all dates, current/previous month, custom date range.
- **Monthly history:** money in, money out, net change, closing balance.
- **Original spreadsheet import:** recognizes the old horizontally arranged `Name | Bill or Income | Amount` sections in one `.xlsx` worksheet.
- **Curated data import:** recognizes the normalized historical `.xlsx` and `.csv` format.
- **Safe repeat imports:** stable source IDs prevent the same historical transactions from being inserted twice.
- **Exact amounts:** stores thousandths of a dollar internally to preserve two historical three-decimal-place entries. Most amounts display to two decimals.
- **Backups:** export CSV/XLSX, or back up/restore the complete SQLite ledger.
- **Optional encrypted email snapshots:** AES-256-GCM encrypted backup sent to yourself over SMTP and retrieved over IMAP. Decryption requires a separate passphrase that is not stored.

### Current limitations

This is an **alpha desktop release/source project**. It has not yet undergone full native UI testing or installer signing on Windows/Linux. **Email backups are manual snapshot transfer, not automatic two-way sync.** If you restore an old email snapshot, it replaces current local data; GlassBalance first creates a local safety backup and asks for confirmation. Local SQLite data is **not encrypted at rest** by default; use your operating system's full-disk encryption.

There is no live bank connection, budget-limit forecasting, or cloud service. The source distribution includes **no private financial records**.

## Get started on Windows

1. Install [Python 3.11 or newer](https://www.python.org/downloads/), and check **Add Python to PATH** during setup.
2. Extract the source ZIP to a folder.
3. Double-click **`run-windows.bat`**. It creates a virtual environment and installs dependencies on the first run, then launches the app. An internet connection is needed to download packages the first time.
4. Select **Import Excel / CSV** and choose your curated ledger or your original Excel workbook.

Alternatively, open PowerShell in this directory and run:

```powershell
py -3 -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements.txt
.venv\Scripts\python.exe app.py
```

## Get started on Linux

Install Python 3.11+, `python3-venv`, and desktop libraries required by Qt. Most modern desktop distributions have Qt's prerequisites; on some Ubuntu/Debian systems you may need `libxcb-cursor0` and `libegl1`.

```bash
cd glass_balance
chmod +x run-linux.sh
./run-linux.sh
```

Or run directly:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python app.py
```

No internet connection is required to use the app after installing dependencies, unless you choose to use the optional email backup feature.

## Generate standalone Windows / Linux builds

This repository contains a GitHub Actions workflow at `.github/workflows/build.yml`.

1. Create a GitHub repository from this source (do **not** upload your private balance sheets).
2. On GitHub, open **Actions → Build desktop packages → Run workflow**.
3. Download the Windows or Linux artifact. These are PyInstaller **one-directory** builds; keep all files together. On Windows run `GlassBalance.exe`; on Linux run `GlassBalance`.

Standalone build artifacts are platform-specific and are not included in the source ZIP.

## Importing your old spreadsheet

Use **Import Excel / CSV** and select either:

- Your **original** workbook with many horizontal transaction sections, or
- The companion **curated** `.xlsx`/`.csv` containing dated transactions.

For historical rows without original dates, the direct importer estimates:

1. A salary labeled `August Salary` → **August 31** (last calendar day of the month worked).
2. The following month's housing rent → **September 2**.
3. Other transactions → spaced through September, with original ordering preserved in a separate source-order field.

Every inferred date is labeled **Estimated**. Selecting a different date in the editor automatically marks it **Confirmed**. **No historical dates are represented as verified facts.** For repeat imports, the same source cell has a stable ID and is skipped rather than duplicated.

The imported opening balance is stored separately and never counted as earnings. Running balances are recalculated from every underlying transaction. The app **does not import potentially inaccurate Excel running-balance formulas**.

**Note:** If your historical workbook is corrected after an import, importing it again will *skip* existing source IDs rather than change records you've already reviewed or edited. Export/backup first before rebuilding an imported ledger from scratch.

## How to enter transactions

- A salary of 2,000 → enter `2000`.
- A grocery expense of 35.50 → enter `-35.50`.
- Money lent to someone → enter a negative amount; repayment → enter a positive amount.
- Set the **Date** with the calendar and choose whether that date is confirmed or estimated.

Double-click a row to edit. Deleting a row immediately recalculates subsequent balances.

## Email backup / restore (optional)

Select **Email backups**. Supply your email address, SMTP/IMAP host and port, an email **app password** if your provider supports that authentication method, and a different encryption passphrase (12+ characters).

- **Send encrypted backup** securely mails an AES-256-GCM encrypted SQLite snapshot to your own inbox.
- **Restore newest email backup** downloads the latest matching attachment, decrypts it, creates a local safety backup, and replaces the local ledger **only after warning you**.

Passwords/passphrases are held only during this dialog, not written to disk. Email address and host/port settings may be remembered. Some email providers require OAuth instead of app passwords; OAuth is **not implemented yet**, so this feature won't work with every provider. Do **not** reuse your email password as your encryption passphrase.

Do not use the manual email feature as simultaneous two-device sync: an old restore may overwrite newer changes from another device. Conflict-aware synchronization is a planned separate feature.

## Where your records live

- **Windows:** the platform's Qt application data directory for `GlassBalance`, normally under `%LOCALAPPDATA%` or `%APPDATA%`.
- **Linux:** the user's application-data directory, normally `~/.local/share/GlassBalance/` (may vary with system environment variables).

The filename is `balance.sqlite`. Local safety backups are placed in a `backups/` subdirectory.

## Tests

These cover workbook imports, salary/rent dating, fractional-cent preservation, deduplication, running balances, CSV/XLSX round-trips, database backups/restores, and encryption. No PySide6 installation is required for these core tests:

```bash
python -m unittest discover -s tests -v
```

## Technology and license

- Python 3.11+
- PySide6 / Qt 6 (`QWidget`, no web views)
- SQLite (Python standard library)
- `openpyxl` for Excel import/export
- `cryptography` for authenticated AES encryption

Application source code is **MIT licensed** (see `LICENSE`). Third-party dependencies have their **own licenses**. PySide6/Qt is made available under LGPL/GPL/commercial options, and redistribution must respect the applicable Qt licensing and other dependency requirements. The source ZIP deliberately contains no original or curated private ledger records.

## Suggested next milestones

1. Review screen for bulk correcting historical *estimated* dates.
2. Optional categories, tags, recurring entries, and budgets without disrupting the running-balance ledger.
3. Conflict-aware encrypted sync across devices with transaction IDs/revisions and recovery snapshots.
4. Signed installers and Linux AppImage/Flatpak builds.

Contributions and bug reports are welcome once you publish the repository.
