<div align="center">

 <img src="glassbalance/assets/glassbalance_icon.png" alt="GlassBalance logo" width="96">

# GlassBalance

### Your money, your records, your computer.

**A free, open-source, offline-first personal finance app for Windows and Linux, with an experimental macOS build.**

Track your transactions, understand your balance, and manage money lent or borrowed—without creating an account or sending your ledger to a cloud service.

[![GitHub Releases](https://img.shields.io/github/v/release/Onimee58/GlassBalance?include_prereleases&label=available%20release)](https://github.com/Onimee58/GlassBalance/releases)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Platforms](https://img.shields.io/badge/platforms-Windows%20%7C%20Linux%20%7C%20macOS%20(experimental)-informational)](https://github.com/Onimee58/GlassBalance/releases)

### [⬇ Download GlassBalance](https://github.com/Onimee58/GlassBalance/releases) · [📋 Browse All Releases](https://github.com/Onimee58/GlassBalance/releases) · [🏷 Latest Stable Release](https://github.com/Onimee58/GlassBalance/releases/latest)

*The **Download** link opens the newest available releases, including Alpha and Beta versions. The **Latest Stable Release** link excludes prereleases and may point to an older version.*

</div>

---

## Why GlassBalance?

GlassBalance gives you a straightforward, private place to keep your personal financial history. It is designed around a **continuous running balance**, rather than requiring bank connections or an online account.

- **Offline-first:** use the ledger without an internet connection.
- **Private by default:** transactions live in a local SQLite database.
- **Cross-platform desktop app:** built with Python, PySide6, and Qt 6.
- **Transparent:** open-source under the MIT License.
- **In control:** review your history, export your data, and create backups.

## Features

| | Capability | What it does |
|---|---|---|
| 💰 | **Running balance** | Record income and expenses and see the balance after each transaction. |
| 🔍 | **Balance Search** | Find matching transactions and calculate money in, money out, and net change. |
| ✍️ | **Easy transaction editing** | Add, edit, delete, filter, and annotate ledger entries. |
| ✨ | **Autocomplete** | Reuse descriptions from your existing transaction history. |
| 🤝 | **Unbalanced tracker** | Track money lent or borrowed and link repayments with confirmation. |
| 📅 | **Monthly history** | Review monthly income, expenses, and balance changes. |
| 🗂️ | **Categories & charts** | Categorize transactions and see spending per category; double-click a category to list its transactions. |
| 📊 | **Money in · out · net** | Totals for this month, last month, this year, all time or any custom date range. |
| 🔁 | **Recurring transactions** | Templates for rent, salary and subscriptions, posted only after you confirm. |
| ↶ | **Undo deletion** | Restore the most recently deleted transaction during the same session. |
| 🎨 | **Personalization** | Choose dark, light, or system appearance and a custom accent color. |
| 📁 | **Import and export** | Work with supported CSV and Excel ledger files. |
| 🔐 | **Backups** | Create and restore local backups; optionally send encrypted email snapshots. |
| 🔔 | **In-app updates** | Get notified of new stable releases; download, verify and install them from inside the app. |

> **Financial integrity matters.** Unbalanced loan tracking references existing ledger transactions; it does not add the same amount to your balance twice. Linking or removing repayment relationships does not itself change the ledger balance.

## Download and install

**[Go to the Downloads / Releases page →](https://github.com/Onimee58/GlassBalance/releases)**

Choose the package for your operating system from the release assets. The available formats depend on the version.

| Operating system | Download option | Notes |
|---|---|---|
| **Windows** | `GlassBalance-Setup-…-Windows-x64.exe` | **Recommended.** Installs for your user account only; no administrator rights needed. Updates install from inside the app. |
| **Windows** | Portable ZIP | Extract the whole folder and launch `GlassBalance.exe`. Portable copies don't update themselves. |
| **Ubuntu / Debian** | `glassbalance_…_amd64.deb` | **Recommended.** Install with `sudo apt install ./glassbalance_*_amd64.deb`. Updates install from inside the app (you'll be asked for your password). |
| **Linux** | Portable ZIP | Extract and run `bash install-linux.sh` for a menu entry, or launch `GlassBalance/GlassBalance` directly. |
| **macOS** *(experimental)* | `GlassBalance-…-macOS-arm64.dmg` | Apple Silicon only. Open the disk image and drag GlassBalance to Applications. |

Every release includes `SHA256SUMS.txt` so you can verify downloads, for example `sha256sum -c SHA256SUMS.txt --ignore-missing`.

**First launch of unsigned builds:**
- **Windows:** if SmartScreen appears, choose **More info → Run anyway**.
- **macOS:** the app isn't notarized yet. If macOS blocks it, open **System Settings → Privacy & Security** and choose **Open Anyway**.

**Useful links:** [All releases, including previews](https://github.com/Onimee58/GlassBalance/releases) · [Latest non-prerelease](https://github.com/Onimee58/GlassBalance/releases/latest) · [Release notes and older versions](https://github.com/Onimee58/GlassBalance/releases)

**Before upgrading:** create a backup from within GlassBalance (**Save backup**). Installers and in-app updates replace program files only; your ledger and backups stay where they are. Alpha and Beta builds are intended for testing and may contain bugs.

**Upgrading from v0.2.x or a v0.3.0 preview?** Earlier builds can't detect updates, so download v0.3.0 once from the Releases page. From v0.3.0 on, updates install from inside the app.

### Run from source

Requires **Python 3.11+**. Download the repository or clone it:

```bash
git clone https://github.com/Onimee58/GlassBalance.git
cd GlassBalance
```

**Windows:** Double-click `run-windows.bat`, or run:

```powershell
py -3 -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements.txt
.venv\Scripts\python.exe app.py
```

**Linux:** Run `./run-linux.sh`, or use:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python app.py
```

On Ubuntu, you may need `python3-venv` and distribution-specific Qt runtime libraries. Installing Python dependencies initially requires internet access; normal ledger use does not.

## How it works

**Income is positive; expenses are negative.** For example, a deposit of `2500` increases your balance, while a purchase of `-45.90` decreases it. GlassBalance maintains the running total using your opening balance and transaction history.

Use **Transactions** for the full ledger, **Balance Search** to see totals for a keyword (such as `walmart`), **Monthly History** for monthly summaries, **Categories & charts** for spending by category, **Recurring** for regular bills and income, and **Unbalanced** to manage outstanding lending and borrowing. The **Money in · out · net** card on the Overview sets the date range for the totals and the category view.

Categories are set in the New and Edit transaction dialogs and never change balances. You can also categorize many transactions at once: export to Excel, fill in the **Category** column, and import the file again.

When tracking loans, GlassBalance asks you to confirm repayment links. Removing an Unbalanced tracking record does **not** remove the corresponding financial transaction. Deleting the transaction itself **does** affect your balance.

## Your data and privacy

GlassBalance stores transaction data locally in SQLite. It does **not** require an account, connect to a bank, or automatically upload your ledger.

- **Local backups:** save a copy of your database before imports, upgrades, or major changes.
- **Encrypted email snapshots:** an optional, manually initiated feature that uses mail servers you configure; this is **not** automatic cross-device synchronization.
- **Updates:** GlassBalance asks GitHub for public release information at startup (you can turn this off in **About**). It downloads an installer only when you choose **Download and install**, verifies its checksum, and backs up your ledger before installing. No ledger data is ever sent.
- **Local database encryption:** the SQLite database is **not encrypted at rest by default**. Consider operating-system full-disk encryption for additional protection.

**Never upload your personal database, backup files, or email credentials to a public repository.**

## Roadmap

| Milestone | Main goals |
|---|---|
| **v0.3.0** ✅ | Stable desktop release: native installers, in-app updates, categories and charts, date-range totals, recurring transactions, undo deletion, experimental macOS build. |
| **v0.4.0** | PDF bank-statement import and receipt processing. |
| **v0.5.0** | Data portability and secure cross-device synchronization research/development. |
| **v0.6.0** | Begin Android/mobile development. |

*Roadmap items are plans, not promises; feature availability depends on the release.*

## Contributing and feedback

GlassBalance is an independent open-source project. Bug reports, ideas, and contributions are welcome.

- [Report a bug or request a feature](https://github.com/Onimee58/GlassBalance/issues)
- [View the source code](https://github.com/Onimee58/GlassBalance)
- [Browse release history](https://github.com/Onimee58/GlassBalance/releases)

Developers can run the core tests with:

```bash
python -m unittest discover -s tests -v
```

## License and credits

GlassBalance is licensed under the [MIT License](LICENSE). Third-party dependencies are subject to their respective licenses.

Created and maintained by **[@Onimee58](https://github.com/Onimee58)**.

<div align="center">

**Keep track. Stay balanced. Keep your data yours.**

[⬇ Download](https://github.com/Onimee58/GlassBalance/releases) · [GitHub](https://github.com/Onimee58/GlassBalance) · [Issues](https://github.com/Onimee58/GlassBalance/issues)

</div>
