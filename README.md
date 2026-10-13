# GlassBalance

**A private, open-source balance tracker for Windows and Linux.**

GlassBalance is a **native Qt desktop app**, not a website or Electron/browser wrapper. It reproduces the key behavior of a continuous spreadsheet ledger: each signed transaction increases or decreases a single running balance. It works offline and uses a local SQLite database.

## Features in 0.1

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

This is a **first desktop release/source project**. It has not yet undergone full native UI testing or installer signing on Windows/Linux. **Email backups are manual snapshot transfer, not automatic two-way sync.** If you restore an old email snapshot, it replaces current local data; GlassBalance first creates a local safety backup and asks for confirmation. Local SQLite data is **not encrypted at rest** by default; use your operating system's full-disk encryption.

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

## Creator & Maintainer

GlassBalance was initiated and is maintained by
[Onimee58](https://github.com/Onimee58).

Project started in October 2026.



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
