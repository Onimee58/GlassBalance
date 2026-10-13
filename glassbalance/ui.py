"""Qt 6 desktop interface for GlassBalance.

Pure QWidget interface (no browser/web view). Transparent panels over a subtle
painted gradient make a restrained glass-inspired layout on Windows and Linux.
"""
from __future__ import annotations

import sys
from datetime import date, datetime
from pathlib import Path

from PySide6.QtCore import QDate, QSettings, Qt, QStandardPaths
from PySide6.QtGui import QColor, QFont, QLinearGradient, QPainter, QPen, QRadialGradient
from PySide6.QtWidgets import (
    QApplication, QAbstractItemView, QComboBox, QDateEdit, QDialog,
    QDialogButtonBox, QFileDialog, QFormLayout, QFrame, QGridLayout,
    QHBoxLayout, QHeaderView, QLabel, QLineEdit, QMainWindow, QMessageBox,
    QPushButton, QSizePolicy, QTabWidget, QTableWidget, QTableWidgetItem,
    QVBoxLayout, QWidget,
)

from . import __version__
from .database import Entry, Ledger
from .email_backup import decrypt_snapshot, download_latest_backup, send_backup
from .importer import load_import
from .money import as_mills, display_money, mills_as_decimal


STYLE = """
QWidget { color: #e8edf8; font-family: "Segoe UI", "Inter", sans-serif; font-size: 13px; }
QFrame#glass { background-color: rgba(19, 32, 51, 225); border: 1px solid rgba(153, 187, 219, 45); border-radius: 18px; }
QFrame#stat { background-color: rgba(22, 38, 58, 218); border: 1px solid rgba(158, 189, 222, 46); border-radius: 16px; }
QLabel#brand { color: #fafcff; font-size: 22px; font-weight: 800; letter-spacing: 1px; }
QLabel#title { color: #fafcff; font-size: 27px; font-weight: 730; }
QLabel#muted { color: #9daec4; font-size: 12px; }
QLabel#section { color: #ebf5ff; font-size: 17px; font-weight: 700; }
QLabel#statTitle { color: #acbcd0; font-size: 12px; font-weight: 600; }
QLabel#value { color: #fafcff; font-size: 30px; font-weight: 750; }
QLabel#valueIn { color: #9de7c5; font-size: 25px; font-weight: 700; }
QLabel#valueOut { color: #ffb9b9; font-size: 25px; font-weight: 700; }
QLabel#overline { color: #8ad9d4; font-size: 11px; font-weight: 700; letter-spacing: 1.3px; }
QPushButton { background-color: rgba(105, 134, 169, 35); color: #edf6ff; border: 1px solid rgba(155, 191, 224, 54); border-radius: 10px; padding: 10px 14px; font-weight: 600; min-height: 19px; }
QPushButton:hover { background-color: rgba(112, 150, 190, 66); border-color: rgba(171, 213, 237, 102); }
QPushButton:pressed { background-color: rgba(112, 150, 190, 90); }
QPushButton:disabled { color: #66788a; background-color: rgba(70, 87, 108, 20); border-color: rgba(100, 114, 136, 24); }
QPushButton#primary { background-color: #55c4b9; color: #0d2730; border: 1px solid #65dfcd; font-weight: 800; }
QPushButton#primary:hover { background-color: #83e4da; }
QPushButton#danger { color: #ffd1d5; }
QPushButton#danger:hover { background-color: rgba(180, 60, 70, 75); }
QLineEdit, QComboBox, QDateEdit { background-color: rgba(10, 21, 37, 190); color: #eef7ff; border: 1px solid #354b62; border-radius: 10px; padding: 9px 11px; min-height: 20px; selection-background-color: #167e87; }
QLineEdit:focus, QComboBox:focus, QDateEdit:focus { border: 1px solid #76d6cc; }
QComboBox::drop-down, QDateEdit::drop-down { border: none; width: 20px; }
QComboBox QAbstractItemView { color: #f3f6fc; background: #1b2a3e; selection-background-color: #2d606b; border: 1px solid #526479; }
QTabWidget::pane { background: transparent; border: none; }
QTabBar::tab { color: #9fb1c8; background: transparent; padding: 12px 22px; border: none; border-bottom: 2px solid transparent; font-weight: 700; }
QTabBar::tab:selected { color: #99eae1; border-bottom: 2px solid #55c4b9; }
QTabBar::tab:hover { color: white; }
QTableWidget { background-color: transparent; alternate-background-color: rgba(105, 134, 167, 10); color: #edf3f9; border: none; gridline-color: transparent; selection-background-color: rgba(70, 145, 158, 76); selection-color: white; padding: 1px; outline: none; }
QTableWidget::item { padding: 7px 8px; border-bottom: 1px solid rgba(120, 160, 190, 16); }
QTableWidget::item:selected { background-color: rgba(72, 147, 157, 100); }
QHeaderView::section { color: #96aabd; background: rgba(20, 36, 56, 185); border: none; padding: 10px 11px; font-weight: 650; }
QTableCornerButton::section { background: transparent; border: none; }
QScrollBar:vertical { background: rgba(22, 37, 53, 95); width: 11px; }
QScrollBar::handle:vertical { background: #536b80; border-radius: 5px; min-height: 30px; }
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }
QScrollBar:horizontal { height: 10px; background: rgba(22, 37, 53, 95); }
QScrollBar::handle:horizontal { background: #536b80; border-radius: 4px; min-width: 30px; }
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal { width: 0; }
QDialog { background-color: #18293f; }
QLabel { background: transparent; }
QStatusBar { color: #95b3c1; background: transparent; }
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


class Window(QMainWindow):
    def __init__(self, db_path: str | Path | None=None):
        super().__init__()
        self.setWindowTitle(f"GlassBalance  ·  Personal ledger  ·  v{__version__}")
        self.resize(1280,820)
        self.setMinimumSize(960,640)
        self.db=Ledger(db_path or (data_folder()/"balance.sqlite"))
        self.setStyleSheet(STYLE)
        self.canvas=GradientCanvas()
        self.setCentralWidget(self.canvas)
        self.build()
        self.refresh()
        self.statusBar().showMessage(f"Offline • Stored only on this computer • {self.db.path or 'Memory'}")

    def build(self):
        root=QHBoxLayout(self.canvas)
        root.setContentsMargins(22,22,22,20)
        root.setSpacing(21)
        left=panel()
        left.setFixedWidth(220)
        sidebar=QVBoxLayout(left)
        sidebar.setContentsMargins(19,22,19,17)
        sidebar.setSpacing(10)
        brand_row=QHBoxLayout()
        logo=label("◈")
        logo.setStyleSheet("color:#75e4d6; font-size:27px;")
        brand_row.addWidget(logo)
        brand_row.addWidget(label("BALANCE","brand"),1)
        sidebar.addLayout(brand_row)
        sidebar.addWidget(label("A quieter way to track money.","muted",True))
        sidebar.addSpacing(25)
        sidebar.addWidget(label("YOUR LEDGER","overline"))
        self.side_new=button("＋  New transaction","primary")
        self.side_import=button("↳  Import Excel / CSV")
        self.side_export=button("⇧  Export all data")
        self.side_backup=button("▣  Save local backup")
        self.side_restore=button("↩  Restore backup")
        self.side_email=button("✉  Email backups")
        self.side_opening=button("◉  Opening balance")
        for b in (self.side_new,self.side_import,self.side_export,self.side_backup,
                  self.side_restore,self.side_email,self.side_opening):
            b.setSizePolicy(QSizePolicy.Policy.Expanding,QSizePolicy.Policy.Fixed)
            sidebar.addWidget(b)
        sidebar.addStretch()
        sidebar.addWidget(label("●  Offline-first","overline"))
        sidebar.addWidget(label("Your database stays on this device unless you export it or deliberately send an encrypted email backup.","muted",True))
        sidebar.addSpacing(8)
        sidebar.addWidget(label(f"VERSION {__version__}  •  OPEN SOURCE","muted"))
        root.addWidget(left)

        main=QWidget()
        main.setSizePolicy(QSizePolicy.Policy.Expanding,QSizePolicy.Policy.Expanding)
        root.addWidget(main,1)
        content=QVBoxLayout(main)
        content.setContentsMargins(0,2,1,0)
        content.setSpacing(17)
        header=QHBoxLayout()
        text_block=QVBoxLayout()
        text_block.setSpacing(4)
        text_block.addWidget(label("PERSONAL FINANCE  /  LEDGER","overline"))
        text_block.addWidget(label("Your balance, at a glance","title"))
        text_block.addWidget(label("Every entry, every month, one continuous history.","muted"))
        header.addLayout(text_block,1)
        create=button("＋  Add transaction","primary")
        create.clicked.connect(self.add_transaction)
        header.addWidget(create,alignment=Qt.AlignmentFlag.AlignBottom)
        content.addLayout(header)

        cards=QHBoxLayout()
        cards.setSpacing(13)
        self.balance_value=self._stat(cards,"TOTAL LEDGER BALANCE","$0.00","value",
                                      "Opening balance + all transactions")
        self.income_value=self._stat(cards,"MONEY IN THIS MONTH","$0.00","valueIn",
                                     "Positive transactions")
        self.expense_value=self._stat(cards,"MONEY OUT THIS MONTH","$0.00","valueOut",
                                      "Negative transactions")
        content.addLayout(cards)

        activity=panel()
        activity_layout=QVBoxLayout(activity)
        activity_layout.setContentsMargins(19,17,19,15)
        activity_layout.setSpacing(13)
        activity_header=QHBoxLayout()
        activity_header.addWidget(label("Activity","section"))
        activity_header.addStretch()
        self.count_label=label("0 transactions","muted")
        activity_header.addWidget(self.count_label)
        activity_layout.addLayout(activity_header)
        filters=QHBoxLayout()
        filters.setSpacing(9)
        self.search=QLineEdit()
        self.search.setPlaceholderText("Search transactions…")
        self.search.setClearButtonEnabled(True)
        self.search.setMinimumWidth(150)
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
        self.table.setHorizontalHeaderLabels(["DATE","DESCRIPTION","CHANGE","BALANCE","DATE STATUS"])
        self._setup_table(self.table)
        header=self.table.horizontalHeader()
        header.setSectionResizeMode(0,QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1,QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2,QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3,QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(4,QHeaderView.ResizeMode.ResizeToContents)
        self.table.setMinimumHeight(260)
        self.tabs.addTab(self.table,"Transactions")
        self.monthly=QTableWidget(0,5)
        self.monthly.setHorizontalHeaderLabels(["MONTH","MONEY IN","MONEY OUT","NET CHANGE","END BALANCE"])
        self._setup_table(self.monthly)
        mh=self.monthly.horizontalHeader()
        for col in range(5):
            mh.setSectionResizeMode(col,QHeaderView.ResizeMode.Stretch)
        self.tabs.addTab(self.monthly,"Monthly history")
        activity_layout.addWidget(self.tabs,1)
        bottom=QHBoxLayout()
        bottom.addWidget(label("Double-click a transaction to edit it. Dates marked ~ are estimated.","muted",True),1)
        self.edit_button=button("Edit selected")
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
        self.search.textChanged.connect(self.render_transactions)
        self.period.currentIndexChanged.connect(self.period_changed)
        self.from_date.dateChanged.connect(self.render_transactions)
        self.to_date.dateChanged.connect(self.render_transactions)
        self.table.itemSelectionChanged.connect(self.update_selection)
        self.table.cellDoubleClicked.connect(lambda *_:self.edit_transaction())
        self.edit_button.clicked.connect(self.edit_transaction)
        self.delete_button.clicked.connect(self.delete_transaction)
        self.tabs.currentChanged.connect(self.update_selection)

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
        month=date.today().strftime("%Y-%m")
        in_month=sum(max(r.mills,0) for r in self.all_entries if r.date.startswith(month))
        out_month=sum(max(-r.mills,0) for r in self.all_entries if r.date.startswith(month))
        self.income_value.setText(display_money(in_month))
        self.expense_value.setText(display_money(out_month))
        self.render_transactions()
        self.render_monthly()

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
    app=QApplication(sys.argv)
    app.setFont(QFont("Segoe UI",10))
    window=Window()
    window.show()
    return app.exec()
