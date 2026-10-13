# Maintainer avatar

The build uses the public GitHub profile image supplied by the project maintainer:

https://avatars.githubusercontent.com/u/50075168?s=400&u=781ccb90f9a3b8c934f873352e15afe02ee08ff6&v=4

During GitHub Actions packaging, `scripts/fetch_avatar.py` fetches the image and bundles a
128-pixel optimized PNG at `glassbalance/assets/onimee58_avatar.png`. At runtime, no
internet is required. If the fetch is unavailable, the About dialog displays the
fallback symbol. The `Change profile picture (local)` button can be used instead.

The avatar is not included in this source archive because the image host was
unreachable from the source-packaging environment.
