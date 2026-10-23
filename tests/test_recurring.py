import unittest

from glassbalance.database import Ledger
from glassbalance import recurring


class RecurringTests(unittest.TestCase):
    def setUp(self):
        self.db=Ledger()
        self.db.set_opening(1000000,'2026-01-01')

    def tearDown(self): self.db.close()

    def test_template_does_not_change_balance_until_posted(self):
        before=self.db.balance()
        t=recurring.add_template(self.db,'Rent',-900000,2,'Housing')
        self.assertEqual(self.db.balance(),before)
        self.assertEqual(self.db.count(),0)
        tx=recurring.post(self.db,t,'2026-10')
        self.assertEqual(self.db.balance(),before-900000)
        entry=self.db.entries()[0]
        self.assertEqual((entry.date,entry.description,entry.date_status),('2026-10-02','Rent','confirmed'))
        self.assertEqual(self.db.category(tx),'Housing')

    def test_duplicate_post_same_month_refused_other_month_allowed(self):
        t=recurring.add_template(self.db,'Netflix',-15490,15)
        recurring.post(self.db,t,'2026-10')
        with self.assertRaises(ValueError):
            recurring.post(self.db,t,'2026-10')
        recurring.post(self.db,t,'2026-11')
        self.assertEqual(self.db.count(),2)

    def test_duplicate_guard_survives_reopen(self):
        import tempfile
        from pathlib import Path
        with tempfile.TemporaryDirectory() as d:
            path=Path(d)/'ledger.sqlite'
            db=Ledger(path)
            t=recurring.add_template(db,'Gym',-30000,1)
            recurring.post(db,t,'2026-10')
            db.close()
            db=Ledger(path)
            with self.assertRaises(ValueError):
                recurring.post(db,t,'2026-10')
            self.assertEqual(db.count(),1)
            db.close()

    def test_short_month_clamping(self):
        self.assertEqual(recurring.post_date(31,'2026-02'),'2026-02-28')
        self.assertEqual(recurring.post_date(31,'2028-02'),'2028-02-29')
        self.assertEqual(recurring.post_date(31,'2026-04'),'2026-04-30')
        self.assertEqual(recurring.post_date(5,'2026-04'),'2026-04-05')

    def test_removing_template_keeps_posted_transaction(self):
        t=recurring.add_template(self.db,'Salary',2500000,31)
        recurring.post(self.db,t,'2026-10')
        balance=self.db.balance()
        recurring.remove_template(self.db,t)
        self.assertEqual(recurring.templates(self.db),[])
        self.assertEqual((self.db.count(),self.db.balance()),(1,balance))

    def test_deleted_post_can_be_reposted_and_undo_restores_guard(self):
        t=recurring.add_template(self.db,'Phone',-6000,10)
        tx=recurring.post(self.db,t,'2026-10')
        snap=self.db.delete(tx)
        self.assertIsNone(recurring.posted_transaction(self.db,t,'2026-10'))
        self.db.restore_deleted(snap)
        self.assertEqual(recurring.posted_transaction(self.db,t,'2026-10'),tx)
        with self.assertRaises(ValueError):
            recurring.post(self.db,t,'2026-10')

    def test_validation(self):
        for args in (('',-1,1),('Rent',0,1),('Rent',-1,0),('Rent',-1,32)):
            with self.assertRaises(ValueError):
                recurring.add_template(self.db,*args)


if __name__=='__main__': unittest.main()
