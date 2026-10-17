<div align="center">

# GlassBalance

### Your money, your records, your computer.

**A free, open-source, offline-first personal finance app for Windows and Linux.**

Track your transactions, understand your balance, and manage money lent or borrowed—without creating an account or sending your ledger to a cloud service.

[![GitHub Releases](https://img.shields.io/github/v/release/Onimee58/GlassBalance?include_prereleases&label=available%20release)](https://github.com/Onimee58/GlassBalance/releases)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Platforms](https://img.shields.io/badge/platforms-Windows%20%7C%20Linux-informational)](https://github.com/Onimee58/GlassBalance/releases)

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
| 🎨 | **Personalization** | Choose dark, light, or system appearance and a custom accent color. |
| 📁 | **Import and export** | Work with supported CSV and Excel ledger files. |
| 🔐 | **Backups** | Create and restore local backups; optionally send encrypted email snapshots. |
| 🔔 | **Update checks** | Check GitHub for newer versions without automatic installation. |

> **Financial integrity matters.** Unbalanced loan tracking references existing ledger transactions; it does not add the same amount to your balance twice. Linking or removing repayment relationships does not itself change the ledger balance.

## Download and install

**[Go to the Downloads / Releases page →](https://github.com/Onimee58/GlassBalance/releases)**

Choose the package for your operating system from the release assets. The available formats depend on the version.

| Operating system | Download option | Notes |
|---|---|---|
| **Windows** | Portable ZIP | Extract the whole folder and launch GlassBalance. |
| **Windows** | Setup `.exe` | Native installer planned for v0.3.0-alpha.2; download when available. |
| **Ubuntu / Debian** | `.deb` | Native installer planned for v0.3.0-alpha.2; download when available. |
| **Linux** | Portable ZIP / archive | Extract and run the packaged app; some versions include a desktop launcher script. |

**Useful links:** [All releases, including previews](https://github.com/Onimee58/GlassBalance/releases) · [Latest non-prerelease](https://github.com/Onimee58/GlassBalance/releases/latest) · [Release notes and older versions](https://github.com/Onimee58/GlassBalance/releases)

**Before upgrading:** create a backup from within GlassBalance. Alpha and Beta builds are intended for testing and may contain bugs. Windows builds may display an unsigned-app SmartScreen warning.

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

Use **Transactions** for the full ledger, **Balance Search** to see totals for a keyword (such as `walmart`), **Monthly History** for monthly summaries, and **Unbalanced** to manage outstanding lending and borrowing.

When tracking loans, GlassBalance asks you to confirm repayment links. Removing an Unbalanced tracking record does **not** remove the corresponding financial transaction. Deleting the transaction itself **does** affect your balance.

## Your data and privacy

GlassBalance stores transaction data locally in SQLite. It does **not** require an account, connect to a bank, or automatically upload your ledger.

- **Local backups:** save a copy of your database before imports, upgrades, or major changes.
- **Encrypted email snapshots:** an optional, manually initiated feature that uses mail servers you configure; this is **not** automatic cross-device synchronization.
- **Update checking:** if enabled or triggered manually, it contacts GitHub to check available releases.
- **Local database encryption:** the SQLite database is **not encrypted at rest by default**. Consider operating-system full-disk encryption for additional protection.

**Never upload your personal database, backup files, or email credentials to a public repository.**

## Roadmap

| Milestone | Main goals |
|---|---|
| **v0.3.0-alpha.1** | Appearance themes, autocomplete, transaction comments and context menu, Unbalanced improvements, update checking. |
| **v0.3.0-alpha.2** | Windows installer, Ubuntu/Debian `.deb`, transaction categories, undo deletion, more charts, recurring transactions. |
| **v0.3.0-beta.1** | Stability, upgrade safety, performance, and Windows/Linux testing. |
| **v0.3.0** | Stable desktop release. |
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
