"""Recurring transaction templates. Nothing is ever posted without explicit confirmation.

Templates never affect balances. Posting creates one ordinary ledger transaction per
template per month; a second post for the same month is refused. If the user deletes
the posted transaction, that month becomes postable again (undoing the deletion
restores the post record as well).
"""
from __future__ import annotations

import calendar
from dataclasses import dataclass
from datetime import date, datetime, timezone

from . import categories


@dataclass(frozen=True)
class Template:
    id: int
    name: str
    mills: int
    day: int
    category: str


def install(conn) -> None:
    conn.executescript('''
        CREATE TABLE IF NOT EXISTS recurring_templates (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            amount_mills INTEGER NOT NULL CHECK (amount_mills<>0),
            day_of_month INTEGER NOT NULL CHECK (day_of_month BETWEEN 1 AND 31),
            category TEXT NOT NULL DEFAULT '',
            created_at TEXT NOT NULL DEFAULT (datetime('now'))
        );
        CREATE TABLE IF NOT EXISTS recurring_posts (
            template_id INTEGER NOT NULL REFERENCES recurring_templates(id) ON DELETE CASCADE,
            month TEXT NOT NULL,
            transaction_id INTEGER NOT NULL UNIQUE REFERENCES transactions(id) ON DELETE CASCADE,
            PRIMARY KEY (template_id, month)
        );
    ''')


def _month(value: str) -> tuple[int, int]:
    try:
        year, month = (int(x) for x in str(value).split("-"))
        date(year, month, 1)
    except Exception as exc:
        raise ValueError("Month must be YYYY-MM.") from exc
    return year, month


def post_date(day: int, month: str) -> str:
    """Clamp day-of-month to the month's length (31 → 28/29 in February)."""
    year, mon = _month(month)
    return date(year, mon, min(int(day), calendar.monthrange(year, mon)[1])).isoformat()


def add_template(ledger, name: str, mills: int, day: int, category: str = "") -> int:
    name = " ".join(str(name).split())
    if not name or len(name) > 300:
        raise ValueError("Template name must contain 1 to 300 characters.")
    if not isinstance(mills, int) or isinstance(mills, bool) or mills == 0:
        raise ValueError("Recurring amount must be a non-zero amount.")
    if abs(mills) > 100_000_000_000:
        raise ValueError("Amount is outside the supported range.")
    if not 1 <= int(day) <= 31:
        raise ValueError("Day of month must be between 1 and 31.")
    category = categories.clean(category)
    with ledger.conn:
        cur = ledger.conn.execute('INSERT INTO recurring_templates(name,amount_mills,day_of_month,category) VALUES(?,?,?,?)',
                                  (name, mills, int(day), category))
    return int(cur.lastrowid)


def remove_template(ledger, template_id: int) -> None:
    """Remove a template only. Transactions it already posted stay in the ledger."""
    with ledger.conn:
        cur = ledger.conn.execute('DELETE FROM recurring_templates WHERE id=?', (template_id,))
        if cur.rowcount != 1:
            raise ValueError("Recurring template no longer exists.")


def templates(ledger) -> list[Template]:
    return [Template(int(r['id']), r['name'], int(r['amount_mills']), int(r['day_of_month']), r['category'])
            for r in ledger.conn.execute('SELECT * FROM recurring_templates ORDER BY day_of_month, name COLLATE NOCASE')]


def posted_transaction(ledger, template_id: int, month: str) -> int | None:
    row = ledger.conn.execute('SELECT transaction_id FROM recurring_posts WHERE template_id=? AND month=?',
                              (template_id, month)).fetchone()
    return int(row[0]) if row else None


def post(ledger, template_id: int, month: str | None = None) -> int:
    """Post one template for a month. Caller (UI) must have obtained user confirmation."""
    month = month or date.today().strftime("%Y-%m")
    _month(month)
    row = ledger.conn.execute('SELECT * FROM recurring_templates WHERE id=?', (template_id,)).fetchone()
    if row is None:
        raise ValueError("Recurring template no longer exists.")
    if posted_transaction(ledger, template_id, month) is not None:
        raise ValueError(f"'{row['name']}' has already been posted for {month}.")
    when = post_date(int(row['day_of_month']), month)
    uid = f"glassbalance:recurring:{template_id}:{month}"
    with ledger.conn:
        if ledger.conn.execute('SELECT 1 FROM transactions WHERE source_uid=?', (uid,)).fetchone():
            raise ValueError(f"'{row['name']}' has already been posted for {month}.")
        now = datetime.now(timezone.utc).isoformat(timespec="seconds")
        cur = ledger.conn.execute('''INSERT INTO transactions(tx_date,description,amount_mills,date_status,source_uid,
                source_period,source_cell,source_order,created_at,updated_at) VALUES(?,?,?,?,?,?,?,?,?,?)''',
                (when, row['name'], int(row['amount_mills']), 'confirmed', uid, f"Recurring {month}", '', None, now, now))
        tx_id = int(cur.lastrowid)
        ledger.conn.execute('INSERT INTO recurring_posts(template_id,month,transaction_id) VALUES(?,?,?)',
                            (template_id, month, tx_id))
        if row['category']:
            ledger.conn.execute('INSERT INTO transaction_categories(transaction_id,category) VALUES(?,?)',
                                (tx_id, row['category']))
    return tx_id
