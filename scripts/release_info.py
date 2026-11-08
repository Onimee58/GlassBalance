"""Single source of release metadata, derived from glassbalance/__init__.py.

Usage: python scripts/release_info.py version|tag|deb|prerelease|notes OUTFILE
No third-party imports, so it runs on any CI runner before dependencies are installed.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def version() -> str:
    text = (ROOT / "glassbalance" / "__init__.py").read_text(encoding="utf-8")
    match = re.search(r'^__version__\s*=\s*["\']([^"\']+)["\']', text, re.M)
    if not match:
        raise SystemExit("Cannot find __version__ in glassbalance/__init__.py")
    value = match.group(1)
    if not re.fullmatch(r"\d+\.\d+\.\d+(-(alpha|beta|rc)\.\d+)?", value):
        raise SystemExit(f"Unsupported version format: {value!r} (expected 1.2.3 or 1.2.3-beta.4)")
    return value


def is_prerelease(value: str) -> bool:
    return "-" in value


def deb_version(value: str) -> str:
    """0.3.0-alpha.2 -> 0.3.0~alpha2 ('~' sorts before the final 0.3.0 in dpkg)."""
    if not is_prerelease(value):
        return value
    base, pre = value.split("-", 1)
    return f"{base}~{pre.replace('.', '')}"


def notes(value: str) -> str:
    """The CHANGELOG.md section whose heading starts with '## v<version>'."""
    lines = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8").splitlines()
    out, inside = [], False
    for line in lines:
        if line.startswith("## "):
            if inside:
                break
            inside = re.match(rf"## v{re.escape(value)}(\s|$|\()", line) is not None
            continue
        if inside:
            out.append(line)
    body = "\n".join(out).strip()
    if not body:
        body = f"GlassBalance v{value}. See CHANGELOG.md for details."
    banner = ("**Pre-release for testing. Back up your ledger before installing.**\n\n"
              if is_prerelease(value) else "")
    return banner + body + "\n"


if __name__ == "__main__":
    command = sys.argv[1] if len(sys.argv) > 1 else "version"
    v = version()
    if command == "version":
        print(v)
    elif command == "tag":
        print(f"v{v}")
    elif command == "deb":
        print(deb_version(v))
    elif command == "prerelease":
        print("true" if is_prerelease(v) else "false")
    elif command == "notes":
        Path(sys.argv[2]).write_text(notes(v), encoding="utf-8")
    else:
        raise SystemExit(f"Unknown command {command!r}")
