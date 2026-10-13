# GlassBalance v0.2.0-alpha.2 — UI fix

This is a source update for the existing alpha.2 branch, not a new release tag.

## Changes

- Sidebar is vertically scrollable on smaller windows to prevent the bottom text from being cropped.
- About GlassBalance now has **Change profile picture (local)**. Select an image downloaded from your GitHub profile. The app resizes and stores a 128-pixel PNG locally, and uses it offline.
- The existing GitHub Actions build-time avatar downloader remains in place, so published binaries may include the profile picture automatically when GitHub is reachable during the build.

## Update your GitHub branch

1. Make a backup in the running app first.
2. Replace `glassbalance/ui.py` with the updated file; optionally include this changelog.
3. Commit to `v0.2.0-alpha.2` (this will trigger a workflow only if your workflow is configured for branch pushes, otherwise use Run workflow).
4. Test the new executable before replacing any release asset. Existing ledger data should stay unchanged.

## Privacy

Do not commit your local database, backups, or curated transaction Excel files.
