"""An alpha.1-era database (no category/recurring tables) must open and restore cleanly."""
import sqlite3
import tempfile
import unittest
from pathlib import Path

from glassbalance.database import Ledger
from glassbalance import categories, recurring, unbalanced

OLD_SCHEMA = """
CREATE TABLE state (id INTEGER PRIMARY KEY CHECK (id=1), opening_mills INTEGER NOT NULL DEFAULT 0,
    opening_date TEXT NOT NULL DEFAULT '1970-01-01', opening_status TEXT NOT NULL DEFAULT 'confirmed');
INSERT INTO state VALUES (1, 250000, '2026-01-01', 'confirmed');
CREATE TABLE transactions (id INTEGER PRIMARY KEY AUTOINCREMENT, tx_date TEXT NOT NULL,
    description TEXT NOT NULL, amount_mills INTEGER NOT NULL,
    date_status TEXT NOT NULL CHECK(date_status IN ('estimated','confirmed')),
    source_uid TEXT UNIQUE NOT NULL, source_period TEXT NOT NULL DEFAULT '',
    source_cell TEXT NOT NULL DEFAULT '', source_order INTEGER, created_at TEXT NOT NULL, updated_at TEXT NOT NULL);
CREATE TABLE transaction_comments (transaction_id INTEGER PRIMARY KEY REFERENCES transactions(id) ON DELETE CASCADE,
    note TEXT NOT NULL DEFAULT '');
INSERT INTO transactions VALUES (1,'2026-01-02','Salary',1000000,'confirmed','u1','','',NULL,'x','x');
INSERT INTO transactions VALUES (2,'2026-01-03','Rent',-600000,'estimated','u2','','',NULL,'x','x');
INSERT INTO transaction_comments VALUES (2,'January rent');
"""


def make_old(path):
    con=sqlite3.connect(path)
    con.executescript(OLD_SCHEMA)
    con.commit()
    con.close()


class MigrationTests(unittest.TestCase):
    def test_open_old_database_preserves_everything(self):
        with tempfile.TemporaryDirectory() as d:
            path=Path(d)/'old.sqlite'
            make_old(path)
            db=Ledger(path)
            self.assertEqual((db.count(),db.balance()),(2,650000))
            self.assertEqual(db.comment(2),'January rent')
            self.assertEqual(categories.summary(db.conn)[0]['category'],'Uncategorized')
            self.assertEqual(recurring.templates(db),[])
            self.assertEqual(unbalanced.loan_rows(db),[])
            db.set_category(1,'Income')
            db.close()
            db=Ledger(path)
            self.assertEqual(db.category(1),'Income')
            db.close()

    def test_restore_old_backup_recreates_feature_tables(self):
        with tempfile.TemporaryDirectory() as d:
            old=Path(d)/'old.sqlite'
            make_old(old)
            db=Ledger(Path(d)/'current.sqlite')
            t=recurring.add_template(db,'Rent',-1,1)
            db.restore_from(old)
            self.assertEqual(db.count(),2)
            self.assertEqual(recurring.templates(db),[])
            db.set_category(2,'Housing')
            recurring.add_template(db,'Rent',-600000,2)
            self.assertEqual(unbalanced.loan_rows(db),[])
            db.close()


if __name__=='__main__': unittest.main()
