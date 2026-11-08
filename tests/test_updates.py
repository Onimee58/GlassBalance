import hashlib
import tempfile
import unittest
from pathlib import Path

from glassbalance import update_check as uc

PAGE = "https://github.com/Onimee58/GlassBalance/releases/tag/v0.3.0"
DL = "https://github.com/Onimee58/GlassBalance/releases/download/v0.3.0/"


def release_payload(tag="v0.3.0", prerelease=False, assets=None):
    names = assets if assets is not None else [
        "GlassBalance-Setup-v0.3.0-Windows-x64.exe", "glassbalance_0.3.0_amd64.deb",
        "GlassBalance-v0.3.0-macOS-arm64.dmg", "GlassBalance-v0.3.0-Linux-x64-Portable.zip", "SHA256SUMS.txt"]
    return {"tag_name": tag, "html_url": PAGE.replace("v0.3.0", tag), "draft": False, "prerelease": prerelease,
            "body": "## Notes", "assets": [{"name": n, "browser_download_url": DL + n, "size": 1234} for n in names]}


class VersionTests(unittest.TestCase):
    def test_versions(self):
        self.assertTrue(uc.is_newer('v0.3.0', '0.2.0'))
        self.assertTrue(uc.is_newer('0.3.0', '0.3.0-beta.2'))
        self.assertTrue(uc.is_newer('0.3.0-beta.2', '0.3.0-beta.1'))
        self.assertTrue(uc.is_newer('0.3.0-beta.1', '0.3.0-alpha.2'))
        self.assertFalse(uc.is_newer('0.2.0', '0.3.0'))
        self.assertFalse(uc.is_newer('0.3.0-beta.1', '0.3.0'))
        self.assertFalse(uc.is_newer('v0.2.0', '0.2.0'))
        with self.assertRaises(ValueError):
            uc.parse_version('not a version')


class ReleaseParsingTests(unittest.TestCase):
    def test_stable_release_and_assets(self):
        r = uc.parse_release(release_payload())
        self.assertEqual(r.version, "v0.3.0")
        self.assertEqual(len(r.assets), 5)
        self.assertEqual(uc.latest_stable_release(release_payload())["version"], "v0.3.0")

    def test_rejects_prerelease_draft_and_foreign_urls(self):
        with self.assertRaises(ValueError):
            uc.parse_release(release_payload(prerelease=True))
        self.assertTrue(uc.parse_release(release_payload(prerelease=True), allow_prerelease=True).prerelease)
        with self.assertRaises(ValueError):
            uc.parse_release({**release_payload(), "draft": True}, allow_prerelease=True)
        with self.assertRaises(ValueError):
            uc.parse_release({**release_payload(), "html_url": "https://evil.example/x"})
        bad = release_payload()
        bad["assets"][0]["browser_download_url"] = "https://evil.example/Setup.exe"
        self.assertNotIn("GlassBalance-Setup-v0.3.0-Windows-x64.exe", [a.name for a in uc.parse_release(bad).assets])

    def test_newest_release_from_list(self):
        items = [release_payload("v0.3.0-beta.1", True), release_payload("v0.2.0"), release_payload("v0.3.0-beta.2", True)]
        self.assertEqual(uc.newest_release(items, allow_prerelease=True).version, "v0.3.0-beta.2")
        self.assertEqual(uc.newest_release(items, allow_prerelease=False).version, "v0.2.0")


class InstallKindTests(unittest.TestCase):
    def test_kinds(self):
        self.assertEqual(uc.install_kind("/x/python", "linux", False), uc.SOURCE)
        self.assertEqual(uc.install_kind("/opt/glassbalance/GlassBalance", "linux", True), uc.LINUX_DEB)
        self.assertEqual(uc.install_kind("/home/u/GlassBalance/GlassBalance", "linux", True), uc.LINUX_PORTABLE)
        self.assertEqual(uc.install_kind("/Applications/GlassBalance.app/Contents/MacOS/GlassBalance", "darwin", True),
                         uc.MACOS_APP)
        with tempfile.TemporaryDirectory() as d:
            exe = Path(d) / "GlassBalance.exe"
            exe.write_bytes(b"x")
            self.assertEqual(uc.install_kind(str(exe), "win32", True), uc.WINDOWS_PORTABLE)
            (Path(d) / "unins000.exe").write_bytes(b"x")
            self.assertEqual(uc.install_kind(str(exe), "win32", True), uc.WINDOWS_INSTALLER)

    def test_choose_asset(self):
        r = uc.parse_release(release_payload())
        self.assertEqual(uc.choose_asset(r, uc.WINDOWS_INSTALLER).name, "GlassBalance-Setup-v0.3.0-Windows-x64.exe")
        self.assertEqual(uc.choose_asset(r, uc.LINUX_DEB).name, "glassbalance_0.3.0_amd64.deb")
        self.assertEqual(uc.choose_asset(r, uc.MACOS_APP, machine="arm64").name, "GlassBalance-v0.3.0-macOS-arm64.dmg")
        self.assertIsNone(uc.choose_asset(r, uc.MACOS_APP, machine="x86_64"))
        for kind in (uc.WINDOWS_PORTABLE, uc.LINUX_PORTABLE, uc.SOURCE):
            self.assertIsNone(uc.choose_asset(r, kind))


class VerificationTests(unittest.TestCase):
    def test_checksums_and_verify(self):
        data = b"installer bytes"
        digest = hashlib.sha256(data).hexdigest()
        sums = uc.parse_checksums(f"{digest}  Setup.exe\n{'0'*64} *other.deb\ngarbage line\n")
        self.assertEqual(sums, {"Setup.exe": digest, "other.deb": "0"*64})
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / "Setup.exe"
            path.write_bytes(data)
            uc.verify_download(path, uc.Asset("Setup.exe", DL + "Setup.exe", len(data)), sums)
            with self.assertRaisesRegex(ValueError, "size"):
                uc.verify_download(path, uc.Asset("Setup.exe", DL, len(data) + 1), sums)
            path.write_bytes(b"tampered bytes!")
            with self.assertRaisesRegex(ValueError, "checksum"):
                uc.verify_download(path, uc.Asset("Setup.exe", DL, len(b"tampered bytes!")), sums)
            with self.assertRaisesRegex(ValueError, "no published checksum"):
                uc.verify_download(path, uc.Asset("Unknown.exe", DL, 1), sums)

    def test_messages(self):
        for category in ("offline", "timeout", "tls", "rate_limited", "not_found", "server"):
            title, text = uc.network_message(category)
            self.assertTrue(title and text)
        self.assertIn("boom", uc.network_message("other", "boom")[1])
        self.assertEqual(uc.human_size(52_428_800), "50.0 MB")


if __name__ == '__main__':
    unittest.main()
