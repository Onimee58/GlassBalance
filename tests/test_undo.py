import unittest

from glassbalance.database import Ledger
from glassbalance import unbalanced


class UndoDeletionTests(unittest.TestCase):
    def setUp(self):
        self.db=Ledger()
        self.db.set_opening(500000,'2026-09-30')
        self.a=self.db.add('2026-10-01','Coffee',-4500)
        self.b=self.db.add('2026-10-02','Lunch',-12500)
        self.c=self.db.add('2026-10-03','Salary',300000)

    def tearDown(self): self.db.close()

    def test_restore_keeps_id_comment_category_and_balance(self):
        self.db.set_comment(self.b,'Team lunch')
        self.db.set_category(self.b,'Food')
        before=(self.db.balance(),[(e.id,e.running_mills) for e in self.db.entries()])
        snap=self.db.delete(self.b)
        self.assertNotEqual(self.db.balance(),before[0])
        self.assertEqual(self.db.restore_deleted(snap),self.b)
        self.assertEqual((self.db.balance(),[(e.id,e.running_mills) for e in self.db.entries()]),before)
        self.assertEqual(self.db.comment(self.b),'Team lunch')
        self.assertEqual(self.db.category(self.b),'Food')

    def test_double_restore_is_refused(self):
        snap=self.db.delete(self.a)
        self.db.restore_deleted(snap)
        with self.assertRaises(ValueError):
            self.db.restore_deleted(snap)
        self.assertEqual(self.db.count(),3)

    def test_ids_are_not_reused_after_delete(self):
        snap=self.db.delete(self.c)
        newer=self.db.add('2026-10-04','Bus',-2750)
        self.assertGreater(newer,self.c)
        self.db.restore_deleted(snap)
        self.assertEqual(self.db.count(),4)

    def test_only_last_snapshot_matters_to_ui_but_each_is_independent(self):
        first=self.db.delete(self.a)
        second=self.db.delete(self.b)
        self.db.restore_deleted(second)
        ids={e.id for e in self.db.entries()}
        self.assertIn(self.b,ids)
        self.assertNotIn(self.a,ids)

    def test_loan_linked_transactions_cannot_be_deleted(self):
        unbalanced.register_loan(self.db,self.a,'Alex')
        with self.assertRaises(ValueError):
            self.db.delete(self.a)
        self.assertEqual(len(unbalanced.loan_rows(self.db)),1)
        loan=unbalanced.loan_rows(self.db)[0]
        unbalanced.remove_loan(self.db,loan.id)
        self.db.delete(self.a)
        self.assertEqual(self.db.count(),2)

    def test_loan_repayment_cannot_be_deleted_until_unlinked(self):
        lent=self.db.add('2026-10-05','Lent Sam',-50000)
        back=self.db.add('2026-10-06','Sam refund',20000)
        unbalanced.register_loan(self.db,lent,'Sam')
        unbalanced.confirm_repayment(self.db,unbalanced.loan_rows(self.db)[0].id,back)
        with self.assertRaises(ValueError):
            self.db.delete(back)
        unbalanced.unlink_repayment(self.db,back)
        self.db.delete(back)


if __name__=='__main__': unittest.main()
