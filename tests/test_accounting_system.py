import tempfile
import unittest
from pathlib import Path

from accounting_system import AccountingSystem


class AccountingSystemTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp_dir = tempfile.TemporaryDirectory()
        self.storage = Path(self.tmp_dir.name) / "test_transactions.json"
        self.system = AccountingSystem(str(self.storage))

    def tearDown(self) -> None:
        self.tmp_dir.cleanup()

    def test_add_income_and_expense_and_totals(self) -> None:
        self.system.add_income(1000, "salary", "monthly salary")
        self.system.add_expense(250.75, "rent", "home rent")

        totals = self.system.totals()

        self.assertEqual(totals["income"], 1000)
        self.assertEqual(totals["expenses"], 250.75)
        self.assertEqual(totals["balance"], 749.25)

    def test_totals_by_category(self) -> None:
        self.system.add_income(1000, "salary")
        self.system.add_income(200, "freelance")
        self.system.add_expense(50, "freelance")

        result = self.system.totals_by_category()

        self.assertEqual(result["salary"]["income"], 1000)
        self.assertEqual(result["salary"]["expense"], 0)
        self.assertEqual(result["freelance"]["income"], 200)
        self.assertEqual(result["freelance"]["expense"], 50)

    def test_reject_non_positive_amount(self) -> None:
        with self.assertRaises(ValueError):
            self.system.add_income(0, "salary")

        with self.assertRaises(ValueError):
            self.system.add_expense(-5, "food")

    def test_data_persists_to_file(self) -> None:
        self.system.add_income(300, "sales")

        fresh_system = AccountingSystem(str(self.storage))
        transactions = fresh_system.list_transactions()

        self.assertEqual(len(transactions), 1)
        self.assertEqual(transactions[0].amount, 300)
        self.assertEqual(transactions[0].category, "sales")


if __name__ == "__main__":
    unittest.main()
