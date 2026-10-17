"""Package the PyInstaller onedir output into an amd64 Debian package.

Build on Ubuntu after running scripts/build_bundle.py. No root required.
"""
from __future__ import annotations
import os
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
VERSION = "0.3.0~alpha2"
PACKAGE = f"glassbalance_{VERSION}_amd64.deb"


def build() -> Path:
    source = ROOT / "dist" / "GlassBalance"
    if not (source / "GlassBalance").is_file():
        raise FileNotFoundError("Build the PyInstaller onedir distribution first")
    staging = ROOT / "build" / "deb-root"
    if staging.exists():
        shutil.rmtree(staging)
    app = staging / "opt" / "glassbalance"
    shutil.copytree(source, app)
    for file in app.rglob("*"):
        if file.is_file():
            file.chmod(0o755 if os.access(file, os.X_OK) else 0o644)
    (app / "GlassBalance").chmod(0o755)
    binary = staging / "usr" / "bin" / "glassbalance"
    binary.parent.mkdir(parents=True, exist_ok=True)
    binary.symlink_to("/opt/glassbalance/GlassBalance")
    desktop = staging / "usr" / "share" / "applications" / "io.github.Onimee58.GlassBalance.desktop"
    desktop.parent.mkdir(parents=True, exist_ok=True)
    desktop.write_text("""[Desktop Entry]
Type=Application
Version=1.0
Name=GlassBalance
Comment=Offline-first personal finance ledger
Exec=/opt/glassbalance/GlassBalance
Icon=io.github.Onimee58.GlassBalance
Terminal=false
Categories=Office;Finance;
StartupNotify=true
StartupWMClass=GlassBalance
""", encoding="utf8")
    icon = staging / "usr" / "share" / "icons" / "hicolor" / "256x256" / "apps" / "io.github.Onimee58.GlassBalance.png"
    icon.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(ROOT / "glassbalance" / "assets" / "glassbalance_icon.png", icon)
    control = staging / "DEBIAN" / "control"
    control.parent.mkdir(parents=True, exist_ok=True)
    control.write_text("""Package: glassbalance
Version: 0.3.0~alpha2
Section: utils
Priority: optional
Architecture: amd64
Maintainer: Onimee58 <noreply@users.noreply.github.com>
Homepage: https://github.com/Onimee58/GlassBalance
Description: Offline-first native desktop personal finance ledger
 Private SQLite finance ledger with transaction search and loan tracking.
""",encoding="utf8")
    target=ROOT / PACKAGE
    subprocess.run(["dpkg-deb", "--build", "--root-owner-group", str(staging), str(target)], check=True)
    return target


if __name__ == "__main__":
    print(build())
