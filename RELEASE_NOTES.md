# GlassBalance v0.2.0-alpha.2 — Search & Unbalanced preview

**Alpha / pre-release — back up your ledger before upgrading.**

- Dedicated Balance Search tab with case-insensitive descriptions, matching transactions, totals in/out and signed net.
- Opt-in Unbalanced tracker: classify an existing negative transaction as money lent or positive as borrowed, by person.
- Refund/repayment suggestions are **never automatically linked**. Confirm, dismiss or cancel individually.
- Partial repayments, outstanding balances and explicit unlink. Loan links never add or subtract ledger transactions.
- Prevent changing the amount of a transaction already tied to a loan; unlink first.
- Refreshed About dialog with maintainer credit, GitHub link, and optional bundled 128px avatar.
- Existing SQLite file is compatible. Loan tables are created without replacing the ledger.

**Limitations:** The first alpha.2 loan workflow selects an existing transaction from a list. Only keyword-matched refunds are suggested for confirmation. Manual linking of unmatched repayments, loan deletion, and advanced loan editing are deferred. Avatar is fetched during GitHub Actions packaging when available and otherwise uses a placeholder; no network request at application startup. Not yet independently GUI-tested on both platforms.
