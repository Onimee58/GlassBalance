# GlassBalance v0.3.0-alpha.2: manual test checklist

Development build. **Back up your ledger first** (Save backup, and also copy the `.sqlite` file elsewhere).
Run every section on **Ubuntu** and **Windows** (1366 × 768, 100%). Run sections A–F on **macOS** too.

## A. Migration on your real data (do this first)
1. Open a *copy* of your real ledger with the new build.
2. Transaction count, total balance, a few running balances, comments, Unbalanced loans and appearance settings match alpha.1.
3. Every transaction shows **Uncategorized**. Restart; nothing changed.
4. Restore an **older** backup (from v0.2/alpha.1). The app opens, and Categories, Recurring and Unbalanced tabs all work.

## B. Categories
1. Set a category via **Set category** and via right-click. Balance and running balances are unchanged.
2. Type a new category, then reuse it with different capitalization (`groceries` vs `Groceries`): only one category exists.
3. Choose **Uncategorized** to clear a category.
4. Type a category name into the Transactions search box; matching rows appear.
5. Restart: categories persisted.
6. Export CSV and XLSX: a **Category** column is present. Import into an empty test ledger: categories come back.

## C. Categories & charts
1. Total expenses in the summary line equal the sum of **Expenses** in Monthly history (all months).
2. Income − Expenses equals Total balance − Opening balance.
3. Category counts add up to the total transaction count. Uncategorized is included.
4. With more than 10 categories, the chart groups the rest as "Other". Check Dark and Light modes.

## D. Undo deletion
1. Add a temporary transaction with a comment and category. Delete it, then Undo. ID (hover/tooltip or export), comment, category and balance are restored.
2. Delete A, then delete B, then Undo: only **B** returns, A stays deleted.
3. Delete, edit a different transaction, then Undo: running balances are correct.
4. Delete, then restart: Undo is no longer available (session-only by design).
5. Delete, then restore a backup: Undo is cleared.
6. Try deleting a transaction that is a loan origin, and one that is a linked repayment: both are refused with an explanation. After removing tracking/unlinking, deletion works.

## E. Recurring
1. Add a template: balance and transaction count are unchanged.
2. **Post selected for this month**: confirmation appears; balance changes only after you confirm; the posted entry has the template's category.
3. Post the same template again this month: the button is disabled. **Restart** and check that it is still disabled.
4. Template with day 31: the posted date is the last day of the current month.
5. Remove the template: the posted transaction remains.
6. Delete the posted transaction: posting is allowed again. Instead, Undo the deletion: posting is blocked again.

## F. Regression
- Ubuntu: edit a transaction in the full 2,600+ ledger; no freeze. Switching tabs is responsive.
- Update checker, Unbalanced (track, link, unlink, remove), right-click menu legibility in Dark and Light modes, Balance Search, encrypted email backup.
- Windows: Setup.exe install, upgrade over the previous alpha.2 install, uninstall; ledger preserved.
- Ubuntu: `.deb` install, upgrade, **and `sudo apt remove glassbalance`**; ledger preserved.

## G. macOS (experimental)
1. Open the `.dmg`, drag GlassBalance to Applications.
2. First launch is blocked (unsigned). Allow it in System Settings → Privacy & Security → *Open Anyway*. Record the exact macOS version and steps needed.
3. Ledger is created under `~/Library/Application Support/GlassBalance/`. Delete the app and reinstall: the ledger survives.
4. Check fonts, Dark/Light/System appearance, context menus, dialogs, the Dock icon and window resizing.
5. Report the Mac model (Apple Silicon or Intel). This build is Apple Silicon only.

## Known limitations
- Undo is session-only and covers the most recent deletion.
- Charts cover all transactions; no date-range filter yet.
- Comments are not included in CSV/XLSX export (unchanged from alpha.1).
- macOS build is not notarized; Intel Macs are not supported.
