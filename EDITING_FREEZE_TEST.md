# GlassBalance v0.3 development: editing freeze diagnostic patch

The previous fix did not prevent an Ubuntu freeze after saving edits. This patch replaces Qt header ResizeToContents with stable widths for the large transaction table. Dynamic measurement on a table with 2,600+ records could stall the Qt GUI during refresh. This is a suspected performance cause, not a proven diagnosis.

## Test on Ubuntu

1. Back up your existing ledger first.
2. Run the updated source: `./run-linux.sh`.
3. Edit and save a transaction at least 10 times (including changing date and amount).
4. Check that the app remains responsive, table and running balances reflect edits, and data survives a restart.
5. If GNOME says Not Responding, click **Wait** first and time how long until the UI responds. Do not repeat Save.
6. Report how long the freeze lasts and copy the terminal output if it persists.

This build is for testing only. It does not prove the underlying freeze has been solved.
