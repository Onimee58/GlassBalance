"""Update dialog: check → notes → download with progress → verify → back up → install → restart.

Networking uses Qt's asynchronous QNetworkAccessManager, so the window never freezes.
Only public release metadata is requested; no ledger data ever leaves the computer.
"""
from __future__ import annotations

import json
import os
import shutil
import sys
from datetime import datetime
from pathlib import Path

from PySide6.QtCore import QProcess, QStandardPaths, Qt, QTimer, QUrl
from PySide6.QtGui import QDesktopServices, QGuiApplication
from PySide6.QtNetwork import QNetworkReply, QNetworkRequest
from PySide6.QtWidgets import (QApplication, QDialog, QHBoxLayout, QLabel, QProgressBar, QPushButton,
                               QTextBrowser, QVBoxLayout)

from . import __version__
from . import update_check as uc

USER_AGENT = f"GlassBalance/{__version__} (update check)".encode()
SKIP_KEY = "updates/skipped_version"
CHANNEL_ENV = "GLASSBALANCE_UPDATE_CHANNEL"   # "prerelease" opts testers into betas


def prerelease_channel() -> bool:
    return os.environ.get(CHANNEL_ENV, "").strip().lower() == "prerelease"


def _header(reply: QNetworkReply, name: str) -> str:
    """rawHeader takes bytes in older PySide6 releases and str in newer ones."""
    for arg in (name, name.encode()):
        try:
            return bytes(reply.rawHeader(arg)).decode("latin-1")
        except TypeError:
            continue
    return ""


def classify(reply: QNetworkReply) -> tuple[str, str]:
    """Map a failed QNetworkReply to a user-facing category from update_check.NETWORK_MESSAGES."""
    E = QNetworkReply.NetworkError
    err = reply.error()
    status = reply.attribute(QNetworkRequest.Attribute.HttpStatusCodeAttribute)
    remaining = _header(reply, "x-ratelimit-remaining") or None
    if status in (403, 429) and (status == 429 or remaining == "0"):
        return "rate_limited", ""
    if err in (E.HostNotFoundError, E.ConnectionRefusedError, E.NetworkSessionFailedError,
               E.TemporaryNetworkFailureError, E.UnknownNetworkError, E.ProxyNotFoundError,
               E.ProxyConnectionRefusedError, E.RemoteHostClosedError):
        return "offline", ""
    if err in (E.TimeoutError, E.OperationCanceledError, E.ProxyTimeoutError):
        return "timeout", ""
    if err == E.SslHandshakeFailedError:
        return "tls", ""
    if err == E.ContentNotFoundError or status == 404:
        return "not_found", ""
    if isinstance(status, int) and status >= 500:
        return "server", ""
    return "other", reply.errorString()


def download_dir() -> Path:
    base = QStandardPaths.writableLocation(QStandardPaths.StandardLocation.CacheLocation)
    path = Path(base or Path.home() / ".cache" / "glassbalance") / "updates"
    path.mkdir(parents=True, exist_ok=True)
    return path


class UpdateDialog(QDialog):
    """One dialog that walks through every update state."""

    def __init__(self, window, *, release: uc.Release | None = None, api_url: str | None = None,
                 trusted: dict | None = None, kind: str | None = None):
        super().__init__(window)
        self.window_ref = window
        self.network = window.update_network
        self.settings = window.update_settings
        self.api_url = api_url or (uc.RELEASES_LIST_URL if prerelease_channel() else uc.RELEASES_URL)
        self.trusted = trusted or {}
        self.kind = kind or uc.install_kind()
        self.release = release
        self.asset: uc.Asset | None = None
        self.reply: QNetworkReply | None = None
        self.file = None
        self.part_path: Path | None = None
        self.installer_path: Path | None = None
        self.process: QProcess | None = None
        self.state = "idle"

        self.setWindowTitle("GlassBalance updates")
        self.setMinimumWidth(500)
        outer = QVBoxLayout(self)
        outer.setContentsMargins(24, 22, 24, 20)
        outer.setSpacing(12)
        self.title = QLabel()
        self.title.setObjectName("section")
        self.title.setWordWrap(True)
        self.text = QLabel()
        self.text.setObjectName("muted")
        self.text.setWordWrap(True)
        self.text.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        self.notes = QTextBrowser()
        self.notes.setOpenExternalLinks(True)
        self.notes.setMinimumHeight(170)
        self.progress = QProgressBar()
        self.progress.setTextVisible(True)
        self.detail = QLabel()
        self.detail.setObjectName("muted")
        self.detail.setWordWrap(True)
        for widget in (self.title, self.text, self.notes, self.progress, self.detail):
            outer.addWidget(widget)
        row = QHBoxLayout()
        self.tertiary = QPushButton()
        self.secondary = QPushButton()
        self.primary = QPushButton()
        self.primary.setObjectName("primary")
        row.addWidget(self.tertiary)
        row.addStretch()
        row.addWidget(self.secondary)
        row.addWidget(self.primary)
        outer.addLayout(row)
        for b in (self.primary, self.secondary, self.tertiary):
            b.setCursor(Qt.CursorShape.PointingHandCursor)
            b.clicked.connect(self._clicked)
        self._actions = {}

        if release is not None:
            self.show_available()
        else:
            QTimer.singleShot(0, self.check)

    # ------------------------------------------------------------ view helpers
    def _view(self, state, title, text="", *, notes=None, progress=None, detail="",
              primary=None, secondary=None, tertiary=None):
        self.state = state
        self.title.setText(title)
        self.text.setText(text)
        self.text.setVisible(bool(text))
        self.notes.setVisible(notes is not None)
        if notes is not None:
            self.notes.setMarkdown(notes or "_No release notes provided._")
        self.progress.setVisible(progress is not None)
        if progress == "busy":
            self.progress.setRange(0, 0)
        elif progress is not None:
            self.progress.setRange(0, 1000)
            self.progress.setValue(int(progress * 1000))
        self.detail.setText(detail)
        self.detail.setVisible(bool(detail))
        self._actions = {}
        for btn, spec in ((self.primary, primary), (self.secondary, secondary), (self.tertiary, tertiary)):
            btn.setVisible(spec is not None)
            btn.setEnabled(True)
            if spec:
                btn.setText(spec[0])
                self._actions[btn] = spec[1]
        self.adjustSize()

    def _clicked(self):
        action = self._actions.get(self.sender())
        if action:
            action()

    def _open_page(self):
        QDesktopServices.openUrl(QUrl(self.release.url if self.release else uc.RELEASES_PAGE))

    # ------------------------------------------------------------ 1. check
    def check(self):
        self._view("checking", "Checking for updates…", "Contacting GitHub Releases.", progress="busy",
                   secondary=("Cancel", self._cancel_and_close))
        request = QNetworkRequest(QUrl(self.api_url))
        request.setRawHeader(b"Accept", b"application/vnd.github+json")
        request.setRawHeader(b"User-Agent", USER_AGENT)
        request.setTransferTimeout(10000)
        self.reply = self.network.get(request)
        self.reply.finished.connect(self._checked)

    def _checked(self):
        reply, self.reply = self.reply, None
        if reply is None:
            return
        reply.deleteLater()
        if reply.error() != QNetworkReply.NetworkError.NoError:
            if self.state == "closing":
                return
            return self.show_network_error(*classify(reply), retry=self.check)
        try:
            payload = json.loads(bytes(reply.readAll()).decode("utf-8"))
            if isinstance(payload, list):
                self.release = uc.newest_release(payload, allow_prerelease=prerelease_channel(), **self.trusted)
            else:
                self.release = uc.parse_release(payload, allow_prerelease=prerelease_channel(), **self.trusted)
        except (ValueError, UnicodeDecodeError, TypeError) as exc:
            return self.show_network_error("other", f"Unexpected release data: {exc}", retry=self.check)
        if hasattr(self.window_ref, "set_update_available"):
            self.window_ref.set_update_available(self.release)
        if uc.is_newer(self.release.version, __version__):
            self.show_available()
        else:
            channel = "pre-release" if prerelease_channel() else "stable"
            self._view("current", "You're up to date",
                       f"GlassBalance v{__version__} is the newest {channel} version "
                       f"(latest published: {self.release.version}).",
                       primary=("Close", self.accept))

    def show_network_error(self, category, detail="", *, retry):
        title, text = uc.network_message(category, detail)
        self._view("error", title, text,
                   primary=("Try again", retry),
                   secondary=("Close", self.reject),
                   tertiary=("Open releases page", self._open_page))

    # ------------------------------------------------------------ 2. available
    def show_available(self):
        self.asset = uc.choose_asset(self.release, self.kind)
        checksum = self.release.asset(uc.CHECKSUM_ASSET)
        header = f"GlassBalance {self.release.version} is available"
        current = f"You have v{__version__}."
        if self.asset and checksum:
            text = (f"{current} The update ({uc.human_size(self.asset.size)}) will be downloaded, verified and "
                    "installed. Your ledger is backed up first and is never modified by the installer.")
            primary = ("Download and install", self.download)
        else:
            if self.kind in (uc.WINDOWS_PORTABLE, uc.LINUX_PORTABLE):
                why = "This is a portable copy, so it can't update itself."
            elif self.kind == uc.SOURCE:
                why = "You're running from source; update with git pull."
            elif self.kind == uc.MACOS_APP and not self.asset:
                why = "No macOS download for this Mac is published in this release."
            else:
                why = "This release doesn't include a verified installer for your system."
            text = f"{current} {why} Download it from the release page."
            primary = ("Open release page", lambda: (self._open_page(), self.accept()))
        self._view("available", header, text, notes=self.release.notes,
                   primary=primary, secondary=("Later", self.reject),
                   tertiary=("Skip this version", self._skip))

    def _skip(self):
        self.settings.setValue(SKIP_KEY, self.release.version)
        if hasattr(self.window_ref, "set_update_available"):
            self.window_ref.set_update_available(None)
        self.reject()

    # ------------------------------------------------------------ 3. download
    def download(self):
        self.checksums = None
        self._fetch_checksums()

    def _fetch_checksums(self):
        self._view("downloading", f"Downloading {self.release.version}", "Fetching checksums…",
                   progress="busy", secondary=("Cancel", self._cancel_download))
        request = QNetworkRequest(QUrl(self.release.asset(uc.CHECKSUM_ASSET).url))
        request.setRawHeader(b"User-Agent", USER_AGENT)
        request.setTransferTimeout(20000)
        self.reply = self.network.get(request)
        self.reply.finished.connect(self._checksums_done)

    def _checksums_done(self):
        reply, self.reply = self.reply, None
        if reply is None:
            return
        reply.deleteLater()
        if reply.error() != QNetworkReply.NetworkError.NoError:
            if self.state == "cancelled":
                return
            return self.show_network_error(*classify(reply), retry=self.download)
        self.checksums = uc.parse_checksums(bytes(reply.readAll()).decode("utf-8", "replace"))
        if self.asset.name not in self.checksums:
            return self._fail("No checksum for this installer",
                              "The release doesn't list a checksum for the installer, so it won't be run. "
                              "You can download it manually from the release page.")
        folder = download_dir()
        for old in folder.glob("*"):
            if old.is_file():
                old.unlink(missing_ok=True)
        self.installer_path = folder / self.asset.name
        self.part_path = folder / (self.asset.name + ".part")
        self.file = open(self.part_path, "wb")
        request = QNetworkRequest(QUrl(self.asset.url))
        request.setRawHeader(b"User-Agent", USER_AGENT)
        request.setTransferTimeout(30000)   # aborts after 30 s without data, not 30 s total
        self.reply = self.network.get(request)
        self.reply.readyRead.connect(self._write_chunk)
        self.reply.downloadProgress.connect(self._progress)
        self.reply.finished.connect(self._downloaded)
        self._view("downloading", f"Downloading {self.release.version}", self.asset.name, progress=0.0,
                   detail=f"0 B of {uc.human_size(self.asset.size)}", secondary=("Cancel", self._cancel_download))

    def _write_chunk(self):
        if self.reply is not None and self.file is not None:
            self.file.write(bytes(self.reply.readAll()))

    def _progress(self, received, total):
        total = total if total > 0 else self.asset.size
        self.progress.setValue(int(1000 * received / total) if total else 0)
        self.detail.setText(f"{uc.human_size(received)} of {uc.human_size(total)}")

    def _downloaded(self):
        reply, self.reply = self.reply, None
        if reply is None:
            return
        if self.state != "cancelled" and reply.isOpen():
            self._write_chunk_from(reply)
        if self.file:
            self.file.close()
            self.file = None
        reply.deleteLater()
        if self.state == "cancelled":
            self._discard_download()
            return
        if reply.error() != QNetworkReply.NetworkError.NoError:
            self._discard_download()
            return self.show_network_error(*classify(reply), retry=self.download)
        self._view("verifying", "Verifying download…", "Checking size and SHA-256 checksum.", progress="busy")
        QApplication.processEvents()
        try:
            uc.verify_download(self.part_path, self.asset, self.checksums)
        except (ValueError, OSError) as exc:
            self._discard_download()
            return self._fail("Download failed verification", str(exc), retry=True)
        self.part_path.replace(self.installer_path)
        if self.kind == uc.LINUX_DEB:
            self.installer_path.chmod(0o644)  # readable by the root-run installer
        self.show_ready()

    def _write_chunk_from(self, reply):
        if self.file is not None:
            data = bytes(reply.readAll())
            if data:
                self.file.write(data)

    def _discard_download(self):
        if self.file:
            self.file.close()
            self.file = None
        if self.part_path:
            self.part_path.unlink(missing_ok=True)

    def _cancel_download(self):
        self.state = "cancelled"
        if self.reply is not None:
            self.reply.abort()
        self._discard_download()
        self.show_available()

    def _cancel_and_close(self):
        self.state = "closing"
        if self.reply is not None:
            self.reply.abort()
        self.reject()

    def _fail(self, title, text, retry=False):
        self._view("error", title, text,
                   primary=("Try again", self.download) if retry else ("Close", self.reject),
                   secondary=("Close", self.reject) if retry else None,
                   tertiary=("Open release page", self._open_page))

    # ------------------------------------------------------------ 4. install
    def show_ready(self):
        if self.kind == uc.MACOS_APP:
            text = ("The disk image will open. Drag GlassBalance onto Applications and choose Replace, "
                    "then open GlassBalance again. Your ledger is stored separately and is not affected.")
            primary = ("Open disk image and quit", self.install)
        elif self.kind == uc.LINUX_DEB:
            text = ("Ubuntu will ask for your password to install the update. GlassBalance then restarts "
                    "automatically.")
            primary = ("Install and restart", self.install)
        else:
            text = "GlassBalance will close, install the update and restart automatically."
            primary = ("Install and restart", self.install)
        self._view("ready", f"{self.release.version} is ready to install", text,
                   detail=f"Verified ✓  {self.asset.name}", primary=primary, secondary=("Later", self.reject))

    def _safety_backup(self) -> Path:
        db = self.window_ref.db
        folder = Path(self.window_ref.backup_dir())
        target = folder / f"before-update-to-{self.release.version}-{datetime.now():%Y%m%d-%H%M%S}.sqlite"
        db.backup_to(target)
        return target

    def install(self):
        try:
            backup = self._safety_backup()
        except Exception as exc:
            return self._fail("Couldn't back up your ledger",
                              f"The update was not installed because the safety backup failed:\n{exc}")
        self.detail.setText(f"Safety backup: {backup}")
        if self.kind == uc.WINDOWS_INSTALLER:
            ok = QProcess.startDetached(str(self.installer_path),
                                        ["/SILENT", "/SUPPRESSMSGBOXES", "/NORESTART", "/CLOSEAPPLICATIONS"])
            if not ok:
                return self._fail("Couldn't start the installer",
                                  f"Run it manually:\n{self.installer_path}")
            self._quit_app()
        elif self.kind == uc.LINUX_DEB:
            self._install_deb()
        elif self.kind == uc.MACOS_APP:
            QDesktopServices.openUrl(QUrl.fromLocalFile(str(self.installer_path)))
            self._quit_app()

    def _install_deb(self):
        if shutil.which("pkexec") is None:
            return self._manual_deb("pkexec isn't available on this system.")
        self._view("installing", "Installing update…", "Enter your password in the system dialog.",
                   progress="busy", detail=self.detail.text())
        self.process = QProcess(self)
        self.process.finished.connect(self._deb_finished)
        self.process.errorOccurred.connect(lambda _e: self._manual_deb("The installer could not be started."))
        self.process.start("pkexec", ["dpkg", "-i", str(self.installer_path)])

    def _deb_finished(self, code, _status):
        output = bytes(self.process.readAllStandardError()).decode("utf-8", "replace").strip()
        if code == 0:
            self._view("restarting", "Update installed", "Restarting GlassBalance…", progress="busy")
            QProcess.startDetached("sh", ["-c", f"sleep 1; exec {uc.DEB_PREFIX}/GlassBalance"])
            QTimer.singleShot(300, self._quit_app)
        elif code in (126, 127):
            self._view("ready", "Installation cancelled",
                       "The password prompt was dismissed or authentication failed. Nothing was changed.",
                       primary=("Try again", self.install), secondary=("Close", self.reject))
        else:
            self._manual_deb(f"dpkg reported an error (exit code {code}).\n{output[-600:]}")

    def _manual_deb(self, reason):
        command = f"sudo apt install '{self.installer_path}'"
        self._view("error", "Install the update manually", f"{reason}\n\nRun this in a terminal:\n{command}",
                   primary=("Copy command", lambda: QGuiApplication.clipboard().setText(command)),
                   secondary=("Close", self.reject))

    def _quit_app(self):
        self.state = "quitting"
        self.accept()
        self.window_ref.close()
        QApplication.quit()

    def reject(self):
        if self.state in ("downloading", "installing"):
            if self.state == "installing":
                return  # don't abandon a running installer
            self._cancel_download()
        if self.reply is not None:
            self.state = "closing"
            self.reply.abort()
        super().reject()
