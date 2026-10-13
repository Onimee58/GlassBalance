# Changelog

## v0.2.0-alpha.2

- Dedicated Balance Search tab with in/out/net totals.
- Opt-in Unbalanced loan tracker; user confirmation required for every repayment match.
- Partial repayments and unlinking; no effect on ledger balance.
- About dialog image support and build-time low-resolution GitHub avatar fetch.
- Regression tests for loan accounting and settlement safeguards.

## v0.2.0-alpha

- Native Qt glass-inspired interface redesign, balance trend chart and creator credit.

### UI fixes for alpha.2 (test build)
- Sidebar navigation scrolls on shorter windows and with larger text scaling, preventing footer controls from being clipped.
- About window allows the maintainer to select an avatar locally; it is resized to 128 pixels and saved in the app's local data directory for offline use.
- The packaged GitHub avatar is still used as the default when available.
