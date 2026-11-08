import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
import release_info  # noqa: E402
import glassbalance  # noqa: E402


class ReleaseInfoTests(unittest.TestCase):
    def test_version_matches_package(self):
        self.assertEqual(release_info.version(), glassbalance.__version__)

    def test_debian_versions_sort_before_stable(self):
        self.assertEqual(release_info.deb_version("0.3.0-alpha.2"), "0.3.0~alpha2")
        self.assertEqual(release_info.deb_version("0.3.0-beta.1"), "0.3.0~beta1")
        self.assertEqual(release_info.deb_version("0.3.0"), "0.3.0")

    def test_changelog_has_notes_for_current_version(self):
        body = release_info.notes(release_info.version())
        self.assertNotIn("See CHANGELOG.md for details", body,
                         "Add a '## v<version>' section to CHANGELOG.md before releasing.")


if __name__ == "__main__":
    unittest.main()
