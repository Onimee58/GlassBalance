"""Pure update metadata validation and SemVer comparison; no financial data access."""
from __future__ import annotations

import re

RELEASES_URL = "https://api.github.com/repos/Onimee58/GlassBalance/releases/latest"
RELEASES_PAGE = "https://github.com/Onimee58/GlassBalance/releases"
_VERSION = re.compile(r"^v?(\d+)\.(\d+)\.(\d+)(?:-([0-9A-Za-z.-]+))?(?:\+[0-9A-Za-z.-]+)?$")


def parse_version(text: str):
    match = _VERSION.fullmatch(text.strip())
    if not match:
        raise ValueError(f"Unsupported version: {text!r}")
    major, minor, patch, prerelease = match.groups()
    tokens = []
    if prerelease:
        for token in prerelease.split("."):
            if not token or (token.isdigit() and len(token)>1 and token.startswith("0")):
                raise ValueError("Invalid prerelease label")
            tokens.append(int(token) if token.isdigit() else token)
    return (int(major), int(minor), int(patch)), tuple(tokens)


def is_newer(latest: str, installed: str) -> bool:
    a, apre = parse_version(latest)
    b, bpre = parse_version(installed)
    if a != b:
        return a > b
    if not apre:
        return bool(bpre)
    if not bpre:
        return False
    for left, right in zip(apre, bpre):
        if left == right:
            continue
        if isinstance(left, int) and isinstance(right, str):
            return False
        if isinstance(left, str) and isinstance(right, int):
            return True
        return left > right
    return len(apre) > len(bpre)


def latest_stable_release(payload: object) -> dict[str, str]:
    if not isinstance(payload, dict) or payload.get('draft') or payload.get('prerelease'):
        raise ValueError("Not a published stable release")
    tag = payload.get('tag_name')
    url = payload.get('html_url')
    if not isinstance(tag, str) or not isinstance(url, str):
        raise ValueError("Release metadata incomplete")
    parse_version(tag)
    if not url.startswith('https://github.com/Onimee58/GlassBalance/releases/'):
        raise ValueError("Unexpected release URL")
    return {'version': tag, 'url': url}
