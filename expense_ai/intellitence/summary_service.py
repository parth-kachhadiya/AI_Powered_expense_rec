import calendar
from expense_ai.engine.exceptions import ExpenseEngineError


class SummaryService:

    def __init__(self, transaction_repo):
        self.transaction_repo = transaction_repo

    def monthly_summary(self, year: int, month: int):
        try:
            if month < 1 or month > 12:
                raise ExpenseEngineError(
                    "INVALID_MONTH",
                    "Month must be between 1 and 12."
                )

            last_day = calendar.monthrange(year, month)[1]

            start_date = f"{year}-{month:02d}-01"
            end_date = f"{year}-{month:02d}-{last_day}"

            totals = self.transaction_repo.get_monthly_income_expense(
                start_date,
                end_date
            )

            total_income = totals.get("income", 0) or 0
            total_expense = totals.get("expense", 0) or 0

            net_cashflow = total_income - total_expense

            return {
                "status": "success",
                "metric": "monthly_summary",
                "data": {
                    "year": year,
                    "month": month,
                    "total_income": total_income,
                    "total_expense": total_expense,
                    "net_cashflow": net_cashflow
                }
            }

        except ExpenseEngineError as e:
            return {
                "status": "error",
                "code": e.code,
                "message": e.message
            }

        except Exception as e:
            return {
                "status": "error",
                "code": "INTERNAL_ERROR",
                "message": str(e)
            }

    def category_breakdown(self, year: int, month: int, transaction_type: str):
        try:
            if transaction_type not in {"income", "expense"}:
                raise ExpenseEngineError(
                    "INVALID_TYPE",
                    "Transaction type must be 'income' or 'expense'."
                )

            last_day = calendar.monthrange(year, month)[1]

            start_date = f"{year}-{month:02d}-01"
            end_date = f"{year}-{month:02d}-{last_day}"

            categories = self.transaction_repo.get_category_totals(
                start_date,
                end_date,
                transaction_type
            )

            total_amount = sum(cat["total"] for cat in categories)

            # Avoid division by zero
            if total_amount == 0:
                return {
                    "status": "success",
                    "metric": "category_breakdown",
                    "data": {
                        "year": year,
                        "month": month,
                        "transaction_type": transaction_type,
                        "categories": []
                    }
                }

            for cat in categories:
                percentage = (cat["total"] / total_amount) * 100
                cat["percentage"] = round(percentage, 2)

            return {
                "status": "success",
                "metric": "category_breakdown",
                "data": {
                    "year": year,
                    "month": month,
                    "transaction_type": transaction_type,
                    "categories": categories
                }
            }

        except ExpenseEngineError as e:
            return {
                "status": "error",
                "code": e.code,
                "message": e.message
            }

        except Exception as e:
            return {
                "status": "error",
                "code": "INTERNAL_ERROR",
                "message": str(e)
            }

    def top_categories(self, year: int, month: int, transaction_type: str, limit: int = 3):
        try:
            breakdown = self.category_breakdown(year, month, transaction_type)

            if breakdown["status"] != "success":
                return breakdown

            categories = breakdown["data"]["categories"]

            top = categories[:limit]

            return {
                "status": "success",
                "metric": "top_categories",
                "data": {
                    "year": year,
                    "month": month,
                    "transaction_type": transaction_type,
                    "top_categories": top
                }
            }

        except Exception as e:
            return {
                "status": "error",
                "code": "INTERNAL_ERROR",
                "message": str(e)
            }

    def income_vs_expense_comparison(self, year: int, month: int):
        try:
            summary = self.monthly_summary(year, month)

            if summary["status"] != "success":
                return summary

            data = summary["data"]

            income = data["total_income"]
            expense = data["total_expense"]

            if income == 0:
                expense_ratio = 0
            else:
                expense_ratio = round(expense / income, 2)

            savings = income - expense

            return {
                "status": "success",
                "metric": "income_vs_expense_comparison",
                "data": {
                    "year": year,
                    "month": month,
                    "total_income": income,
                    "total_expense": expense,
                    "savings": savings,
                    "expense_ratio": expense_ratio
                }
            }

        except Exception as e:
            return {
                "status": "error",
                "code": "INTERNAL_ERROR",
                "message": str(e)
            }