# GlassBalance

**Offline-first personal finance for Windows and Linux** · Created and maintained by [@Onimee58](https://github.com/Onimee58) · MIT licensed

GlassBalance is a native Python/PySide6 (Qt 6) desktop application for maintaining a private, continuous balance ledger. Income and expenses are entered as signed transactions, and the running balance is recalculated from the opening balance and recorded entries. Your records are stored in a local SQLite database—no account, browser, or cloud service is required.

> **Current pre-release: v0.3.0-alpha.1 — Personalization & Smart Ledger.** This is testing software. Make a backup of your database before upgrading or importing data. Windows and Linux packages should be tested on their target systems before being treated as production-ready.

## What's new in v0.3.0-alpha.1

### Personalization

- Dark, Light, and System appearance modes.
- Five accent-color presets, plus an expanded custom color dialog with precise color selection.
- Appearance choices saved across restarts.

### Faster transaction workflows

- Description autocomplete based on entries already in your ledger when adding or editing transactions.
- Autocomplete in Transactions search and **Balance Search**; matches are case-insensitive.
- A right-click transaction menu for common actions, including editing, comments, matching transactions, and loan tracking.
- Notes/comments attached to individual transactions.
- **Balance Search** displays matching transactions and separate money-in, money-out, and net totals.
- Search fields better match their tabs: transaction filtering on Transactions, aggregate search on Balance Search, and person/description filtering on Unbalanced.

### Unbalanced: borrowing, lending, and repayments

- Track an existing transaction as money lent or borrowed without recording it twice.
- Review proposed repayments and explicitly confirm each link; unlink incorrect associations.
- Select, search, and **remove an Unbalanced tracking record** with confirmation. Removing tracking does **not** delete the original ledger transaction or change your running balance.
- Loan and repayment relationships remain separate from the financial ledger.

### Updates and reliability

- Optional update checks against official GitHub releases and a manual **Check for updates** control in About.
- A notification indicator when an update is available; updates are **not** automatically installed.
- Improved transaction-table performance for large ledgers, including a fix for an Ubuntu UI freeze after saving edits.
- Improved visibility of accent swatches and Unbalanced selection controls.

**Privacy:** All financial records remain local during normal use. Checking for updates requires an internet connection to GitHub; optional encrypted email backups contact the email servers you configure. There is no automatic transaction upload or cloud sync.

## Existing capabilities

- Continuous ledger with opening balance, signed transactions, running balance, and estimated/confirmed dates.
- Add, edit, delete, search, and filter transactions; monthly income, expenses, net change, and closing balance.
- Balance overview with a recent-balance mini chart.
- Import original historical Excel workbooks and normalized `.xlsx`/`.csv` ledgers; repeat imports use stable source IDs to avoid duplicates.
- CSV/XLSX exports and complete local SQLite backup/restore.
- Optional manually triggered AES-256-GCM encrypted email snapshots (SMTP/IMAP).
- Native Windows and Linux desktop builds via GitHub Actions; Linux user-level launcher installation script.

## Downloads and installation

Visit [GitHub Releases](https://github.com/Onimee58/GlassBalance/releases) for available Windows and Linux packages. **v0.3.0-alpha.1 is a pre-release**; back up your data before testing it.

### Run from source on Windows

1. Install [Python 3.11+](https://www.python.org/downloads/), ensuring Python is on your PATH.
2. Download or clone this repository.
3. Double-click `run-windows.bat`. The first run creates a virtual environment and installs dependencies.

Or use PowerShell in the project directory:

```powershell
py -3 -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements.txt
.venv\Scripts\python.exe app.py
```

### Run from source on Linux

Install Python 3.11+, `python3-venv`, and the Qt runtime libraries required by your distribution. Some Ubuntu/Debian installations also need `libxcb-cursor0` and `libegl1`.

```bash
chmod +x run-linux.sh
./run-linux.sh
```

Or:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python app.py
```

An internet connection may be required once to install Python dependencies. GlassBalance itself works offline afterward, except when using optional update checking or email backup.

### Packaged Linux desktop launcher

When using the Linux application ZIP produced by GitHub Actions, extract the application first and run `bash install-linux.sh` from the extracted package to install the GlassBalance launcher and icon for your user account (without `sudo`). Launch from the application menu to get the correct dock icon. Use `bash uninstall-linux.sh` to remove the installed application; it does not delete your finance records.

### Build packages with GitHub Actions

The `.github/workflows/build.yml` workflow creates platform-specific PyInstaller packages:

1. Open the repository's **Actions** tab.
2. Select **Build desktop packages** and run the workflow on the release branch or tag.
3. Download the build artifacts and verify them on Windows and Linux before publishing.

PyInstaller's one-directory application builds must be kept intact; do not move only the executable out of its package directory. Distributed Windows binaries may show a SmartScreen warning because they are unsigned.

## Using the ledger

Amounts are signed: `2500` is income, `-35.50` is an expense. For lending, the original amount you lend is a negative ledger transaction, and a repayment received is positive; borrowing follows the opposite signs. Unbalanced links are tracking metadata, not additional financial transactions.

Double-click a transaction to edit it, or right-click for additional actions. Previous descriptions appear as suggestions while typing. Search **Transactions** to filter the ledger; use **Balance Search** to calculate totals for a phrase (for example, `walmart`). Choose **Unbalanced** to review outstanding loans and associated repayments. Removing a loan from Unbalanced only removes its tracking classification, after confirmation.

Deleting an actual transaction from the Transactions tab **does** change the running balance. Back up first when performing bulk changes or imports.

## Historical Excel importing

Use **Import Excel / CSV** to load either an original horizontal `Name | Bill or Income | Amount` workbook or a normalized historical `.xlsx`/`.csv` ledger.

When historical dates are absent, the importer estimates dates (for example, the end of a salary month), preserves original ordering, and marks those dates **Estimated** rather than confirmed facts. You can edit and confirm them later. The original opening balance is stored separately, not counted as income; running balances are calculated from imported transactions rather than copied from spreadsheet formulas.

Stable source identifiers prevent repeated imports from adding the exact same historical records. **Re-importing corrected source files does not automatically update previously imported entries**; back up before restructuring an imported ledger.

## Backup, restore, and data privacy

- Use local backup/restore to make a copy of the complete `balance.sqlite` database.
- Optionally send an encrypted snapshot to your own email account using SMTP and retrieve it using IMAP. These are **manual snapshots, not two-way sync**.
- Encrypted email snapshots use AES-256-GCM and a separate passphrase. Avoid reusing your email password for encryption. Some providers require OAuth, which this feature does not currently implement.
- Restoring an older snapshot may overwrite newer local work. GlassBalance requests confirmation and creates a local safety backup before restoring.
- Local SQLite storage is **not encrypted at rest by default**; enable operating-system full-disk encryption if you need that protection.

The application data location is determined by Qt: typically an application-data directory under `%LOCALAPPDATA%`/`%APPDATA%` on Windows and `~/.local/share/GlassBalance/` on Linux. The main file is `balance.sqlite`; local safety copies are stored in `backups/`.

**Never commit personal ledger databases, balance spreadsheets, backup archives, or credentials to a public GitHub repository.** The project source distributions do not contain personal financial records.

## Development and testing

The project uses Python 3.11+, PySide6/Qt 6, SQLite, `openpyxl`, and `cryptography`. Core automated tests can run without installing PySide6:

```bash
python -m unittest discover -s tests -v
```

The v0.3.0-alpha.1 development build passed **17 automated tests** and the newest features were manually checked during Ubuntu development. Test packaged binaries separately on both operating systems.

## Release roadmap

| Milestone | Focus |
| --- | --- |
| **v0.3.0-alpha.1** | Themes, accent colors, autocomplete, transaction comments/context menu, Unbalanced improvements, update checker, performance fixes |
| **v0.3.0-alpha.2** | Categories, undo deletion, financial charts, recurring transactions |
| **v0.3.0-beta.1** | Feature stabilization, defect fixes, performance and Windows/Linux release testing |
| **v0.3.0** | Stable release |
| **v0.4.0** | PDF bank statement import and receipt processing, with review and duplicate detection |

PDF and receipt processing are **not included in v0.3.x**. Cross-device, conflict-aware encrypted synchronization is also a future project, not a feature of the current manual email backup system.

## License and contributions

GlassBalance is released under the [MIT License](LICENSE). Third-party components have separate licenses; PySide6/Qt redistribution must satisfy the applicable LGPL/GPL/commercial terms and other dependencies' requirements.

Bug reports and contributions are welcome at [github.com/Onimee58/GlassBalance](https://github.com/Onimee58/GlassBalance).
