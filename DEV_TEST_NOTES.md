# GlassBalance v0.3.0 development testing — UI refinements

This is a development test build, **not an official release**. Back up your database first.

## New fixes
- Description autocomplete in New/Edit Transaction, Transactions search, and Balance Search (case-insensitive substring suggestions).
- Transactions-only global search bar: it is hidden on the other tabs, which have their own controls.
- Unbalanced person/description filter, selectable loan rows, and a dedicated **Remove selected from Unbalanced** button. Removal asks for confirmation and deletes only loan classification and repayment links, never transactions.
- Colored accent swatches rendered as icons, avoiding Qt stylesheet overrides.
- Native-Qt full custom color selector (non-native dialog).
- Keeps the optimized table sizing that resolved the Ubuntu edit-save freeze.

## Manual test checklist
- [ ] Back up financial database before launching.
- [ ] Create a transaction, type `wal` in the description: existing Walmart descriptions are suggested; selecting one does not fill the amount or date.
- [ ] Edit a transaction and verify suggestions are available and Save no longer freezes the application.
- [ ] Type `amm` in Transactions search and Balance Search: suggestion list appears; each tab displays corresponding results.
- [ ] In Unbalanced, confirm the top transaction search field is hidden and the loan-specific filter finds a person.
- [ ] Select the test loan, click **Remove selected from Unbalanced**, cancel once, confirm once. Original ledger total and transaction count must not change.
- [ ] Change all five accent presets: icons show distinct colors and selection updates the interface.
- [ ] Open custom color picker, enter hex/RGB color; verify it changes, saves and persists after app restart.
- [ ] Try Dark, Light, and System on Linux and Windows, checking navigation contrast.
- [ ] Test repayment confirmations: nothing links automatically.

## Automated testing
Run `python -m unittest discover -s tests -v` (17 tests expected).

Known limitation: UI could not be started in the authoring environment because PySide6 is unavailable there. Both desktop platforms need manual checks.
