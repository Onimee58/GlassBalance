"""Optional transaction notes; does not alter ledger amounts."""

def install(conn):
    with conn:
        conn.execute('''CREATE TABLE IF NOT EXISTS transaction_comments (
            transaction_id INTEGER PRIMARY KEY REFERENCES transactions(id) ON DELETE CASCADE,
            note TEXT NOT NULL DEFAULT ''
        )''')


def get(conn, tx_id):
    row=conn.execute('SELECT note FROM transaction_comments WHERE transaction_id=?',(tx_id,)).fetchone()
    return str(row[0]) if row else ''


def set_note(conn, tx_id, note):
    if len(note)>5000: raise ValueError('Comment cannot exceed 5000 characters')
    with conn:
        if not conn.execute('SELECT 1 FROM transactions WHERE id=?',(tx_id,)).fetchone():
            raise ValueError('Transaction does not exist')
        if note.strip():
            conn.execute('INSERT INTO transaction_comments(transaction_id,note) VALUES(?,?) ON CONFLICT(transaction_id) DO UPDATE SET note=excluded.note',(tx_id,note.strip()))
        else:
            conn.execute('DELETE FROM transaction_comments WHERE transaction_id=?',(tx_id,))
