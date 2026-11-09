import unittest
from datetime import date

from glassbalance.database import Ledger
from glassbalance import categories, periods


class PresetTests(unittest.TestCase):
    def test_presets(self):
        t = date(2026, 3, 15)
        self.assertEqual(periods.preset_range("This month", t), (date(2026, 3, 1), t))
        self.assertEqual(periods.preset_range("Last month", t), (date(2026, 2, 1), date(2026, 2, 28)))
        self.assertEqual(periods.preset_range("Last 3 months", t), (date(2026, 1, 1), t))
        self.assertEqual(periods.preset_range("This year", t), (date(2026, 1, 1), t))
        self.assertEqual(periods.preset_range("Last year", t), (date(2025, 1, 1), date(2025, 12, 31)))
        self.assertEqual(periods.preset_range("All time", t), (None, None))

    def test_year_and_leap_boundaries(self):
        jan = date(2026, 1, 10)
        self.assertEqual(periods.preset_range("Last month", jan), (date(2025, 12, 1), date(2025, 12, 31)))
        self.assertEqual(periods.preset_range("Last 3 months", jan)[0], date(2025, 11, 1))
        self.assertEqual(periods.preset_range("Last month", date(2028, 3, 5))[1], date(2028, 2, 29))

    def test_normalize_and_describe(self):
        a, b = date(2026, 5, 1), date(2026, 4, 1)
        self.assertEqual(periods.normalize(a, b), (b, a))
        self.assertEqual(periods.describe(None, None), "All transactions")
        self.assertEqual(periods.describe(date(2026, 10, 1), date(2026, 10, 31)), "Oct 1 – Oct 31, 2026")
        self.assertEqual(periods.describe(date(2025, 12, 1), date(2026, 1, 5)), "Dec 1, 2025 – Jan 5, 2026")


class TotalsTests(unittest.TestCase):
    def setUp(self):
        self.db = Ledger()
        self.db.set_opening(1_000_000, "2026-01-01")     # opening is never income
        self.db.add("2026-01-31", "Salary", 3_000_000)
        self.db.add("2026-02-01", "Rent", -1_200_000)
        self.db.add("2026-02-14", "Dinner", -85_500)
        self.db.add("2026-03-01", "Refund", 20_000)
        self.db.set_category(self.db.entries()[1].id, "Housing")

    def tearDown(self):
        self.db.close()

    def test_inclusive_range_and_all_time(self):
        feb = periods.totals(self.db.entries(), date(2026, 2, 1), date(2026, 2, 28))
        self.assertEqual(feb, {"in": 0, "out": 1_285_500, "net": -1_285_500, "count": 2})
        edge = periods.totals(self.db.entries(), date(2026, 1, 31), date(2026, 2, 1))
        self.assertEqual(edge["count"], 2)
        everything = periods.totals(self.db.entries(), None, None)
        self.assertEqual(everything["net"], self.db.balance() - self.db.opening()[0])

    def test_category_summary_respects_range(self):
        rows = {r["category"]: r for r in categories.summary(self.db.conn, date(2026, 2, 1), "2026-02-28")}
        self.assertEqual(rows["Housing"]["expense"], 1_200_000)
        self.assertEqual(rows["Uncategorized"]["expense"], 85_500)
        self.assertEqual(sum(r["count"] for r in rows.values()), 2)
        self.assertEqual(len(categories.summary(self.db.conn)), 2)


if __name__ == "__main__":
    unittest.main()


class CategoryDrillDownTests(unittest.TestCase):
    def test_transactions_in_matches_summary(self):
        db = Ledger()
        db.set_opening(0, "2026-01-01")
        a = db.add("2026-02-01", "Rent", -1_200_000)
        db.add("2026-02-05", "Kroger", -50_000)
        c = db.add("2026-03-01", "Rent", -1_200_000)
        db.set_category(a, "Housing"); db.set_category(c, "Housing")
        rows = categories.transactions_in(db.conn, "Housing")
        self.assertEqual([r["id"] for r in rows], [c, a])                 # newest first
        self.assertEqual([r["id"] for r in categories.transactions_in(db.conn, "Housing", date(2026, 2, 1), "2026-02-28")], [a])
        self.assertEqual(len(categories.transactions_in(db.conn, "Uncategorized")), 1)
        for row in categories.summary(db.conn, date(2026, 2, 1), date(2026, 3, 31)):
            listed = categories.transactions_in(db.conn, row["category"], date(2026, 2, 1), date(2026, 3, 31))
            self.assertEqual(len(listed), row["count"])
            self.assertEqual(sum(r["mills"] for r in listed), row["income"] - row["expense"])
        db.close()
