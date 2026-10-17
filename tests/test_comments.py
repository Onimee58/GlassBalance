import unittest
from glassbalance.database import Ledger

class NotesTest(unittest.TestCase):
    def test_comments_do_not_modify_balance_and_survive_edits(self):
        db=Ledger()
        row=db.add('2026-10-01','Walmart',-15000)
        balance=db.balance()
        db.set_comment(row,'Groceries')
        self.assertEqual(db.comment(row),'Groceries')
        self.assertEqual(db.balance(),balance)
        db.edit(row,'2026-10-02','Walmart',-15000)
        self.assertEqual(db.comment(row),'Groceries')
        db.set_comment(row,'')
        self.assertEqual(db.comment(row),'')
        db.close()

    def test_comment_deleted_with_transaction(self):
        db=Ledger()
        row=db.add('2026-10-01','Lunch',-15000)
        db.set_comment(row,'Work lunch')
        db.delete(row)
        self.assertEqual(db.comment(row),'')
        db.close()

    def test_comment_limit(self):
        db=Ledger()
        row=db.add('2026-10-01','Lunch',-15000)
        with self.assertRaises(ValueError): db.set_comment(row,'a'*5001)
        db.close()
