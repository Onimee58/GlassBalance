"""Qt 6 desktop interface for GlassBalance.

Pure QWidget interface (no browser/web view). Transparent panels over a subtle
painted gradient make a restrained glass-inspired layout on Windows and Linux.
"""
from __future__ import annotations

import sys
from datetime import date, datetime
from pathlib import Path

from PySide6.QtCore import QDate, QSettings, Qt, QStandardPaths
from PySide6.QtGui import QColor, QFont, QIcon, QLinearGradient, QPainter, QPen, QRadialGradient, QPixmap
from PySide6.QtWidgets import (
    QApplication, QAbstractItemView, QComboBox, QDateEdit, QDialog,
    QDialogButtonBox, QFileDialog, QFormLayout, QFrame, QGridLayout,
    QHBoxLayout, QHeaderView, QLabel, QLineEdit, QMainWindow, QMessageBox,
    QPushButton, QSizePolicy, QTabWidget, QTableWidget, QTableWidgetItem,
    QVBoxLayout, QWidget, QStackedWidget, QGraphicsDropShadowEffect, QInputDialog, QScrollArea,
)

from . import __version__
from .database import Entry, Ledger
from .email_backup import decrypt_snapshot, download_latest_backup, send_backup
from .importer import load_import
from .money import as_mills, display_money, mills_as_decimal
from . import unbalanced


STYLE = """
QWidget { color: #ecf2fa; font-family: "Inter", "Segoe UI", "Noto Sans", sans-serif; font-size: 13px; }
QScrollArea#sidebarScroll { background-color: #091221; border: none; }
QWidget#sidebarViewport { background-color: #091221; }
QWidget#sidebarContent { background-color: #091221; }
QFrame#sidebar { background-color: #091221; border: 1px solid rgba(143, 177, 208, 27); border-radius: 20px; }
QFrame#glass { background-color: rgba(18, 32, 51, 222); border: 1px solid rgba(152, 190, 223, 43); border-radius: 20px; }
QFrame#stat { background-color: rgba(18, 32, 51, 218); border: 1px solid rgba(152, 190, 223, 43); border-radius: 18px; }
QFrame#hero { background-color: rgba(22, 44, 64, 230); border: 1px solid rgba(119, 207, 203, 72); border-radius: 22px; }
QLabel#brand { color: #fbfdff; font-size: 18px; font-weight: 800; }
QLabel#title { color: #fafcff; font-size: 28px; font-weight: 750; }
QLabel#muted { color: #a4b8cd; font-size: 12px; }
QLabel#section { color: #fafcff; font-size: 17px; font-weight: 740; }
QLabel#statTitle { color: #9fb5c8; font-size: 11px; font-weight: 700; }
QLabel#value { color: #fbfdff; font-size: 37px; font-weight: 800; }
QLabel#valueIn { color: #a2ebd3; font-size: 24px; font-weight: 760; }
QLabel#valueOut { color: #ffbabf; font-size: 24px; font-weight: 760; }
QLabel#overline { color: #78dace; font-size: 11px; font-weight: 750; }
QPushButton { background-color: rgba(96, 132, 166, 30); color: #e8f2fc; border: 1px solid rgba(162, 194, 220, 44); border-radius: 11px; padding: 10px 14px; font-weight: 650; min-height: 19px; text-align: center; }
QPushButton:hover { background-color: rgba(100, 155, 182, 65); border-color: rgba(140, 223, 215, 90); }
QPushButton:pressed { background-color: rgba(112, 150, 190, 92); }
QPushButton:disabled { color: #687f94; border-color: rgba(100, 114, 136, 24); }
QPushButton#nav { text-align: left; padding: 12px 17px; background: transparent; border: 1px solid transparent; }
QPushButton#nav:hover { background: rgba(111, 161, 189, 35); }
QPushButton#navActive { text-align: left; padding: 12px 17px; background-color: rgba(68, 169, 164, 37); border: 1px solid rgba(105, 202, 197, 72); color: #b3fff2; }
QPushButton#primary { background-color: #81e0ce; color: #082a32; border: 1px solid #a0f8e3; font-weight: 800; }
QPushButton#primary:hover { background-color: #a8f3e3; }
QPushButton#danger { color: #ffbec4; }
QPushButton#danger:hover { background-color: rgba(180, 60, 70, 70); }
QLineEdit, QComboBox, QDateEdit { background-color: rgba(10, 21, 37, 188); color: #edf7ff; border: 1px solid #344a61; border-radius: 10px; padding: 9px 11px; min-height: 20px; selection-background-color: #167e87; }
QLineEdit:focus, QComboBox:focus, QDateEdit:focus { border: 1px solid #79ddd3; }
QComboBox::drop-down, QDateEdit::drop-down { border: none; width: 22px; }
QComboBox QAbstractItemView { color: #f3f6fc; background: #1b2a3e; selection-background-color: #2d606b; border: 1px solid #526479; }
QTabWidget::pane { background: transparent; border: none; }
QTabBar::tab { color: #9fb1c8; background: transparent; padding: 12px 20px; border: none; border-bottom: 2px solid transparent; font-weight: 700; }
QTabBar::tab:selected { color: #a3eee2; border-bottom: 2px solid #81e0ce; }
QTabBar::tab:hover { color: white; }
QTableWidget { background: transparent; alternate-background-color: rgba(90, 140, 175, 9); color: #edf3f9; border: none; gridline-color: transparent; selection-background-color: rgba(70, 145, 158, 76); selection-color: white; outline: none; }
QTableWidget::item { padding: 7px 8px; border-bottom: 1px solid rgba(120, 160, 190, 16); }
QHeaderView::section { color: #a0b6c8; background: rgba(23, 42, 60, 190); border: none; padding: 11px; font-weight: 700; }
QTableCornerButton::section { background: transparent; border: none; }
QScrollBar:vertical { background: rgba(22, 37, 53, 95); width: 11px; }
QScrollBar::handle:vertical { background: #536b80; border-radius: 5px; min-height: 30px; }
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }
QScrollBar:horizontal { height: 10px; background: rgba(22, 37, 53, 95); }
QScrollBar::handle:horizontal { background: #536b80; border-radius: 4px; min-width: 30px; }
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal { width: 0; }
QDialog { background-color: #17283d; }
QLabel { background: transparent; }
QStatusBar { color: #94acbe; background: transparent; }
"""


class GradientCanvas(QWidget):
    """Only the main canvas is painted; cards use Qt semi-transparent colors."""
    def paintEvent(self, event):
        p=QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        background=QLinearGradient(0,0,self.width(),self.height())
        background.setColorAt(0,QColor("#101a2a"))
        background.setColorAt(0.5,QColor("#15273a"))
        background.setColorAt(1,QColor("#0f1a29"))
        p.fillRect(self.rect(),background)
        for x,y,r,rgba in ((self.width()*0.76,64,300,(35,123,139,40)),
                           (self.width()*0.10,self.height()*0.76,310,(84,94,156,28))):
            g=QRadialGradient(x,y,r)
            g.setColorAt(0,QColor(*rgba))
            g.setColorAt(1,QColor(0,0,0,0))
            p.setPen(Qt.PenStyle.NoPen)
            p.setBrush(g)
            p.drawEllipse(int(x-r),int(y-r),int(r*2),int(r*2))
        p.end()


class BalanceChart(QWidget):
    """Native lightweight balance plot; no web runtime or external plotting dependency."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.points=[]
        self.setMinimumHeight(115)
        self.setAccessibleName("Balance trend across the last 90 transactions")

    def set_entries(self, entries):
        self.points=[entry.running_mills for entry in entries[-90:]]
        self.update()

    def paintEvent(self, event):
        painter=QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        width,height=self.width(),self.height()
        if width<10 or height<10:
            return
        painter.setPen(QPen(QColor(130,170,184,34),1))
        for f in (0.2,0.5,0.8):
            y=round(height*f)
            painter.drawLine(0,y,width,y)
        vals=self.points
        if not vals:
            painter.setPen(QColor('#95b2bf'))
            painter.drawText(self.rect(),Qt.AlignmentFlag.AlignCenter,'Your balance trend will appear here')
            return
        if len(vals)==1:
            vals=[vals[0],vals[0]]
        lo,hi=min(vals),max(vals)
        spread=max(hi-lo,1)
        from PySide6.QtCore import QPointF
        from PySide6.QtGui import QPainterPath
        coords=[QPointF(5+(width-10)*i/(len(vals)-1), 10+(height-25)*(hi-v)/spread)
                for i,v in enumerate(vals)]
        trace=QPainterPath(coords[0])
        for point in coords[1:]:
            trace.lineTo(point)
        filled=QPainterPath(trace)
        filled.lineTo(coords[-1].x(),height)
        filled.lineTo(coords[0].x(),height)
        filled.closeSubpath()
        gradient=QLinearGradient(0,0,0,height)
        gradient.setColorAt(0,QColor(92,217,193,85))
        gradient.setColorAt(1,QColor(92,217,193,0))
        painter.fillPath(filled,gradient)
        painter.setPen(QPen(QColor('#8ae9d4'),2.6))
        painter.drawPath(trace)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor('#d7fff4'))
        painter.drawEllipse(coords[-1],4,4)
        painter.end()


def label(text: str, obj: str = "", wrap: bool = False) -> QLabel:
    item=QLabel(text)
    if obj:
        item.setObjectName(obj)
    item.setWordWrap(wrap)
    return item


def panel(object_name: str="glass") -> QFrame:
    box=QFrame()
    box.setObjectName(object_name)
    return box


def button(text: str, kind: str = "") -> QPushButton:
    btn=QPushButton(text)
    if kind:
        btn.setObjectName(kind)
    btn.setCursor(Qt.CursorShape.PointingHandCursor)
    return btn


def message(parent, title: str, content: str) -> None:
    QMessageBox.information(parent,title,content)


def error(parent, title: str, exc: Exception) -> None:
    QMessageBox.critical(parent,title,str(exc))


def confirm(parent,title: str,text: str) -> bool:
    return QMessageBox.question(parent,title,text,
           QMessageBox.StandardButton.Yes|QMessageBox.StandardButton.No,
           QMessageBox.StandardButton.No)==QMessageBox.StandardButton.Yes


class TransactionDialog(QDialog):
    def __init__(self,parent=None,entry: Entry|None=None):
        super().__init__(parent)
        self.setWindowTitle("Edit transaction" if entry else "New transaction")
        self.setMinimumWidth(410)
        outer=QVBoxLayout(self)
        outer.setContentsMargins(23,23,23,21)
        outer.setSpacing(16)
        outer.addWidget(label("Edit transaction" if entry else "Record a transaction","section"))
        outer.addWidget(label("Amounts with a minus sign reduce your balance.","muted"))
        form=QFormLayout()
        form.setLabelAlignment(Qt.AlignmentFlag.AlignLeft)
        form.setSpacing(13)
        self.name=QLineEdit(entry.description if entry else "")
        self.name.setPlaceholderText("e.g. Groceries, September salary, rent")
        self.amount=QLineEdit(mills_as_decimal(entry.mills) if entry else "")
        self.amount.setPlaceholderText("e.g. -35.50 or 2100.00")
        self.date=QDateEdit()
        self.date.setDisplayFormat("MMM d, yyyy")
        self.date.setCalendarPopup(True)
        self.date.setDate(QDate.fromString(entry.date,Qt.DateFormat.ISODate) if entry else QDate.currentDate())
        self.status=QComboBox()
        self.status.addItems(["Confirmed", "Estimated"])
        self.status.setCurrentText(entry.date_status.title() if entry else "Confirmed")
        form.addRow("Description",self.name)
        form.addRow("Signed amount",self.amount)
        form.addRow("Date",self.date)
        form.addRow("Date accuracy",self.status)
        outer.addLayout(form)
        outer.addWidget(label("Imported historical dates are estimated until you confirm them.","muted",True))
        actions=QDialogButtonBox(QDialogButtonBox.StandardButton.Save|QDialogButtonBox.StandardButton.Cancel)
        actions.accepted.connect(self.validate)
        actions.rejected.connect(self.reject)
        outer.addWidget(actions)
        # A manual date adjustment confirms it automatically.
        self.date.dateChanged.connect(lambda _:self.status.setCurrentText("Confirmed"))
        self.name.setFocus()

    def validate(self):
        try:
            name=self.name.text().strip()
            if not name:
                raise ValueError("Enter a description.")
            if len(name)>300:
                raise ValueError("Description cannot exceed 300 characters.")
            if not self.amount.text().strip():
                raise ValueError("Enter the signed amount.")
            self.checked_mills=as_mills(self.amount.text())
            self.checked_date=self.date.date().toString(Qt.DateFormat.ISODate)
            self.checked_status=self.status.currentText().lower()
            self.checked_name=name
        except ValueError as exc:
            error(self,"Check transaction",exc)
            return
        self.accept()


class OpeningDialog(QDialog):
    def __init__(self,parent,old_mills: int,old_date: str,old_status: str):
        super().__init__(parent)
        self.setWindowTitle("Opening balance")
        self.setMinimumWidth(390)
        layout=QVBoxLayout(self)
        layout.setContentsMargins(22,22,22,22)
        layout.addWidget(label("Starting balance","section"))
        layout.addWidget(label("An opening balance is not income. It is included once in all running balances.","muted",True))
        form=QFormLayout()
        self.amount=QLineEdit(mills_as_decimal(old_mills))
        self.date=QDateEdit()
        self.date.setCalendarPopup(True)
        self.date.setDisplayFormat("MMM d, yyyy")
        self.date.setDate(QDate.fromString(old_date,Qt.DateFormat.ISODate))
        self.status=QComboBox()
        self.status.addItems(["Confirmed","Estimated"])
        self.status.setCurrentText(old_status.title())
        form.addRow("Starting amount",self.amount)
        form.addRow("Effective date",self.date)
        form.addRow("Date accuracy",self.status)
        layout.addLayout(form)
        actions=QDialogButtonBox(QDialogButtonBox.StandardButton.Save|QDialogButtonBox.StandardButton.Cancel)
        actions.accepted.connect(self.validate)
        actions.rejected.connect(self.reject)
        layout.addWidget(actions)

    def validate(self):
        try:
            self.checked_mills=as_mills(self.amount.text())
            self.checked_date=self.date.date().toString(Qt.DateFormat.ISODate)
            self.checked_status=self.status.currentText().lower()
        except ValueError as exc:
            error(self,"Opening balance",exc)
            return
        self.accept()


class EmailDialog(QDialog):
    """Optional manual encrypted snapshot transfer. Never persists passwords."""
    def __init__(self,parent,db: Ledger):
        super().__init__(parent)
        self.db=db
        self.setWindowTitle("Encrypted email backups")
        self.setMinimumWidth(530)
        self.settings=QSettings("GlassBalance","Desktop")
        box=QVBoxLayout(self)
        box.setContentsMargins(25,24,25,22)
        box.setSpacing(14)
        box.addWidget(label("Email backup & restore","section"))
        box.addWidget(label("Send an encrypted snapshot to yourself or restore the newest one. This is manual backup transfer, not automatic two-way sync.","muted",True))
        form=QFormLayout()
        form.setSpacing(9)
        self.address=QLineEdit(str(self.settings.value("email/address","")))
        self.address.setPlaceholderText("you@example.com")
        self.smtp=QLineEdit(str(self.settings.value("email/smtp","smtp.gmail.com")))
        self.imap=QLineEdit(str(self.settings.value("email/imap","imap.gmail.com")))
        self.smtp_port=QLineEdit(str(self.settings.value("email/smtp_port","465")))
        self.imap_port=QLineEdit(str(self.settings.value("email/imap_port","993")))
        self.app_password=QLineEdit()
        self.app_password.setEchoMode(QLineEdit.EchoMode.Password)
        self.app_password.setPlaceholderText("Provider-specific email app password")
        self.passphrase=QLineEdit()
        self.passphrase.setEchoMode(QLineEdit.EchoMode.Password)
        self.passphrase.setPlaceholderText("A different 12+ character encryption passphrase")
        for k,field in (("Email address",self.address),("SMTP host",self.smtp),
                        ("SMTP port",self.smtp_port),("IMAP host",self.imap),
                        ("IMAP port",self.imap_port),("Email app password",self.app_password),
                        ("Encryption passphrase",self.passphrase)):
            form.addRow(k,field)
        box.addLayout(form)
        box.addWidget(label("Keep your encryption passphrase somewhere safe. It is never stored by the app or included in the email. Losing it means old backups cannot be decrypted.","muted",True))
        actions=QHBoxLayout()
        send_btn=button("Send encrypted backup","primary")
        restore_btn=button("Restore newest email backup")
        close_btn=button("Close")
        send_btn.clicked.connect(self.send)
        restore_btn.clicked.connect(self.restore)
        close_btn.clicked.connect(self.reject)
        for action in (send_btn,restore_btn,close_btn):
            actions.addWidget(action)
        box.addLayout(actions)

    def _config(self):
        addr=self.address.text().strip()
        pwd=self.app_password.text()
        phrase=self.passphrase.text()
        if len(phrase)<12:
            raise ValueError("Please use an encryption passphrase of 12 or more characters.")
        smtp_port=int(self.smtp_port.text())
        imap_port=int(self.imap_port.text())
        if not (1<=smtp_port<=65535 and 1<=imap_port<=65535):
            raise ValueError("Email ports must be between 1 and 65535.")
        self.settings.setValue("email/address",addr)
        self.settings.setValue("email/smtp",self.smtp.text().strip())
        self.settings.setValue("email/imap",self.imap.text().strip())
        self.settings.setValue("email/smtp_port",smtp_port)
        self.settings.setValue("email/imap_port",imap_port)
        return addr,pwd,phrase,smtp_port,imap_port

    def send(self):
        try:
            addr,pwd,phrase,smtp_port,_=self._config()
            QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)
            try:
                filename=send_backup(addr,pwd,self.smtp.text().strip(),phrase,
                                     self.db.backup_bytes(),smtp_port)
            finally:
                QApplication.restoreOverrideCursor()
            message(self,"Backup sent",f"Encrypted backup sent to {addr}.\n\nAttachment: {filename}")
        except Exception as exc:
            error(self,"Email backup failed",exc)

    def restore(self):
        if not confirm(self,"Replace local ledger?",
           "Restoring an email snapshot REPLACES the local database, including any transactions added since the snapshot.\n\n"
           "A separate local safety backup will be saved first. Continue?"):
            return
        try:
            addr,pwd,phrase,_,imap_port=self._config()
            QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)
            try:
                encrypted=download_latest_backup(addr,pwd,self.imap.text().strip(),imap_port)
                plaintext=decrypt_snapshot(encrypted,phrase)
            finally:
                QApplication.restoreOverrideCursor()
            # Save current data independently before performing a destructive restore.
            safety=backup_folder()/f"before-email-restore-{datetime.now().strftime('%Y%m%d-%H%M%S')}.sqlite"
            self.db.backup_to(safety)
            self.db.restore_bytes(plaintext)
            message(self,"Email restore complete",f"Your ledger was restored.\n\nLocal safety copy:\n{safety}")
            self.accept()
        except Exception as exc:
            error(self,"Email restore failed",exc)


def data_folder() -> Path:
    root=QStandardPaths.writableLocation(QStandardPaths.StandardLocation.AppDataLocation)
    if not root:
        root=str(Path.home()/".glassbalance")
    path=Path(root)
    path.mkdir(parents=True,exist_ok=True)
    return path


def backup_folder() -> Path:
    root=data_folder()/"backups"
    root.mkdir(parents=True,exist_ok=True)
    return root


def app_icon() -> QIcon:
    """Resolve bundled icon in both source and PyInstaller installations."""
    base=Path(getattr(sys,"_MEIPASS",Path(__file__).resolve().parent.parent))
    path=base/"glassbalance"/"assets"/"glassbalance_icon.png"
    return QIcon(str(path)) if path.is_file() else QIcon()


class Window(QMainWindow):
    def __init__(self, db_path: str | Path | None=None):
        super().__init__()
        self.setWindowTitle(f"GlassBalance  ·  Personal ledger  ·  v{__version__}")
        self.setWindowIcon(app_icon())
        self.resize(1350,860)
        self.setMinimumSize(1010,710)
        self.db=Ledger(db_path or (data_folder()/"balance.sqlite"))
        unbalanced.install(self.db)
        self.setStyleSheet(STYLE)
        self.canvas=GradientCanvas()
        self.setCentralWidget(self.canvas)
        self.build()
        self.refresh()
        self.statusBar().showMessage(f"Offline • Stored only on this computer • {self.db.path or 'Memory'}")

    def build(self):
        root=QHBoxLayout(self.canvas)
        root.setContentsMargins(20,20,20,16)
        root.setSpacing(18)

        left=panel("sidebar")
        left.setFixedWidth(213)
        sidebar_shell=QVBoxLayout(left)
        sidebar_shell.setContentsMargins(0,0,0,0)
        sidebar_shell.setSpacing(0)
        side_scroll=QScrollArea(left)
        side_scroll.setObjectName("sidebarScroll")
        side_scroll.setFrameShape(QFrame.Shape.NoFrame)
        side_scroll.viewport().setObjectName("sidebarViewport")
        side_scroll.viewport().setStyleSheet("background-color: #091221;")
        side_scroll.setWidgetResizable(True)
        side_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        side_content=QWidget()
        side_content.setObjectName("sidebarContent")
        side_content.setStyleSheet("background-color: #091221;")
        sidebar=QVBoxLayout(side_content)
        sidebar.setContentsMargins(14,18,14,14)
        sidebar.setSpacing(6)
        side_scroll.setWidget(side_content)
        sidebar_shell.addWidget(side_scroll)
        brand_row=QHBoxLayout()
        mark=QLabel()
        mark.setFixedSize(36,36)
        mark.setPixmap(app_icon().pixmap(34,34))
        brand_row.addWidget(mark)
        brand_row.addWidget(label("GlassBalance","brand"),1)
        sidebar.addLayout(brand_row)
        sidebar.addWidget(label("YOUR MONEY, IN FOCUS","muted"))
        sidebar.addSpacing(12)
        sidebar.addWidget(label("WORKSPACE","overline"))
        self.nav_overview=button("▦    Overview","navActive")
        self.nav_activity=button("≡    Transactions","nav")
        self.nav_monthly=button("▤    Monthly history","nav")
        self.nav_balance_search=button("⌕    Balance Search","nav")
        self.nav_unbalanced=button("⇄    Unbalanced","nav")
        for control in (self.nav_overview,self.nav_activity,self.nav_monthly,self.nav_balance_search,self.nav_unbalanced):
            sidebar.addWidget(control)
        sidebar.addSpacing(7)
        sidebar.addWidget(label("TOOLS","overline"))
        self.side_import=button("↳    Import Excel / CSV","nav")
        self.side_export=button("⇧    Export ledger","nav")
        self.side_backup=button("▣    Save backup","nav")
        self.side_restore=button("↶    Restore backup","nav")
        self.side_email=button("✉    Encrypted email","nav")
        self.side_opening=button("◉    Opening balance","nav")
        self.side_about=button("ⓘ    About GlassBalance","nav")
        for control in (self.side_import,self.side_export,self.side_backup,
                        self.side_restore,self.side_email,self.side_opening,self.side_about):
            sidebar.addWidget(control)
        sidebar.addStretch()
        sidebar.addWidget(label("●  LOCAL & OFFLINE","overline"))
        sidebar.addWidget(label("Your ledger stays on this device unless you choose to share a backup.","muted",True))
        sidebar.addSpacing(6)
        sidebar.addWidget(label(f"v{__version__}  ·  ALPHA PREVIEW","muted"))
        root.addWidget(left)

        main=QWidget()
        main.setSizePolicy(QSizePolicy.Policy.Expanding,QSizePolicy.Policy.Expanding)
        root.addWidget(main,1)
        content=QVBoxLayout(main)
        content.setContentsMargins(0,5,0,0)
        content.setSpacing(15)
        header=QHBoxLayout()
        header_text=QVBoxLayout()
        header_text.setSpacing(5)
        header_text.addWidget(label("YOUR PERSONAL LEDGER  /  OVERVIEW","overline"))
        header_text.addWidget(label("Money, made clearer.","title"))
        header_text.addWidget(label("A complete picture of every transaction.","muted"))
        header.addLayout(header_text,1)
        self.side_new=button("＋  New transaction","primary")
        header.addWidget(self.side_new,alignment=Qt.AlignmentFlag.AlignVCenter)
        content.addLayout(header)

        summary_row=QHBoxLayout()
        summary_row.setSpacing(13)
        hero=panel("hero")
        hero.setMinimumHeight(208)
        hero_layout=QVBoxLayout(hero)
        hero_layout.setContentsMargins(22,18,22,17)
        hero_layout.setSpacing(4)
        hero_layout.addWidget(label("TOTAL BALANCE","statTitle"))
        self.balance_value=label("$0.00","value")
        hero_layout.addWidget(self.balance_value)
        hero_layout.addWidget(label("Opening balance + every recorded transaction","muted"))
        self.trend=BalanceChart()
        hero_layout.addWidget(self.trend,1)
        summary_row.addWidget(hero,3)
        mini=QVBoxLayout()
        mini.setSpacing(12)
        income=panel("stat")
        i_layout=QVBoxLayout(income)
        i_layout.setContentsMargins(17,15,15,14)
        i_layout.addWidget(label("INCOME  ·  THIS MONTH","statTitle"))
        self.income_value=label("$0.00","valueIn")
        i_layout.addWidget(self.income_value)
        i_layout.addWidget(label("Positive transactions","muted"))
        mini.addWidget(income)
        expense=panel("stat")
        e_layout=QVBoxLayout(expense)
        e_layout.setContentsMargins(17,15,15,14)
        e_layout.addWidget(label("EXPENSES  ·  THIS MONTH","statTitle"))
        self.expense_value=label("$0.00","valueOut")
        e_layout.addWidget(self.expense_value)
        e_layout.addWidget(label("Negative transactions","muted"))
        mini.addWidget(expense)
        summary_row.addLayout(mini,2)
        content.addLayout(summary_row)

        activity=panel()
        activity_layout=QVBoxLayout(activity)
        activity_layout.setContentsMargins(19,17,19,15)
        activity_layout.setSpacing(12)
        activity_header=QHBoxLayout()
        activity_header.addWidget(label("Ledger activity","section"))
        activity_header.addStretch()
        self.count_label=label("0 transactions","muted")
        activity_header.addWidget(self.count_label)
        activity_layout.addLayout(activity_header)
        filters=QHBoxLayout()
        filters.setSpacing(9)
        self.search=QLineEdit()
        self.search.setPlaceholderText("Search descriptions or periods…")
        self.search.setClearButtonEnabled(True)
        filters.addWidget(self.search,1)
        self.period=QComboBox()
        self.period.addItems(["All dates","This month","Previous month","Custom dates"])
        filters.addWidget(self.period)
        self.from_date=QDateEdit()
        self.from_date.setDisplayFormat("MMM d, yyyy")
        self.from_date.setCalendarPopup(True)
        self.from_date.setDate(QDate.currentDate().addMonths(-1))
        self.to_date=QDateEdit()
        self.to_date.setDisplayFormat("MMM d, yyyy")
        self.to_date.setCalendarPopup(True)
        self.to_date.setDate(QDate.currentDate())
        self.from_date.setToolTip("Filter start date (inclusive)")
        self.to_date.setToolTip("Filter end date (inclusive)")
        filters.addWidget(self.from_date)
        filters.addWidget(self.to_date)
        self.from_date.hide()
        self.to_date.hide()
        activity_layout.addLayout(filters)

        self.tabs=QTabWidget()
        self.table=QTableWidget(0,5)
        self.table.setHorizontalHeaderLabels(["DATE","DESCRIPTION","CHANGE","RUNNING BALANCE","ACCURACY"])
        self._setup_table(self.table)
        th=self.table.horizontalHeader()
        for i in (0,2,3,4):
            th.setSectionResizeMode(i,QHeaderView.ResizeMode.ResizeToContents)
        th.setSectionResizeMode(1,QHeaderView.ResizeMode.Stretch)
        self.table.setMinimumHeight(220)
        self.tabs.addTab(self.table,"Transactions")
        self.monthly=QTableWidget(0,5)
        self.monthly.setHorizontalHeaderLabels(["MONTH","INCOME","EXPENSES","NET CHANGE","END BALANCE"])
        self._setup_table(self.monthly)
        mh=self.monthly.horizontalHeader()
        for col in range(5):
            mh.setSectionResizeMode(col,QHeaderView.ResizeMode.Stretch)
        self.tabs.addTab(self.monthly,"Monthly history")
        self.balance_search_tab=QWidget()
        bs=QVBoxLayout(self.balance_search_tab)
        bs.addWidget(label("Search all transactions and see the signed net amount for any name or phrase.","muted",True))
        self.balance_query=QLineEdit()
        self.balance_query.setPlaceholderText("Try: walmart")
        self.balance_query.setClearButtonEnabled(True)
        bs.addWidget(self.balance_query)
        bs_totals=QHBoxLayout()
        self.bs_in=label("Money in: $0.00","valueIn")
        self.bs_out=label("Money out: $0.00","valueOut")
        self.bs_net=label("Net: $0.00","section")
        for widget in (self.bs_in,self.bs_out,self.bs_net): bs_totals.addWidget(widget)
        bs.addLayout(bs_totals)
        self.bs_table=QTableWidget(0,3)
        self.bs_table.setHorizontalHeaderLabels(["DATE","DESCRIPTION","AMOUNT"])
        self._setup_table(self.bs_table)
        self.bs_table.horizontalHeader().setSectionResizeMode(1,QHeaderView.ResizeMode.Stretch)
        bs.addWidget(self.bs_table,1)
        self.tabs.addTab(self.balance_search_tab,"Balance Search")
        self.unbalanced_tab=QWidget()
        ub=QVBoxLayout(self.unbalanced_tab)
        ub.addWidget(label("Loan tracking is separate from the ledger. Nothing is settled without confirmation.","muted",True))
        ub_tools=QHBoxLayout()
        self.loan_new=button("Track selected transaction as loan","primary")
        self.loan_suggest=button("Review possible refunds")
        self.loan_unlink=button("Unlink repayment")
        for b in (self.loan_new,self.loan_suggest,self.loan_unlink): ub_tools.addWidget(b)
        ub.addLayout(ub_tools)
        self.ub_summary=label("Outstanding balances","section")
        ub.addWidget(self.ub_summary)
        self.loan_table=QTableWidget(0,5)
        self.loan_table.setHorizontalHeaderLabels(["PERSON","TYPE","ORIGINAL","REPAID","OUTSTANDING"])
        self._setup_table(self.loan_table)
        self.loan_table.horizontalHeader().setSectionResizeMode(0,QHeaderView.ResizeMode.Stretch)
        ub.addWidget(self.loan_table,2)
        ub.addWidget(label("Linked repayments for selected loan · select a row to unlink a repayment","muted"))
        self.repay_table=QTableWidget(0,3)
        self.repay_table.setHorizontalHeaderLabels(["DATE","DESCRIPTION","AMOUNT"])
        self._setup_table(self.repay_table)
        self.repay_table.horizontalHeader().setSectionResizeMode(1,QHeaderView.ResizeMode.Stretch)
        ub.addWidget(self.repay_table,1)
        self.tabs.addTab(self.unbalanced_tab,"Unbalanced")
        activity_layout.addWidget(self.tabs,1)
        bottom=QHBoxLayout()
        bottom.addWidget(label("~ Estimated historical date  ·  Double-click a row to edit","muted",True),1)
        self.edit_button=button("Edit selection")
        self.delete_button=button("Delete","danger")
        for b in (self.edit_button,self.delete_button):
            b.setEnabled(False)
            bottom.addWidget(b)
        activity_layout.addLayout(bottom)
        content.addWidget(activity,1)

        self.side_new.clicked.connect(self.add_transaction)
        self.side_import.clicked.connect(self.import_file)
        self.side_export.clicked.connect(self.export_file)
        self.side_backup.clicked.connect(self.save_backup)
        self.side_restore.clicked.connect(self.restore_backup)
        self.side_email.clicked.connect(self.email_backup)
        self.side_opening.clicked.connect(self.edit_opening)
        self.side_about.clicked.connect(self.show_about)
        self.nav_overview.clicked.connect(lambda:self.navigate(0))
        self.nav_activity.clicked.connect(lambda:self.navigate(0))
        self.nav_monthly.clicked.connect(lambda:self.navigate(1))
        self.nav_balance_search.clicked.connect(lambda:self.navigate(2))
        self.nav_unbalanced.clicked.connect(lambda:self.navigate(3))
        self.balance_query.textChanged.connect(self.render_balance_search)
        self.loan_new.clicked.connect(self.register_selected_loan)
        self.loan_suggest.clicked.connect(self.review_refunds)
        self.loan_unlink.clicked.connect(self.unlink_selected_repayment)
        self.loan_table.itemSelectionChanged.connect(self.render_repayments)
        self.search.textChanged.connect(self.render_transactions)
        self.period.currentIndexChanged.connect(self.period_changed)
        self.from_date.dateChanged.connect(self.render_transactions)
        self.to_date.dateChanged.connect(self.render_transactions)
        self.table.itemSelectionChanged.connect(self.update_selection)
        self.table.cellDoubleClicked.connect(lambda *_:self.edit_transaction())
        self.edit_button.clicked.connect(self.edit_transaction)
        self.delete_button.clicked.connect(self.delete_transaction)
        self.tabs.currentChanged.connect(self.update_selection)
        self.tabs.currentChanged.connect(self._nav_feedback)

    def navigate(self, tab: int):
        self.tabs.setCurrentIndex(tab)
        if tab==0:
            self.search.setFocus()

    def _nav_feedback(self, tab: int):
        self.nav_overview.setObjectName("navActive" if tab==0 else "nav")
        self.nav_activity.setObjectName("nav" )
        self.nav_monthly.setObjectName("navActive" if tab==1 else "nav")
        self.nav_balance_search.setObjectName("navActive" if tab==2 else "nav")
        self.nav_unbalanced.setObjectName("navActive" if tab==3 else "nav")
        for control in (self.nav_overview,self.nav_activity,self.nav_monthly,self.nav_balance_search,self.nav_unbalanced):
            control.style().unpolish(control)
            control.style().polish(control)

    def render_balance_search(self):
        if not hasattr(self,"all_entries"): return
        query=self.balance_query.text().strip().casefold()
        matches=[e for e in self.all_entries if query and query in e.description.casefold()]
        pos=sum(max(e.mills,0) for e in matches)
        neg=sum(min(e.mills,0) for e in matches)
        self.bs_in.setText("Money in: " + display_money(pos))
        self.bs_out.setText("Money out: " + display_money(neg))
        self.bs_net.setText("Net: " + display_money(pos+neg))
        self.bs_table.setRowCount(len(matches))
        for i,e in enumerate(reversed(matches)):
            for c,v in enumerate((e.date,e.description,display_money(e.mills))):
                self.bs_table.setItem(i,c,QTableWidgetItem(v))

    def render_loans(self):
        loans=unbalanced.loan_rows(self.db)
        self.loan_table.setRowCount(len(loans))
        owed=sum(x.outstanding_mills for x in loans if x.direction=='lent')
        owing=sum(x.outstanding_mills for x in loans if x.direction=='borrowed')
        self.ub_summary.setText(f"Owed to you: {display_money(owed)}    ·    You owe: {display_money(owing)}")
        for i,loan in enumerate(loans):
            vals=(loan.person,loan.direction.title(),display_money(loan.principal_mills),
                  display_money(loan.repaid_mills),display_money(loan.outstanding_mills))
            for j,value in enumerate(vals):
                item=QTableWidgetItem(value)
                item.setData(Qt.ItemDataRole.UserRole,loan.id)
                self.loan_table.setItem(i,j,item)
        self.render_repayments()

    def active_loan_id(self):
        row=self.loan_table.currentRow()
        item=self.loan_table.item(row,0) if row>=0 else None
        return item.data(Qt.ItemDataRole.UserRole) if item else None

    def render_repayments(self):
        loan_id=self.active_loan_id()
        rows=unbalanced.linked_repayments(self.db,loan_id) if loan_id else []
        self.repay_table.setRowCount(len(rows))
        for i,tx in enumerate(rows):
            for j,val in enumerate((tx['tx_date'],tx['description'],display_money(tx['amount_mills']))):
                item=QTableWidgetItem(val)
                item.setData(Qt.ItemDataRole.UserRole,tx['id'])
                self.repay_table.setItem(i,j,item)

    def register_selected_loan(self):
        # A loan is registered only when the user explicitly selects its existing transaction.
        candidates=[e for e in self.all_entries if e.mills != 0]
        labels=[f"{e.date}  |  {e.description}  |  {display_money(e.mills)}  (#{e.id})" for e in reversed(candidates)]
        if not labels: return message(self,"No transactions","Add a transaction first.")
        choice,ok=QInputDialog.getItem(self,"Select original loan","Original lending / borrowing transaction:",labels,0,False)
        if not ok: return
        txid=int(choice.rsplit('(#',1)[-1][:-1]) if '(#' in choice else None
        person,ok=QInputDialog.getText(self,"Name the person","Person who lent or borrowed:")
        if not ok: return
        try:
            direction=unbalanced.register_loan(self.db,txid,person)
            self.render_loans()
            message(self,"Loan tracked",f"Recorded as {direction}. Ledger balance was not changed.")
        except Exception as exc: error(self,"Could not track loan",exc)

    def review_refunds(self):
        loan_id=self.active_loan_id()
        if loan_id is None: return message(self,"Select a loan","Select a loan to review suggested repayments.")
        options=unbalanced.suggestions(self.db,loan_id)
        if not options:
            return message(self,"No suggestions","No unreviewed matching refund or repayment descriptions found. No changes made.")
        labels=[f"{tx['tx_date']} | {tx['description']} | {display_money(tx['amount_mills'])} (#{tx['id']})" for tx in options]
        choice,ok=QInputDialog.getItem(self,"Possible repayments","Choose a transaction to review:",labels,0,False)
        if not ok: return
        txid=int(choice.rsplit('(#',1)[-1][:-1])
        choice_index=labels.index(choice)
        tx=options[choice_index]
        box=QMessageBox(self)
        box.setWindowTitle("Confirm repayment")
        box.setText(f"Link '{tx['description']}' ({display_money(tx['amount_mills'])}) as a repayment?\nThis will not change your ledger balance.")
        yes=box.addButton("Confirm repayment",QMessageBox.ButtonRole.AcceptRole)
        no=box.addButton("Not a repayment",QMessageBox.ButtonRole.DestructiveRole)
        box.addButton("Cancel",QMessageBox.ButtonRole.RejectRole)
        box.exec()
        try:
            if box.clickedButton()==yes: unbalanced.confirm_repayment(self.db,loan_id,txid)
            elif box.clickedButton()==no: unbalanced.dismiss_suggestion(self.db,loan_id,txid)
            self.render_loans()
        except Exception as exc: error(self,"Cannot link repayment",exc)

    def unlink_selected_repayment(self):
        row=self.repay_table.currentRow()
        item=self.repay_table.item(row,0) if row>=0 else None
        if not item: return message(self,"Select repayment","Select a linked repayment in the lower table first.")
        if not confirm(self,"Unlink repayment?","Remove this repayment link? The original transaction stays unchanged."): return
        unbalanced.unlink_repayment(self.db,item.data(Qt.ItemDataRole.UserRole))
        self.render_loans()

    def show_about(self):
        from PySide6.QtGui import QPixmap

        dlg=QDialog(self)
        dlg.setWindowTitle("About GlassBalance")
        dlg.setWindowIcon(app_icon())
        layout=QVBoxLayout(dlg)
        layout.setSpacing(12)
        avatar=QLabel()
        avatar.setFixedHeight(106)
        avatar.setAlignment(Qt.AlignmentFlag.AlignCenter)
        asset_root=Path(getattr(sys,"_MEIPASS",Path(__file__).resolve().parent.parent))
        bundled=asset_root/"glassbalance"/"assets"/"onimee58_avatar.png"
        custom=data_folder()/"maintainer_avatar.png"

        def display_avatar():
            for path in (custom,bundled):
                if path.is_file():
                    pix=QPixmap(str(path))
                    if not pix.isNull():
                        avatar.setPixmap(pix.scaled(96,96,Qt.AspectRatioMode.KeepAspectRatio,Qt.TransformationMode.SmoothTransformation))
                        return
            avatar.setText("◈")
            avatar.setStyleSheet("font-size: 38px; color: #81e0ce;")

        def choose_avatar():
            path,_=QFileDialog.getOpenFileName(dlg,"Choose your GitHub profile picture",str(Path.home()),"Images (*.png *.jpg *.jpeg *.webp)")
            if not path:
                return
            pix=QPixmap(path)
            if pix.isNull():
                return message(dlg,"Invalid picture","Please select a valid PNG, JPEG, or WebP image.")
            image=pix.scaled(128,128,Qt.AspectRatioMode.KeepAspectRatio,Qt.TransformationMode.SmoothTransformation)
            if not image.save(str(custom),"PNG"):
                return message(dlg,"Picture not saved","Could not save your profile image.")
            display_avatar()

        display_avatar()
        layout.addWidget(avatar)
        photo_button=button("Change profile picture (local)")
        photo_button.clicked.connect(choose_avatar)
        layout.addWidget(photo_button)
        logo=QLabel()
        logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        logo.setPixmap(app_icon().pixmap(54,54))
        layout.addWidget(logo)
        title=label(f"GlassBalance v{__version__}","section")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        info=label("Created and maintained by @Onimee58\nFounding maintainer · October 2026\nMIT License", "muted",True)
        info.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(info)
        link=QLabel('<a href="https://github.com/Onimee58/GlassBalance" style="color:#81e0ce;">GitHub project ↗</a>')
        link.setOpenExternalLinks(True)
        link.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(link)
        layout.addWidget(label("Alpha software: keep a backup before upgrading.","muted",True))
        close=button("Close")
        close.clicked.connect(dlg.accept)
        layout.addWidget(close)
        dlg.resize(395,420)
        dlg.exec()

    def _setup_table(self,table):
        table.setShowGrid(False)
        table.setAlternatingRowColors(True)
        table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        table.verticalHeader().hide()
        table.setSortingEnabled(False)
        table.setWordWrap(False)
        table.verticalHeader().setDefaultSectionSize(38)

    def _stat(self,container,title,value,key,subtitle):
        card=panel("stat")
        col=QVBoxLayout(card)
        col.setContentsMargins(18,17,15,16)
        col.setSpacing(8)
        col.addWidget(label(title,"statTitle"))
        current=label(value,key)
        current.setMinimumWidth(150)
        col.addWidget(current)
        col.addWidget(label(subtitle,"muted"))
        container.addWidget(card,1)
        return current

    def refresh(self):
        self.all_entries=self.db.entries()
        self.balance_value.setText(display_money(self.db.balance()))
        self.trend.set_entries(self.all_entries)
        month=date.today().strftime("%Y-%m")
        in_month=sum(max(r.mills,0) for r in self.all_entries if r.date.startswith(month))
        out_month=sum(max(-r.mills,0) for r in self.all_entries if r.date.startswith(month))
        self.income_value.setText(display_money(in_month))
        self.expense_value.setText(display_money(out_month))
        self.render_transactions()
        self.render_monthly()
        self.render_balance_search()
        self.render_loans()

    def period_changed(self):
        custom=self.period.currentText()=="Custom dates"
        self.from_date.setVisible(custom)
        self.to_date.setVisible(custom)
        self.render_transactions()

    def _current_filter(self,r: Entry) -> bool:
        term=self.search.text().strip().lower()
        if term and term not in r.description.lower() and term not in r.source_period.lower():
            return False
        choice=self.period.currentText()
        if choice=="This month":
            return r.date.startswith(date.today().strftime("%Y-%m"))
        if choice=="Previous month":
            first=date.today().replace(day=1)
            previous=(first.replace(day=1).toordinal()-1)
            from datetime import date as date_class
            month=date_class.fromordinal(previous).strftime("%Y-%m")
            return r.date.startswith(month)
        if choice=="Custom dates":
            start=self.from_date.date().toString(Qt.DateFormat.ISODate)
            end=self.to_date.date().toString(Qt.DateFormat.ISODate)
            return start<=r.date<=end
        return True

    def render_transactions(self):
        if not hasattr(self,"all_entries"):
            return
        results=[r for r in self.all_entries if self._current_filter(r)]
        self.table.setUpdatesEnabled(False)
        try:
            self.table.clearSelection()
            self.table.setRowCount(len(results))
            for row,r in enumerate(reversed(results)):
                dt=f"{r.date}{' ~' if r.date_status=='estimated' else ''}"
                cells=[dt,r.description,display_money(r.mills),display_money(r.running_mills),r.date_status.title()]
                for col,value in enumerate(cells):
                    item=QTableWidgetItem(value)
                    item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                    item.setData(Qt.ItemDataRole.UserRole,r.id)
                    if col in (2,3):
                        item.setTextAlignment(Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignVCenter)
                    if col==2:
                        item.setForeground(QColor("#99e5be" if r.mills>=0 else "#ffb5b9"))
                    if col==4 and r.date_status=="estimated":
                        item.setForeground(QColor("#e2c58c"))
                    if col==1 and r.source_cell:
                        item.setToolTip(f"Original: {r.source_period}\nCell: {r.source_cell}\nSource ID: {r.source_uid}")
                    self.table.setItem(row,col,item)
        finally:
            self.table.setUpdatesEnabled(True)
        self.count_label.setText(f"{len(results):,} of {len(self.all_entries):,} transactions")
        self.update_selection()

    def render_monthly(self):
        months=list(reversed(self.db.monthly_totals()))
        self.monthly.setUpdatesEnabled(False)
        try:
            self.monthly.setRowCount(len(months))
            for row,m in enumerate(months):
                year,month=map(int,m["month"].split("-"))
                pretty=date(year,month,1).strftime("%B %Y")
                values=[pretty,display_money(m["income"]),display_money(m["expense"]),
                        display_money(m["income"]-m["expense"]),display_money(m["closing"])]
                for col,value in enumerate(values):
                    cell=QTableWidgetItem(value)
                    if col:
                        cell.setTextAlignment(Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignVCenter)
                    if col==1:
                        cell.setForeground(QColor("#99e5be"))
                    if col==2:
                        cell.setForeground(QColor("#ffb5b9"))
                    self.monthly.setItem(row,col,cell)
        finally:
            self.monthly.setUpdatesEnabled(True)

    def selected_id(self) -> int | None:
        if self.tabs.currentIndex()!=0 or not self.table.selectionModel().hasSelection():
            return None
        row=self.table.currentRow()
        if row<0:
            return None
        item=self.table.item(row,0)
        return int(item.data(Qt.ItemDataRole.UserRole)) if item else None

    def update_selection(self):
        enabled=self.selected_id() is not None
        self.edit_button.setEnabled(enabled)
        self.delete_button.setEnabled(enabled)

    def add_transaction(self):
        dialog=TransactionDialog(self)
        if dialog.exec()==QDialog.DialogCode.Accepted:
            try:
                self.db.add(dialog.checked_date,dialog.checked_name,dialog.checked_mills,dialog.checked_status)
                self.refresh()
                self.statusBar().showMessage("Transaction saved locally.",5000)
            except Exception as exc:
                error(self,"Unable to save",exc)

    def edit_transaction(self):
        chosen=self.selected_id()
        entry=next((e for e in self.all_entries if e.id==chosen),None)
        if entry is None:
            return
        dialog=TransactionDialog(self,entry)
        if dialog.exec()==QDialog.DialogCode.Accepted:
            try:
                self.db.edit(entry.id,dialog.checked_date,dialog.checked_name,
                             dialog.checked_mills,dialog.checked_status)
                self.refresh()
                self.statusBar().showMessage("Transaction updated; running balances recalculated.",5000)
            except Exception as exc:
                error(self,"Unable to edit",exc)

    def delete_transaction(self):
        entry_id=self.selected_id()
        entry=next((e for e in self.all_entries if e.id==entry_id),None)
        if entry is None:
            return
        if confirm(self,"Delete transaction?",
                   f"Permanently delete '{entry.description}' ({display_money(entry.mills)})?\n\n"
                   "Later running balances will update automatically."):
            try:
                self.db.delete(entry.id)
                self.refresh()
            except Exception as exc:
                error(self,"Unable to delete",exc)

    def import_file(self):
        path,_=QFileDialog.getOpenFileName(self,"Choose Excel or CSV",str(Path.home()),
                                            "Ledger files (*.xlsx *.csv)")
        if not path:
            return
        try:
            QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)
            try:
                data=load_import(path)
                duplicates=self.db.duplicates_in(data)
            finally:
                QApplication.restoreOverrideCursor()
            if not data.transactions:
                raise ValueError("There are no transactions to import.")
            dts=[tx.date for tx in data.transactions]
            opening=display_money(data.opening_mills) if data.opening_mills is not None else "Not specified"
            summary=(f"Format: {data.format}\n"
                     f"Transactions in file: {len(data.transactions):,}\n"
                     f"Already imported: {duplicates:,}\n"
                     f"New transactions: {len(data.transactions)-duplicates:,}\n"
                     f"Opening balance: {opening}\n"
                     f"Date range: {min(dts)} to {max(dts)}\n"
                     f"Estimated dates: {sum(x.date_status=='estimated' for x in data.transactions):,}\n\n"
                     f"{data.note}\n\n"
                     "Continue? Your original file will not be modified.")
            if confirm(self,"Review import",summary):
                inserted,skipped=self.db.import_data(data)
                self.refresh()
                message(self,"Import complete",f"Added {inserted:,} transactions.\nSkipped {skipped:,} already-imported transactions.\n\nBalance: {display_money(self.db.balance())}")
        except Exception as exc:
            error(self,"Import failed",exc)

    def export_file(self):
        path,flt=QFileDialog.getSaveFileName(self,"Export complete ledger",
            str(Path.home()/"glassbalance-export.xlsx"),
            "Excel workbook (*.xlsx);;CSV file (*.csv)")
        if not path:
            return
        try:
            suffix=Path(path).suffix.lower()
            if suffix not in (".csv",".xlsx"):
                path+=(".csv" if "CSV" in flt else ".xlsx")
            if Path(path).suffix.lower()==".csv":
                self.db.export_csv(path)
            else:
                self.db.export_xlsx(path)
            message(self,"Export complete",f"All transactions exported to:\n{path}")
        except Exception as exc:
            error(self,"Export failed",exc)

    def save_backup(self):
        path,_=QFileDialog.getSaveFileName(self,"Save complete local database backup",
            str(backup_folder()/f"glassbalance-{date.today().isoformat()}.sqlite"),"SQLite backup (*.sqlite)")
        if not path:
            return
        try:
            if not path.lower().endswith(".sqlite"):
                path+=".sqlite"
            self.db.backup_to(path)
            message(self,"Backup saved",f"A complete local database backup is saved at:\n{path}")
        except Exception as exc:
            error(self,"Backup failed",exc)

    def restore_backup(self):
        path,_=QFileDialog.getOpenFileName(self,"Select GlassBalance backup",str(backup_folder()),
                                            "SQLite backup (*.sqlite *.db)")
        if not path:
            return
        if not confirm(self,"Replace local data?",
           "Restoring a backup will REPLACE all current transactions.\n\n"
           "A local safety backup will be created first. Proceed?"):
            return
        try:
            safety=backup_folder()/f"before-local-restore-{datetime.now().strftime('%Y%m%d-%H%M%S')}.sqlite"
            self.db.backup_to(safety)
            self.db.restore_from(path)
            self.refresh()
            message(self,"Ledger restored",f"Restore complete.\n\nSafety backup of your previous ledger:\n{safety}")
        except Exception as exc:
            error(self,"Restore failed",exc)

    def email_backup(self):
        dialog=EmailDialog(self,self.db)
        if dialog.exec()==QDialog.DialogCode.Accepted:
            self.refresh()

    def edit_opening(self):
        opening,when,status=self.db.opening()
        dialog=OpeningDialog(self,opening,when,status)
        if dialog.exec()==QDialog.DialogCode.Accepted:
            if self.db.count() and opening!=dialog.checked_mills:
                if not confirm(self,"Change historical totals?",
                     "Changing your opening balance will change the total and every historical running balance. Continue?"):
                    return
            try:
                self.db.set_opening(dialog.checked_mills,dialog.checked_date,dialog.checked_status)
                self.refresh()
            except Exception as exc:
                error(self,"Opening balance",exc)

    def closeEvent(self,event):
        self.db.close()
        super().closeEvent(event)


def run():
    QApplication.setApplicationName("GlassBalance")
    QApplication.setOrganizationName("GlassBalance")
    if sys.platform.startswith("linux"):
        QApplication.setDesktopFileName("io.github.Onimee58.GlassBalance")
    app=QApplication(sys.argv)
    app.setWindowIcon(app_icon())
    app.setFont(QFont("Segoe UI",10))
    window=Window()
    window.show()
    return app.exec()
