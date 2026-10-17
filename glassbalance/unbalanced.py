"""Opt-in lending relationships; never changes ledger transactions or auto-settles."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class LoanRow:
    id: int
    person: str
    direction: str
    principal_mills: int
    repaid_mills: int
    origin_id: int
    description: str

    @property
    def outstanding_mills(self) -> int:
        return self.principal_mills - self.repaid_mills


def install(ledger):
    ledger.conn.executescript('''
        CREATE TABLE IF NOT EXISTS loan_records (
            id INTEGER PRIMARY KEY,
            origin_tx_id INTEGER NOT NULL UNIQUE REFERENCES transactions(id) ON DELETE CASCADE,
            person TEXT NOT NULL,
            direction TEXT NOT NULL CHECK (direction IN ('lent','borrowed')),
            created_at TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS loan_repayments (
            id INTEGER PRIMARY KEY,
            loan_id INTEGER NOT NULL REFERENCES loan_records(id) ON DELETE CASCADE,
            repayment_tx_id INTEGER NOT NULL UNIQUE REFERENCES transactions(id) ON DELETE CASCADE,
            created_at TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS dismissed_suggestions (
            repayment_tx_id INTEGER NOT NULL REFERENCES transactions(id) ON DELETE CASCADE,
            loan_id INTEGER NOT NULL REFERENCES loan_records(id) ON DELETE CASCADE,
            PRIMARY KEY (repayment_tx_id, loan_id)
        );
    ''')


def loan_rows(ledger):
    rows = ledger.conn.execute('''
        SELECT l.id, l.person, l.direction, l.origin_tx_id, t.description,
               ABS(t.amount_mills) AS principal,
               COALESCE(SUM(ABS(r.amount_mills)),0) AS repaid
        FROM loan_records l
        JOIN transactions t ON t.id=l.origin_tx_id
        LEFT JOIN loan_repayments p ON p.loan_id=l.id
        LEFT JOIN transactions r ON r.id=p.repayment_tx_id
        GROUP BY l.id ORDER BY l.id DESC
    ''').fetchall()
    return [LoanRow(int(r['id']),r['person'],r['direction'],int(r['principal']),int(r['repaid']),
                    int(r['origin_tx_id']),r['description']) for r in rows]


def register_loan(ledger, transaction_id, person):
    person=person.strip()
    if not person or len(person)>100:
        raise ValueError('Please enter a person name (up to 100 characters).')
    row=ledger.conn.execute('SELECT amount_mills FROM transactions WHERE id=?',(transaction_id,)).fetchone()
    if row is None or int(row[0])==0:
        raise ValueError('Choose an existing transaction with a non-zero amount.')
    direction='lent' if row[0]<0 else 'borrowed'
    with ledger.conn:
        ledger.conn.execute('INSERT INTO loan_records(origin_tx_id,person,direction,created_at) VALUES(?,?,?,datetime("now"))',
                            (transaction_id,person,direction))
    return direction


def confirm_repayment(ledger, loan_id, transaction_id):
    loans={loan.id:loan for loan in loan_rows(ledger)}
    if loan_id not in loans:
        raise ValueError('Loan does not exist.')
    loan=loans[loan_id]
    tx=ledger.conn.execute('SELECT amount_mills FROM transactions WHERE id=?',(transaction_id,)).fetchone()
    if tx is None:
        raise ValueError('Transaction does not exist.')
    amount=int(tx[0])
    if (loan.direction=='lent' and amount<=0) or (loan.direction=='borrowed' and amount>=0):
        raise ValueError('Repayment must have the opposite sign from the original loan.')
    if abs(amount)>loan.outstanding_mills:
        raise ValueError('Repayment exceeds the remaining loan amount.')
    if transaction_id==loan.origin_id:
        raise ValueError('A loan cannot repay itself.')
    with ledger.conn:
        ledger.conn.execute('INSERT INTO loan_repayments(loan_id,repayment_tx_id,created_at) VALUES(?,?,datetime("now"))',
                            (loan_id,transaction_id))
        ledger.conn.execute('DELETE FROM dismissed_suggestions WHERE repayment_tx_id=? AND loan_id=?',
                            (transaction_id,loan_id))


def unlink_repayment(ledger, repayment_tx_id):
    with ledger.conn:
        ledger.conn.execute('DELETE FROM loan_repayments WHERE repayment_tx_id=?',(repayment_tx_id,))


def dismiss_suggestion(ledger, loan_id, transaction_id):
    with ledger.conn:
        ledger.conn.execute('INSERT OR IGNORE INTO dismissed_suggestions(repayment_tx_id,loan_id) VALUES(?,?)',
                            (transaction_id,loan_id))


def suggestions(ledger, loan_id):
    loan=next((x for x in loan_rows(ledger) if x.id==loan_id),None)
    if not loan or loan.outstanding_mills<=0:
        return []
    rows=ledger.conn.execute('''
        SELECT t.* FROM transactions t
        LEFT JOIN loan_repayments rp ON rp.repayment_tx_id=t.id
        LEFT JOIN loan_records lr ON lr.origin_tx_id=t.id
        LEFT JOIN dismissed_suggestions ds ON ds.repayment_tx_id=t.id AND ds.loan_id=?
        WHERE rp.id IS NULL AND lr.id IS NULL AND ds.loan_id IS NULL
        AND ((?='lent' AND t.amount_mills>0) OR (?='borrowed' AND t.amount_mills<0))
        AND ABS(t.amount_mills)<=?
        ORDER BY t.tx_date DESC, t.id DESC
    ''',(loan.id,loan.direction,loan.direction,loan.outstanding_mills)).fetchall()
    terms=loan.person.casefold().split()
    return [dict(r) for r in rows if terms and all(token in r['description'].casefold() for token in terms)
            and ('refund' in r['description'].casefold() or 'repay' in r['description'].casefold()
                 or 'return' in r['description'].casefold())]


def linked_repayments(ledger, loan_id):
    return [dict(r) for r in ledger.conn.execute('''
        SELECT t.* FROM loan_repayments p JOIN transactions t ON t.id=p.repayment_tx_id
        WHERE p.loan_id=? ORDER BY t.tx_date,t.id''',(loan_id,))]


def remove_loan(ledger, loan_id):
    """Remove only loan classification; original transactions are untouched."""
    with ledger.conn:
        row=ledger.conn.execute("SELECT id FROM loan_records WHERE id=?", (loan_id,)).fetchone()
        if row is None:
            raise ValueError("Loan no longer exists")
        ledger.conn.execute("DELETE FROM loan_repayments WHERE loan_id=?", (loan_id,))
        ledger.conn.execute("DELETE FROM dismissed_suggestions WHERE loan_id=?", (loan_id,))
        ledger.conn.execute("DELETE FROM loan_records WHERE id=?", (loan_id,))
