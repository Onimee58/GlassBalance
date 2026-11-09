import tempfile
import unittest
from pathlib import Path

from glassbalance.database import Ledger
from glassbalance.importer import load_import
from glassbalance import categories


class CategoryTests(unittest.TestCase):
    def setUp(self):
        self.db=Ledger()
        self.db.set_opening(100000,'2026-09-30')
        self.food=self.db.add('2026-10-01','Walmart',-45900)
        self.pay=self.db.add('2026-10-02','Salary',2500000)
        self.rent=self.db.add('2026-10-03','Rent',-900000)

    def tearDown(self): self.db.close()

    def test_category_never_changes_balance_and_defaults_to_uncategorized(self):
        before=(self.db.balance(),[e.running_mills for e in self.db.entries()])
        self.assertEqual(self.db.category(self.food),'')
        self.assertEqual(self.db.set_category(self.food,'  Groceries  '),'Groceries')
        self.db.set_category(self.rent,'Housing')
        self.assertEqual((self.db.balance(),[e.running_mills for e in self.db.entries()]),before)
        self.assertEqual(self.db.set_category(self.food,'Uncategorized'),'')
        self.assertEqual(self.db.category(self.food),'')

    def test_case_variants_merge_and_length_limit(self):
        self.db.set_category(self.food,'Groceries')
        self.assertEqual(self.db.set_category(self.rent,'groceries'),'Groceries')
        self.assertEqual(categories.names(self.db.conn),['Groceries'])
        with self.assertRaises(ValueError):
            self.db.set_category(self.food,'x'*61)

    def test_summary_reconciles_with_ledger(self):
        self.db.set_category(self.food,'Groceries')
        self.db.set_category(self.pay,'Income')
        summary={r['category']:r for r in categories.summary(self.db.conn)}
        self.assertEqual(summary['Groceries']['expense'],45900)
        self.assertEqual(summary['Uncategorized']['expense'],900000)
        self.assertEqual(summary['Income']['income'],2500000)
        total=sum(r['income']-r['expense'] for r in summary.values())
        self.assertEqual(total,self.db.balance()-self.db.opening()[0])
        self.assertEqual(sum(r['count'] for r in summary.values()),self.db.count())

    def test_category_cascades_with_transaction_delete(self):
        self.db.set_category(self.food,'Groceries')
        self.db.delete(self.food)
        self.assertNotIn(self.food,categories.mapping(self.db.conn))

    def test_export_import_roundtrip_keeps_categories(self):
        self.db.set_category(self.food,'Groceries')
        self.db.set_category(self.rent,'Housing')
        with tempfile.TemporaryDirectory() as d:
            for name in ('x.csv','x.xlsx'):
                path=Path(d)/name
                (self.db.export_csv if name.endswith('csv') else self.db.export_xlsx)(path)
                other=Ledger()
                other.import_data(load_import(path))
                got={e.description:other.category(e.id) for e in other.entries()}
                self.assertEqual(got,{'Walmart':'Groceries','Salary':'','Rent':'Housing'})
                self.assertEqual(other.balance(),self.db.balance())
                other.close()


if __name__=='__main__': unittest.main()


class CategoryReimportTests(unittest.TestCase):
    """Export → add categories in a spreadsheet → import back into the SAME ledger."""
    def test_reimport_updates_categories_without_touching_money(self):
        import csv
        db=Ledger()
        db.set_opening(100000,'2026-09-30')
        a=db.add('2026-10-01','Walmart',-45900)
        b=db.add('2026-10-02','Salary',2500000)
        c=db.add('2026-10-03','Rent',-900000)
        db.set_category(c,'Housing')
        before=(db.balance(),[(e.id,e.date,e.mills,e.running_mills) for e in db.entries()])
        with tempfile.TemporaryDirectory() as d:
            path=Path(d)/'export.csv'
            db.export_csv(path)
            rows=list(csv.DictReader(open(path,encoding='utf-8-sig')))
            for r in rows:
                r['Category']={'Walmart':'groceries','Salary':'Income','Rent':''}.get(r['Description'],r['Category'])
            with open(path,'w',newline='',encoding='utf-8-sig') as f:
                w=csv.DictWriter(f,fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
            data=load_import(path)
            changes=db.category_changes(data)
            self.assertEqual(sorted((i,n) for i,_o,n in changes),[(a,'groceries'),(b,'Income')])
            self.assertEqual(db.import_data(data),(0,3))
            self.assertEqual(db.apply_category_changes(changes),2)
        self.assertEqual((db.category(a),db.category(b),db.category(c)),('groceries','Income','Housing'))
        self.assertEqual((db.balance(),[(e.id,e.date,e.mills,e.running_mills) for e in db.entries()]),before)
        db.close()
