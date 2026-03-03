from expense_ai.database.connection import get_connection
from expense_ai.database.transaction_repository import TransactionRepository
from expense_ai.intellitence.summary_service import SummaryService
from expense_ai.intellitence.trend_service import TrendService


def register_analytics_tools(mcp):

    @mcp.tool()
    def monthly_summary(year: int, month: int):
        """
        Generate monthly income, expense, and net summary.

        Parameters:
        - year (int): Target year (e.g., 2025).
        - month (int): Target month (1–12).

        Example:
        monthly_summary(2025, 3)

        Returns:
        Total income, total expense, and net cashflow for the month.
        """
        conn = get_connection()
        try:
            repo = TransactionRepository(conn)
            service = SummaryService(repo)
            return service.monthly_summary(year, month)
        finally:
            conn.close()

    @mcp.tool()
    def category_breakdown(year: int, month: int, transaction_type : str):
        """
        Get category-wise breakdown for income or expense.

        Parameters:
        - year (int): Year.
        - month (int): Month.
        - transaction_type (str): "income" or "expense".

        Example:
        category_breakdown(2025, 3, "expense")

        Returns:
        List of categories with total amounts for the selected month.
        """
        conn = get_connection()
        try:
            repo = TransactionRepository(conn)
            service = SummaryService(repo)
            return service.category_breakdown(year, month, transaction_type)
        finally:
            conn.close()

    @mcp.tool()
    def top_categories(year: int, month: int, transaction_type : str, top_n : int):
        """
        Retrieve top N categories by spending or income.

        Parameters:
        - year (int): Year.
        - month (int): Month.
        - transaction_type (str): "income" or "expense".
        - top_n (int): Number of top categories to return.

        Example:
        top_categories(2025, 3, "expense", 3)

        Returns:
        Top N categories ranked by amount.
        """
        conn = get_connection()
        try:
            repo = TransactionRepository(conn)
            service = SummaryService(repo)
            return service.top_categories(year, month, transaction_type, top_n)
        finally:
            conn.close()

    @mcp.tool()
    def income_vs_expense_comparison(year: int, month: int):
        """
        Compare total income and expense for a specific month.

        Parameters:
        - year (int): Year.
        - month (int): Month.

        Example:
        income_vs_expense_comparison(2025, 3)

        Returns:
        Comparison metrics including surplus or deficit.
        """

        conn = get_connection()
        try:
            repo = TransactionRepository(conn)
            service = SummaryService(repo)
            return service.income_vs_expense_comparison(year, month)
        finally:
            conn.close()

    @mcp.tool()
    def compare_two_months(current_year: int, current_month: int, compare_year: int, compare_month: int):
        """
        Compare financial performance between two months.

        Parameters:
        - current_year (int)
        - current_month (int)
        - compare_year (int)
        - compare_month (int)

        Example:
        compare_two_months(2025, 3, 2025, 2)

        Returns:
        Difference in income, expense, and net cashflow.
        """
        conn = get_connection()
        try:
            repo = TransactionRepository(conn)
            service = TrendService(repo)
            return service.compare_months(current_year, current_month, compare_year, compare_month)
        finally:
            conn.close()

    @mcp.tool()
    def rolling_average(year: int, month: int, window_size : int):
        """
        Calculate rolling average for income and expense.

        Parameters:
        - year (int)
        - month (int)
        - window_size (int): Number of months for smoothing (e.g., 3).

        Example:
        rolling_average(2025, 3, 3)

        Returns:
        Smoothed financial trend values.
        """
        conn = get_connection()
        try:
            repo = TransactionRepository(conn)
            service = TrendService(repo)
            return service.rolling_average(year, month, window_size)
        finally:
            conn.close()

    @mcp.tool()
    def expense_slope(year: int, month: int, last_n_months : int):
        """
        Compute trend slope of expenses over recent months.

        Parameters:
        - year (int)
        - month (int)
        - last_n_months (int): Number of months to analyze.

        Example:
        expense_slope(2025, 3, 6)

        Returns:
        Slope value indicating upward or downward expense trend.
        """
        conn = get_connection()
        try:
            repo = TransactionRepository(conn)
            service = TrendService(repo)
            return service.expense_slope(year, month, last_n_months)
        finally:
            conn.close()

    @mcp.tool()
    def income_slope(year: int, month: int, last_n_months : int):
        """
        Compute trend slope of income over recent months.

        Parameters:
        - year (int)
        - month (int)
        - last_n_months (int)

        Example:
        income_slope(2025, 3, 6)

        Returns:
        Slope value indicating income growth or decline.
        """
        conn = get_connection()
        try:
            repo = TransactionRepository(conn)
            service = TrendService(repo)
            return service.income_slope(year, month, last_n_months)
        finally:
            conn.close()

    @mcp.tool()
    def net_cashflow_slope(year: int, month: int, last_n_months : int):
        """
        Compute trend slope of net cashflow (income - expense).

        Parameters:
        - year (int)
        - month (int)
        - last_n_months (int)

        Example:
        net_cashflow_slope(2025, 3, 6)

        Returns:
        Slope indicating financial sustainability trend.
        """
        conn = get_connection()
        try:
            repo = TransactionRepository(conn)
            service = TrendService(repo)
            return service.net_cashflow_slope(year, month, last_n_months)
        finally:
            conn.close()

    @mcp.tool()
    def expense_volatility(year: int, month: int, last_n_months : int):
        """
        Measure volatility (standard deviation) of expenses.

        Parameters:
        - year (int)
        - month (int)
        - last_n_months (int)

        Example:
        expense_volatility(2025, 3, 6)

        Returns:
        Volatility score representing spending stability.
        """
        
        conn = get_connection()
        try:
            repo = TransactionRepository(conn)
            service = TrendService(repo)
            return service.expense_volatility(year, month, last_n_months)
        finally:
            conn.close()
