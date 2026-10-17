# GlassBalance v0.3 development — testing checklist

**Before testing:** Make a local backup of your live ledger. For loan and edit tests, preferably use a separate test database. Do not publish a release until the results are reviewed.

Platform: __________  Build / commit: __________  Date: __________

## Editing freeze (critical)
- [ ] Edit a recent transaction, save; the interface remains responsive.
- [ ] Edit an older transaction (date, description and amount), save; verify totals.
- [ ] Edit descriptions only repeatedly (at least 10 times), without restarting.
- [ ] Confirm no duplicate edit is saved.
- [ ] Edit a transaction in a ledger with 2,600+ entries; app remains responsive.
- [ ] Test editing a linked loan transaction: amount changes are refused safely.
- [ ] Close/restart; verify all saved edits persist.

## Right-click ledger actions
- [ ] Right-click a transaction; Edit, Note, Find, Loan, Repayment and Delete appear.
- [ ] Add a note; inspect its tooltip; edit and clear the note.
- [ ] Find matching transactions opens Balance Search with relevant keyword.
- [ ] Track a transaction as loan; explicit confirmation is required.
- [ ] Link a repayment; explicit confirmation is required; cancel has no effect.
- [ ] Loan outstanding amount changes after confirmation, ledger balance does not.
- [ ] Delete still asks for confirmation.

## Appearance
- [ ] Dark theme remains readable.
- [ ] Light theme remains readable across dashboard, tables, dialogs and sidebar.
- [ ] System theme follows your OS at launch (check light and dark OS settings).
- [ ] Preset accent colors change the buttons and highlights.
- [ ] Custom color dialog accepts a selected shade and dismisses cleanly.
- [ ] Theme and custom accent persist after restart.
- [ ] Windows sidebar remains readable under every theme.

## Update checks & data integrity
- [ ] Manual update check works; offline state is nonblocking.
- [ ] Startup update check setting still persists.
- [ ] Existing ledger total and transaction count remain unchanged.
- [ ] Local and encrypted backup restore still work, including transaction notes.
- [ ] No unwanted downloads or automatic loan settlements occur.

Please report PASS/FAIL plus screenshots or logs for failures.
