"""Fetch and optimize the public maintainer avatar at build time.

The application never makes a network request to display the About dialog.
"""
from pathlib import Path
from urllib.request import Request, urlopen

import os
os.makedirs(os.path.join(os.path.dirname(__file__), "..", "glassbalance", "assets"), exist_ok=True)

AVATAR_URL = (
    "https://avatars.githubusercontent.com/u/50075168"
    "?s=128&u=781ccb90f9a3b8c934f873352e15afe02ee08ff6&v=4"
)
TARGET = Path("glassbalance/assets/onimee58_avatar.png")


def main():
    if TARGET.is_file() and TARGET.stat().st_size > 0:
        print("Maintainer avatar already bundled.")
        return
    try:
        from PySide6.QtCore import QByteArray, QBuffer, QIODevice, Qt
        from PySide6.QtGui import QImage

        request = Request(AVATAR_URL, headers={"User-Agent": "GlassBalance-avatar-builder"})
        with urlopen(request, timeout=15) as response:
            data = response.read(250_001)
        if len(data) > 250_000:
            raise ValueError("Avatar exceeds download limit")
        image = QImage.fromData(data)
        if image.isNull():
            raise ValueError("Invalid image received")
        scaled = image.scaled(128, 128, Qt.AspectRatioMode.KeepAspectRatio,
                              Qt.TransformationMode.SmoothTransformation)
        output = QByteArray()
        buffer = QBuffer(output)
        if not buffer.open(QIODevice.OpenModeFlag.WriteOnly) or not scaled.save(buffer, "PNG"):
            raise ValueError("Failed to encode PNG")
        buffer.close()
        TARGET.parent.mkdir(parents=True, exist_ok=True)
        TARGET.write_bytes(bytes(output))
        print(f"Bundled 128px maintainer avatar: {TARGET.stat().st_size:,} bytes")
    except Exception as exc:
        print(f"Avatar unavailable; About dialog will show fallback: {exc}")


if __name__ == "__main__":
    main()
