from __future__ import annotations

from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import Dict, List
import json


@dataclass
class Transaction:
    transaction_type: str
    category: str
    amount: float
    description: str
    created_at: str

    def to_dict(self) -> dict:
        return asdict(self)


class AccountingSystem:
    """Simple accounting system that tracks income and expenses."""

    def __init__(self, storage_path: str = "transactions.json") -> None:
        self.storage_path = Path(storage_path)
        self.transactions: List[Transaction] = []
        self._load()

    def add_income(self, amount: float, category: str, description: str = "") -> Transaction:
        return self._add_transaction("income", amount, category, description)

    def add_expense(self, amount: float, category: str, description: str = "") -> Transaction:
        return self._add_transaction("expense", amount, category, description)

    def _add_transaction(
        self,
        transaction_type: str,
        amount: float,
        category: str,
        description: str,
    ) -> Transaction:
        if amount <= 0:
            raise ValueError("Amount must be greater than zero.")
        if transaction_type not in {"income", "expense"}:
            raise ValueError("transaction_type must be either 'income' or 'expense'.")

        transaction = Transaction(
            transaction_type=transaction_type,
            category=category.strip() or "general",
            amount=round(float(amount), 2),
            description=description.strip(),
            created_at=datetime.now().isoformat(timespec="seconds"),
        )
        self.transactions.append(transaction)
        self._save()
        return transaction

    def list_transactions(self) -> List[Transaction]:
        return list(self.transactions)

    def totals(self) -> Dict[str, float]:
        income = sum(t.amount for t in self.transactions if t.transaction_type == "income")
        expenses = sum(t.amount for t in self.transactions if t.transaction_type == "expense")
        return {
            "income": round(income, 2),
            "expenses": round(expenses, 2),
            "balance": round(income - expenses, 2),
        }

    def totals_by_category(self) -> Dict[str, Dict[str, float]]:
        summary: Dict[str, Dict[str, float]] = {}
        for transaction in self.transactions:
            category = transaction.category
            if category not in summary:
                summary[category] = {"income": 0.0, "expense": 0.0}
            summary[category][transaction.transaction_type] += transaction.amount

        for category_totals in summary.values():
            category_totals["income"] = round(category_totals["income"], 2)
            category_totals["expense"] = round(category_totals["expense"], 2)
        return summary

    def _load(self) -> None:
        if not self.storage_path.exists():
            return

        raw = json.loads(self.storage_path.read_text(encoding="utf-8"))
        self.transactions = [Transaction(**item) for item in raw]

    def _save(self) -> None:
        payload = [transaction.to_dict() for transaction in self.transactions]
        self.storage_path.write_text(
            json.dumps(payload, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )


def _print_transactions(transactions: List[Transaction]) -> None:
    if not transactions:
        print("No transactions yet.")
        return

    print("\nTransactions:")
    for index, transaction in enumerate(transactions, start=1):
        print(
            f"{index}. [{transaction.created_at}] "
            f"{transaction.transaction_type.upper()} - "
            f"{transaction.category}: {transaction.amount:.2f} "
            f"({transaction.description or 'no description'})"
        )


def run_cli() -> None:
    system = AccountingSystem()

    menu = """
=== Simple Accounting System ===
1) Add income
2) Add expense
3) Show transactions
4) Show totals
5) Show totals by category
0) Exit
Choose: """

    while True:
        choice = input(menu).strip()

        if choice == "0":
            print("Goodbye.")
            break
        if choice in {"1", "2"}:
            transaction_type = "income" if choice == "1" else "expense"
            category = input("Category: ").strip()
            amount_text = input("Amount: ").strip()
            description = input("Description (optional): ").strip()

            try:
                amount = float(amount_text)
                if transaction_type == "income":
                    system.add_income(amount, category, description)
                else:
                    system.add_expense(amount, category, description)
                print("Transaction added successfully.\n")
            except ValueError as error:
                print(f"Error: {error}\n")
        elif choice == "3":
            _print_transactions(system.list_transactions())
            print()
        elif choice == "4":
            totals = system.totals()
            print(
                f"Income: {totals['income']:.2f} | "
                f"Expenses: {totals['expenses']:.2f} | "
                f"Balance: {totals['balance']:.2f}\n"
            )
        elif choice == "5":
            by_category = system.totals_by_category()
            if not by_category:
                print("No transactions yet.\n")
                continue
            print("\nCategory Summary:")
            for category, totals in by_category.items():
                print(
                    f"- {category}: income={totals['income']:.2f}, "
                    f"expense={totals['expense']:.2f}"
                )
            print()
        else:
            print("Invalid choice. Try again.\n")


if __name__ == "__main__":
    run_cli()
