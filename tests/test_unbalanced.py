import unittest
from glassbalance.database import Ledger
from glassbalance import unbalanced

class LoanTests(unittest.TestCase):
    def setUp(self):
        self.db=Ledger()
        unbalanced.install(self.db)
        self.origin=self.db.add('2026-08-01','Lent ammu',-500000)
        self.refund=self.db.add('2026-08-15','Ammu refund',200000)
        self.base=self.db.balance()

    def tearDown(self): self.db.close()

    def test_manual_confirmation_and_no_ledger_change(self):
        unbalanced.register_loan(self.db,self.origin,'Ammu')
        loan=unbalanced.loan_rows(self.db)[0]
        self.assertEqual(loan.outstanding_mills,500000)
        self.assertEqual(len(unbalanced.suggestions(self.db,loan.id)),1)
        self.assertEqual(unbalanced.loan_rows(self.db)[0].outstanding_mills,500000)
        unbalanced.confirm_repayment(self.db,loan.id,self.refund)
        self.assertEqual(unbalanced.loan_rows(self.db)[0].outstanding_mills,300000)
        self.assertEqual(self.db.balance(),self.base)
        with self.assertRaises(ValueError):
            self.db.edit(self.refund,'2026-08-15','Ammu refund',300000)
        unbalanced.unlink_repayment(self.db,self.refund)
        self.assertEqual(unbalanced.loan_rows(self.db)[0].outstanding_mills,500000)
        self.assertEqual(self.db.balance(),self.base)

    def test_decline_and_sign_check(self):
        unbalanced.register_loan(self.db,self.origin,'Ammu')
        loan=unbalanced.loan_rows(self.db)[0]
        unbalanced.dismiss_suggestion(self.db,loan.id,self.refund)
        self.assertEqual(unbalanced.suggestions(self.db,loan.id),[])
        with self.assertRaises(ValueError):
            unbalanced.confirm_repayment(self.db,loan.id,self.origin)

    def test_borrowed_partial_and_overpay(self):
        origin=self.db.add('2026-09-01','Borrowed from Sarah',300000)
        refund=self.db.add('2026-09-02','Sarah refund',-100000)
        unbalanced.register_loan(self.db,origin,'Sarah')
        loan=next(x for x in unbalanced.loan_rows(self.db) if x.person=='Sarah')
        unbalanced.confirm_repayment(self.db,loan.id,refund)
        self.assertEqual(unbalanced.loan_rows(self.db)[0].outstanding_mills,200000)
        too_large=self.db.add('2026-09-03','Sarah refund',-300000)
        with self.assertRaises(ValueError): unbalanced.confirm_repayment(self.db,loan.id,too_large)
