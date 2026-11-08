"""Update metadata, asset selection and verification. Pure Python, no Qt, no ledger access.

The UI (updater_ui.py) does the networking; everything decided here is unit-tested.
"""
from __future__ import annotations

import hashlib
import os
import platform as _platform
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path, PurePosixPath

REPO = "Onimee58/GlassBalance"
RELEASES_URL = f"https://api.github.com/repos/{REPO}/releases/latest"
RELEASES_LIST_URL = f"https://api.github.com/repos/{REPO}/releases?per_page=15"
RELEASES_PAGE = f"https://github.com/{REPO}/releases"
TRUSTED_PAGE_PREFIX = f"https://github.com/{REPO}/releases/"
TRUSTED_ASSET_PREFIX = f"https://github.com/{REPO}/releases/download/"
CHECKSUM_ASSET = "SHA256SUMS.txt"

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


@dataclass(frozen=True)
class Asset:
    name: str
    url: str
    size: int


@dataclass(frozen=True)
class Release:
    version: str          # tag, e.g. "v0.3.0"
    url: str              # release page
    notes: str
    prerelease: bool
    assets: tuple[Asset, ...] = field(default_factory=tuple)

    def asset(self, name: str) -> Asset | None:
        return next((a for a in self.assets if a.name == name), None)


def parse_release(payload: object, *, allow_prerelease: bool = False,
                  page_prefix: str = TRUSTED_PAGE_PREFIX, asset_prefix: str = TRUSTED_ASSET_PREFIX) -> Release:
    """Validate one GitHub release object. Rejects drafts, unexpected URLs and bad versions."""
    if not isinstance(payload, dict) or payload.get("draft"):
        raise ValueError("Not a published release")
    if payload.get("prerelease") and not allow_prerelease:
        raise ValueError("Not a published stable release")
    tag, url = payload.get("tag_name"), payload.get("html_url")
    if not isinstance(tag, str) or not isinstance(url, str):
        raise ValueError("Release metadata incomplete")
    parse_version(tag)
    if not url.startswith(page_prefix):
        raise ValueError("Unexpected release URL")
    assets = []
    for item in payload.get("assets") or []:
        if not isinstance(item, dict):
            continue
        name, link, size = item.get("name"), item.get("browser_download_url"), item.get("size")
        if (isinstance(name, str) and isinstance(link, str) and isinstance(size, int)
                and link.startswith(asset_prefix) and "/" not in name and 0 < size < 1_000_000_000):
            assets.append(Asset(name, link, size))
    notes = payload.get("body") if isinstance(payload.get("body"), str) else ""
    return Release(tag, url, notes[:20000], bool(payload.get("prerelease")), tuple(assets))


def latest_stable_release(payload: object) -> dict[str, str]:
    """Backward-compatible summary used by older code paths and tests."""
    release = parse_release(payload)
    return {"version": release.version, "url": release.url}


def newest_release(payloads: object, *, allow_prerelease: bool, **prefixes) -> Release:
    """Pick the highest version from a /releases list (used for the opt-in test channel)."""
    if not isinstance(payloads, list):
        raise ValueError("Unexpected release list")
    found = []
    for item in payloads:
        try:
            found.append(parse_release(item, allow_prerelease=allow_prerelease, **prefixes))
        except ValueError:
            continue
    if not found:
        raise ValueError("No published releases found")
    best = found[0]
    for candidate in found[1:]:
        if is_newer(candidate.version, best.version):
            best = candidate
    return best


# ---------------------------------------------------------------- install kind

WINDOWS_INSTALLER = "windows-installer"
WINDOWS_PORTABLE = "windows-portable"
LINUX_DEB = "deb"
LINUX_PORTABLE = "linux-portable"
MACOS_APP = "macos-app"
SOURCE = "source"
DEB_PREFIX = PurePosixPath("/opt/glassbalance")


def install_kind(executable: str | None = None, system: str | None = None, frozen: bool | None = None) -> str:
    """How this copy was installed, which decides whether it can update itself."""
    executable = executable or sys.executable
    system = system or sys.platform
    frozen = getattr(sys, "frozen", False) if frozen is None else frozen
    if not frozen:
        return SOURCE
    exe = Path(executable)
    if system == "win32":
        return WINDOWS_INSTALLER if any(exe.parent.glob("unins*.exe")) else WINDOWS_PORTABLE
    if system == "darwin":
        return MACOS_APP if ".app/Contents/MacOS" in exe.as_posix() else SOURCE
    # Linux paths are compared as POSIX paths so this also evaluates correctly when the
    # test suite runs on Windows (where Path("/opt/...") would become "D:\\opt\\...").
    if os.name == "posix":
        try:
            executable = os.path.realpath(executable)   # /usr/bin/glassbalance -> /opt/glassbalance/...
        except OSError:
            pass
    posix = PurePosixPath(executable.replace("\\", "/"))
    return LINUX_DEB if DEB_PREFIX in posix.parents else LINUX_PORTABLE


_ASSET_PATTERNS = {
    WINDOWS_INSTALLER: re.compile(r"GlassBalance-Setup-v[0-9A-Za-z.\-]+-Windows-x64\.exe"),
    LINUX_DEB: re.compile(r"glassbalance_[0-9A-Za-z.~\-]+_amd64\.deb"),
    MACOS_APP: re.compile(r"GlassBalance-v[0-9A-Za-z.\-]+-macOS-arm64\.dmg"),
}


def choose_asset(release: Release, kind: str, machine: str | None = None) -> Asset | None:
    """The installer this copy can apply, or None (then the release page is offered)."""
    if kind == MACOS_APP and (machine or _platform.machine()) != "arm64":
        return None  # only Apple Silicon builds are published
    pattern = _ASSET_PATTERNS.get(kind)
    if pattern is None:
        return None
    return next((a for a in release.assets if pattern.fullmatch(a.name)), None)


# ---------------------------------------------------------------- verification

def parse_checksums(text: str) -> dict[str, str]:
    """Parse `sha256sum` output: '<64 hex>  <name>' (optional '*' binary marker)."""
    result = {}
    for line in text.splitlines():
        match = re.fullmatch(r"\s*([0-9a-fA-F]{64})\s+\*?(\S.*?)\s*", line)
        if match:
            result[match.group(2)] = match.group(1).lower()
    return result


def sha256_file(path: str | Path) -> str:
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def verify_download(path: str | Path, asset: Asset, checksums: dict[str, str]) -> None:
    """Raise ValueError unless size and SHA-256 match the published values."""
    path = Path(path)
    expected = checksums.get(asset.name)
    if not expected:
        raise ValueError("This release has no published checksum for the installer; it will not be run.")
    if path.stat().st_size != asset.size:
        raise ValueError("The download is incomplete (size mismatch). Please try again.")
    if sha256_file(path) != expected:
        raise ValueError("The download is corrupted (checksum mismatch). It was deleted and will not be run.")


# ---------------------------------------------------------------- messages

NETWORK_MESSAGES = {
    "offline": ("You appear to be offline",
                "GlassBalance couldn't reach GitHub. Check your internet connection and try again. "
                "Your ledger works fully offline in the meantime."),
    "timeout": ("The connection timed out",
                "GitHub didn't respond in time. Your connection may be slow or a firewall may be blocking it."),
    "tls": ("Secure connection failed",
            "A secure (HTTPS) connection to GitHub couldn't be established. A proxy, captive portal or "
            "incorrect system clock can cause this. Nothing was downloaded."),
    "rate_limited": ("GitHub is limiting requests",
                     "Too many update checks came from your network recently. Please try again in about an hour."),
    "not_found": ("No release found",
                  "GitHub didn't return a release for GlassBalance. Try again later or open the releases page."),
    "server": ("GitHub is having problems",
               "GitHub returned a server error. This is usually temporary; please try again later."),
    "other": ("Update check failed",
              "Something unexpected went wrong while contacting GitHub."),
}


def network_message(category: str, detail: str = "") -> tuple[str, str]:
    title, text = NETWORK_MESSAGES.get(category, NETWORK_MESSAGES["other"])
    if category == "other" and detail:
        text = f"{text}\n\nDetails: {detail}"
    return title, text


def human_size(size: int) -> str:
    value = float(size)
    for unit in ("B", "KB", "MB", "GB"):
        if value < 1024 or unit == "GB":
            return f"{value:.0f} {unit}" if unit in ("B", "KB") else f"{value:.1f} {unit}"
        value /= 1024
    return f"{size} B"
