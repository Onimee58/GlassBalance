"""Optional transaction categories; never alter ledger amounts or balances."""
from __future__ import annotations

UNCATEGORIZED = "Uncategorized"
MAX_LENGTH = 60


def install(conn) -> None:
    with conn:
        conn.execute('''CREATE TABLE IF NOT EXISTS transaction_categories (
            transaction_id INTEGER PRIMARY KEY REFERENCES transactions(id) ON DELETE CASCADE,
            category TEXT NOT NULL
        )''')
        conn.execute('CREATE INDEX IF NOT EXISTS idx_tx_category ON transaction_categories(category)')


def clean(name: str | None) -> str:
    """Normalize a category name. Blank or 'Uncategorized' means no category."""
    name = " ".join(str(name or "").split())
    if len(name) > MAX_LENGTH:
        raise ValueError(f"Category names cannot exceed {MAX_LENGTH} characters.")
    if not name or name.casefold() == UNCATEGORIZED.casefold():
        return ""
    return name


def get(conn, tx_id: int) -> str:
    row = conn.execute('SELECT category FROM transaction_categories WHERE transaction_id=?', (tx_id,)).fetchone()
    return str(row[0]) if row else ""


def set_category(conn, tx_id: int, name: str | None) -> str:
    """Assign a category (blank clears it). Returns the stored name or ''."""
    name = clean(name)
    # Reuse the existing spelling of a category that differs only by case.
    if name:
        existing = conn.execute('SELECT category FROM transaction_categories WHERE category=? COLLATE NOCASE LIMIT 1',
                                (name,)).fetchone()
        if existing:
            name = str(existing[0])
    with conn:
        if not conn.execute('SELECT 1 FROM transactions WHERE id=?', (tx_id,)).fetchone():
            raise ValueError("Transaction does not exist.")
        if name:
            conn.execute('''INSERT INTO transaction_categories(transaction_id,category) VALUES(?,?)
                            ON CONFLICT(transaction_id) DO UPDATE SET category=excluded.category''', (tx_id, name))
        else:
            conn.execute('DELETE FROM transaction_categories WHERE transaction_id=?', (tx_id,))
    return name


def mapping(conn) -> dict[int, str]:
    return {int(r[0]): str(r[1]) for r in conn.execute('SELECT transaction_id,category FROM transaction_categories')}


def names(conn) -> list[str]:
    return [str(r[0]) for r in conn.execute(
        'SELECT DISTINCT category FROM transaction_categories ORDER BY category COLLATE NOCASE')]


def summary(conn) -> list[dict]:
    """Income/expense per category across ALL transactions, Uncategorized included.

    Totals always reconcile with the ledger: sum(income)-sum(expense) equals the
    sum of all transaction amounts (opening balance excluded).
    """
    rows = conn.execute('''
        SELECT COALESCE(c.category, ?) AS category,
               SUM(CASE WHEN t.amount_mills>0 THEN t.amount_mills ELSE 0 END) AS income,
               SUM(CASE WHEN t.amount_mills<0 THEN -t.amount_mills ELSE 0 END) AS expense,
               COUNT(*) AS count
        FROM transactions t LEFT JOIN transaction_categories c ON c.transaction_id=t.id
        GROUP BY COALESCE(c.category, ?)
        ORDER BY expense DESC, income DESC, category COLLATE NOCASE
    ''', (UNCATEGORIZED, UNCATEGORIZED)).fetchall()
    return [{"category": str(r[0]), "income": int(r[1]), "expense": int(r[2]), "count": int(r[3])} for r in rows]
