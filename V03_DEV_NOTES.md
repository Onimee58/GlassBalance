# v0.3.0 development preview (not a release)

Includes the previously tested update checker, the initial appearance settings (dark/light/system and custom accent), ledger context menu, and optional transaction comments. The edit-refresh path now blocks table signals during repopulation and preserves selection to reduce an observed post-save hang. The original cause has not been conclusively reproduced; human Ubuntu testing is required.

No automatic update installation, no new PDF importer, and no automatic loan repayment settlement.

The note field is stored in a new `transaction_comments` table. It is additive and does not change existing financial records; backups should be taken before testing. Full backward compatibility with earlier application versions is not guaranteed once new comments are saved (older apps won't display comments).

Current package was built from the locally available v0.3 update-checker source, NOT fetched from the live GitHub main branch. Check changes against the current `develop/v0.3.0` before committing.
