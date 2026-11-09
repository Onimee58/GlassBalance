"""Repository hygiene: scripts users run directly must stay executable after a fresh clone."""
import os
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
EXECUTABLES = ["run-linux.sh", "app.py", "scripts/install-linux.sh", "scripts/uninstall-linux.sh",
               "scripts/build_macos.sh"]


class ExecutableBitTests(unittest.TestCase):
    @unittest.skipUnless(os.name == "posix", "Windows checkouts have no executable bit")
    def test_scripts_are_executable(self):
        missing = [name for name in EXECUTABLES if not os.access(ROOT / name, os.X_OK)]
        self.assertEqual(missing, [], "Run: git update-index --chmod=+x " + " ".join(missing))

    def test_scripts_have_shebang(self):
        for name in EXECUTABLES:
            with open(ROOT / name, "rb") as handle:
                self.assertTrue(handle.read(2) == b"#!", f"{name} needs a #! line")


if __name__ == "__main__":
    unittest.main()
