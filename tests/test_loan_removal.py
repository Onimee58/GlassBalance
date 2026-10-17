import unittest
from glassbalance.database import Ledger
from glassbalance import unbalanced

class LoanRemovalTests(unittest.TestCase):
    def test_removing_tracking_keeps_ledger_unchanged(self):
        ledger=Ledger(':memory:')
        unbalanced.install(ledger)
        a=ledger.add('2026-10-01','Loaned Alex',-120000,'confirmed')
        b=ledger.add('2026-10-02','Alex refund',30000,'confirmed')
        loans=unbalanced.loan_rows(ledger)
        unbalanced.register_loan(ledger,a,'Alex')
        loan=unbalanced.loan_rows(ledger)[0]
        unbalanced.confirm_repayment(ledger,loan.id,b)
        before=(ledger.balance(),len(ledger.entries()))
        unbalanced.remove_loan(ledger,loan.id)
        self.assertEqual((ledger.balance(),len(ledger.entries())),before)
        self.assertEqual(unbalanced.loan_rows(ledger),[])
        self.assertEqual(len(ledger.entries()),2)

if __name__=='__main__': unittest.main()
