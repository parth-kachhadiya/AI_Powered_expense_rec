import calendar
from expense_ai.engine.exceptions import ExpenseEngineError


class TrendService:

    def __init__(self, transaction_repo):
        self.transaction_repo = transaction_repo

    # ==========================================================
    # PUBLIC METHOD
    # ==========================================================
    def compare_months(
        self,
        current_year: int,
        current_month: int,
        compare_year: int = None,
        compare_month: int = None
    ):
        try:
            # Validate current month
            if current_month < 1 or current_month > 12:
                raise ExpenseEngineError("INVALID_MONTH", "Month must be 1–12.")

            # If no compare provided → default previous month
            if compare_year is None or compare_month is None:
                compare_year, compare_month = self._get_previous_month(
                    current_year,
                    current_month
                )

            # Ensure compare month is strictly earlier
            if not self._is_past_month(
                current_year,
                current_month,
                compare_year,
                compare_month
            ):
                raise ExpenseEngineError(
                    "INVALID_COMPARISON",
                    "Comparison month must be earlier than current month."
                )

            # Get date ranges
            curr_start, curr_end = self._get_month_range(current_year, current_month)
            comp_start, comp_end = self._get_month_range(compare_year, compare_month)

            # Fetch totals
            curr_totals = self.transaction_repo.get_monthly_income_expense(curr_start, curr_end)
            comp_totals = self.transaction_repo.get_monthly_income_expense(comp_start, comp_end)

            # Compute growth for totals
            income_growth = self._compute_growth(
                curr_totals.get("income", 0),
                comp_totals.get("income", 0)
            )

            expense_growth = self._compute_growth(
                curr_totals.get("expense", 0),
                comp_totals.get("expense", 0)
            )

            curr_net = curr_totals.get("income", 0) - curr_totals.get("expense", 0)
            comp_net = comp_totals.get("income", 0) - comp_totals.get("expense", 0)

            net_growth = self._compute_growth(curr_net, comp_net)

            # Category-wise growth
            category_growth = {
                "income": self._compute_category_growth(
                    curr_start, curr_end,
                    comp_start, comp_end,
                    "income"
                ),
                "expense": self._compute_category_growth(
                    curr_start, curr_end,
                    comp_start, comp_end,
                    "expense"
                )
            }

            return {
                "status": "success",
                "metric": "month_comparison",
                "data": {
                    "current": {"year": current_year, "month": current_month},
                    "compare": {"year": compare_year, "month": compare_month},
                    "income_growth": income_growth,
                    "expense_growth": expense_growth,
                    "net_cashflow_growth": net_growth,
                    "category_growth": category_growth
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

    # ==========================================================
    # INTERNAL HELPERS
    # ==========================================================
    def _compute_growth(self, current, previous):

        difference = current - previous

        if previous > 0 and current > 0:
            growth_percentage = round(((current - previous) / previous) * 100, 2)
            status = "NORMAL"

        elif previous == 0 and current > 0:
            growth_percentage = None
            status = "ACTIVATED"

        elif previous > 0 and current == 0:
            growth_percentage = -100.0
            status = "DEACTIVATED"

        else:
            growth_percentage = 0
            status = "NO_ACTIVITY"

        return {
            "previous_value": previous,
            "current_value": current,
            "difference": difference,
            "growth_percentage": growth_percentage,
            "growth_status": status
        }

    def _compute_category_growth(
        self,
        curr_start, curr_end,
        comp_start, comp_end,
        transaction_type
    ):
        curr_categories = self.transaction_repo.get_category_totals(
            curr_start, curr_end, transaction_type
        )

        comp_categories = self.transaction_repo.get_category_totals(
            comp_start, comp_end, transaction_type
        )

        curr_map = {c["category_id"]: c for c in curr_categories}
        comp_map = {c["category_id"]: c for c in comp_categories}

        all_ids = set(curr_map.keys()) | set(comp_map.keys())

        results = []

        for cid in all_ids:
            curr_val = curr_map.get(cid, {}).get("total", 0)
            comp_val = comp_map.get(cid, {}).get("total", 0)

            if curr_val == 0 and comp_val == 0:
                continue  # exclude no activity

            growth = self._compute_growth(curr_val, comp_val)

            results.append({
                "category_id": cid,
                "category_name": (
                    curr_map.get(cid, {}).get("category_name") or
                    comp_map.get(cid, {}).get("category_name")
                ),
                **growth
            })

        # Sort by absolute growth impact
        def sort_key(item):
            if item["growth_status"] == "ACTIVATED":
                return float("inf")
            return abs(item["growth_percentage"] or 0)

        results.sort(key=sort_key, reverse=True)

        return results

    def _get_previous_month(self, year, month):
        if month == 1:
            return year - 1, 12
        return year, month - 1

    def _is_past_month(self, curr_y, curr_m, comp_y, comp_m):
        return (comp_y * 12 + comp_m) < (curr_y * 12 + curr_m)

    def _get_month_range(self, year, month):
        last_day = calendar.monthrange(year, month)[1]
        start = f"{year}-{month:02d}-01"
        end = f"{year}-{month:02d}-{last_day}"
        return start, end

    def rolling_average(self, current_year: int, current_month: int, window: int = 3):
        try:
            if window <= 0:
                raise ExpenseEngineError("INVALID_WINDOW", "Window must be positive.")

            # Calculate start month (window size back)
            total_month_index = current_year * 12 + current_month
            start_index = total_month_index - (window - 1)

            start_year = start_index // 12
            start_month = start_index % 12

            if start_month == 0:
                start_month = 12
                start_year -= 1

            start_date, _ = self._get_month_range(start_year, start_month)
            _, end_date = self._get_month_range(current_year, current_month)

            monthly_data = self.transaction_repo.get_monthly_totals_for_range(
                start_date,
                end_date
            )

            income_values = []
            expense_values = []
            net_values = []

            for ym in sorted(monthly_data.keys()):
                income = monthly_data[ym].get("income", 0)
                expense = monthly_data[ym].get("expense", 0)
                net = income - expense

                income_values.append(income)
                expense_values.append(expense)
                net_values.append(net)

            if not income_values:
                return {
                    "status": "success",
                    "metric": "rolling_average",
                    "data": {}
                }

            income_sma = round(sum(income_values) / len(income_values), 2)
            expense_sma = round(sum(expense_values) / len(expense_values), 2)
            net_sma = round(sum(net_values) / len(net_values), 2)

            return {
                "status": "success",
                "metric": "rolling_average",
                "data": {
                    "window": window,
                    "income_sma": income_sma,
                    "expense_sma": expense_sma,
                    "net_sma": net_sma
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

    def _calculate_slope(self, values):
        n = len(values)

        if n < 2:
            return 0

        x_values = list(range(1, n + 1))
        y_values = values

        sum_x = sum(x_values)
        sum_y = sum(y_values)
        sum_xy = sum(x * y for x, y in zip(x_values, y_values))
        sum_x2 = sum(x * x for x in x_values)

        numerator = (n * sum_xy) - (sum_x * sum_y)
        denominator = (n * sum_x2) - (sum_x ** 2)

        if denominator == 0:
            return 0

        slope = numerator / denominator
        return round(slope, 2)

    def expense_slope(self, current_year: int, current_month: int, last_n_months: int = 6):
        try:
            if last_n_months < 2:
                raise ExpenseEngineError(
                    "INVALID_RANGE",
                    "At least 2 months required for slope calculation."
                )

            total_month_index = current_year * 12 + current_month
            start_index = total_month_index - (last_n_months - 1)

            start_year = start_index // 12
            start_month = start_index % 12

            if start_month == 0:
                start_month = 12
                start_year -= 1

            start_date, _ = self._get_month_range(start_year, start_month)
            _, end_date = self._get_month_range(current_year, current_month)

            monthly_data = self.transaction_repo.get_monthly_totals_for_range(
                start_date,
                end_date
            )

            expense_values = []

            for ym in sorted(monthly_data.keys()):
                expense_values.append(
                    monthly_data[ym].get("expense", 0)
                )

            slope = self._calculate_slope(expense_values)

            if slope > 0:
                direction = "UPWARD"
            elif slope < 0:
                direction = "DOWNWARD"
            else:
                direction = "STABLE"

            return {
                "status": "success",
                "metric": "expense_trend_slope",
                "data": {
                    "months_analyzed": last_n_months,
                    "slope": slope,
                    "trend_direction": direction
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

    def income_slope(self, current_year: int, current_month: int, last_n_months: int = 6):
        try:
            if last_n_months < 2:
                raise ExpenseEngineError(
                    "INVALID_RANGE",
                    "At least 2 months required for slope calculation."
                )

            total_month_index = current_year * 12 + current_month
            start_index = total_month_index - (last_n_months - 1)

            start_year = start_index // 12
            start_month = start_index % 12

            if start_month == 0:
                start_month = 12
                start_year -= 1

            start_date, _ = self._get_month_range(start_year, start_month)
            _, end_date = self._get_month_range(current_year, current_month)

            monthly_data = self.transaction_repo.get_monthly_totals_for_range(
                start_date,
                end_date
            )

            income_values = []

            for ym in sorted(monthly_data.keys()):
                income_values.append(
                    monthly_data[ym].get("income", 0)
                )

            slope = self._calculate_slope(income_values)

            if slope > 0:
                direction = "UPWARD"
            elif slope < 0:
                direction = "DOWNWARD"
            else:
                direction = "STABLE"

            return {
                "status": "success",
                "metric": "income_trend_slope",
                "data": {
                    "months_analyzed": last_n_months,
                    "slope": slope,
                    "trend_direction": direction
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

    def net_cashflow_slope(self, current_year: int, current_month: int, last_n_months: int = 6):
        try:
            if last_n_months < 2:
                raise ExpenseEngineError(
                    "INVALID_RANGE",
                    "At least 2 months required for slope calculation."
                )

            total_month_index = current_year * 12 + current_month
            start_index = total_month_index - (last_n_months - 1)

            start_year = start_index // 12
            start_month = start_index % 12

            if start_month == 0:
                start_month = 12
                start_year -= 1

            start_date, _ = self._get_month_range(start_year, start_month)
            _, end_date = self._get_month_range(current_year, current_month)

            monthly_data = self.transaction_repo.get_monthly_totals_for_range(
                start_date,
                end_date
            )

            net_values = []

            for ym in sorted(monthly_data.keys()):
                income = monthly_data[ym].get("income", 0)
                expense = monthly_data[ym].get("expense", 0)
                net_values.append(income - expense)

            slope = self._calculate_slope(net_values)

            if slope > 0:
                direction = "UPWARD"
            elif slope < 0:
                direction = "DOWNWARD"
            else:
                direction = "STABLE"

            return {
                "status": "success",
                "metric": "net_cashflow_trend_slope",
                "data": {
                    "months_analyzed": last_n_months,
                    "slope": slope,
                    "trend_direction": direction
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

    def _calculate_std_dev(self, values):
        n = len(values)
        if n == 0:
            return 0

        mean = sum(values) / n
        variance = sum((x - mean) ** 2 for x in values) / n
        return round(variance ** 0.5, 2)

    def expense_volatility(self, current_year: int, current_month: int, last_n_months: int = 6):
        try:
            total_month_index = current_year * 12 + current_month
            start_index = total_month_index - (last_n_months - 1)

            start_year = start_index // 12
            start_month = start_index % 12

            if start_month == 0:
                start_month = 12
                start_year -= 1

            start_date, _ = self._get_month_range(start_year, start_month)
            _, end_date = self._get_month_range(current_year, current_month)

            monthly_data = self.transaction_repo.get_monthly_totals_for_range(
                start_date, end_date
            )

            expense_values = [
                monthly_data[ym].get("expense", 0)
                for ym in sorted(monthly_data.keys())
            ]

            std_dev = self._calculate_std_dev(expense_values)
            mean = round(sum(expense_values) / len(expense_values), 2) if expense_values else 0

            volatility_ratio = round(std_dev / mean, 2) if mean != 0 else 0

            return {
                "status": "success",
                "metric": "expense_volatility",
                "data": {
                    "mean": mean,
                    "std_dev": std_dev,
                    "volatility_ratio": volatility_ratio
                }
            }

        except Exception as e:
            return {
                "status": "error",
                "code": "INTERNAL_ERROR",
                "message": str(e)
            }