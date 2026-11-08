# In-app updater: test plan (v0.3.0-beta.1)

The updater can only be tested end to end between **two published releases** that both contain it.
beta.1 is the first one, so the real install test happens when beta.2 (or v0.3.0) is published.

## Before beta.2 exists (beta.1 alone)
1. **Up to date / older stable**: with normal settings, About → *Check for updates…* says *You're up to date*.
   (The latest stable is v0.2.0, which is older than beta.1.)
2. **Offline**: disconnect from the network, then check again → *You appear to be offline* with **Try again**. Reconnect, then Try again → works.
   Start the app offline → no popup at all.
3. **Startup toggle**: About → Startup checks Off → restart → no check is made.

## Pre-release channel (testers only)
Launch with the environment variable set so betas are offered:
- Ubuntu: `GLASSBALANCE_UPDATE_CHANNEL=prerelease /opt/glassbalance/GlassBalance`
- Windows (cmd): `set GLASSBALANCE_UPDATE_CHANNEL=prerelease` and then run `"%LOCALAPPDATA%\Programs\GlassBalance\GlassBalance.exe"`
- macOS: `GLASSBALANCE_UPDATE_CHANNEL=prerelease open -a GlassBalance`

## When beta.2 is published (install beta.1 first, channel = prerelease)
| Step | Windows (Setup.exe) | Ubuntu (.deb) | macOS |
|---|---|---|---|
| Dialog shows beta.2 notes, size | ✓ | ✓ | ✓ |
| Progress bar moves; **Cancel** returns to the offer, nothing left in the cache | ✓ | ✓ | ✓ |
| Unplug the network mid-download → friendly error + Try again | ✓ | ✓ | ✓ |
| *Install and restart* creates `before-update-to-…sqlite` in backups | ✓ | ✓ | ✓ |
| Install | silent, **no** UAC prompt | password dialog appears | disk image opens |
| Cancel the password dialog → *Installation cancelled*, nothing changed | n/a | ✓ | n/a |
| App restarts on its own at the new version; ledger intact | ✓ | ✓ | drag to Applications, then reopen |
| **Skip this version** → restart → no popup; manual check still offers it | ✓ | ✓ | ✓ |

Portable ZIPs and source checkouts should offer **Open release page** instead of installing.
