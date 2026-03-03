# expense_ai/mcp/transaction_tools.py

from expense_ai.database.connection import get_connection
from expense_ai.database.category_repository import CategoryRepository
from expense_ai.database.transaction_repository import TransactionRepository
from expense_ai.engine.expense_engine import ExpenseEngine


def register_transaction_tools(mcp):

    @mcp.tool()
    def add_transaction(
        amount: float,
        type: str,
        category_id: int,
        payment_method: str,
        description: str,
        transaction_date: str,
    ):
        """
        Create a new financial transaction (income or expense).

        Parameters:
        - amount (float): Transaction amount (e.g., 2500.50).
        - type (str): "income" or "expense".
        - category_id (int): ID of category from categories table.
        - payment_method (str): Mode of payment (e.g., "cash", "online", "cheque").
        - description (str): Short note describing the transaction.
        - transaction_date (str): Date in ISO format (YYYY-MM-DD).

        Allowed income categories (id : name) : {
            1 : "Salary",
            2 : "Business",
            3 : "Investment",
            4 : "Rental"
        }

        Allowed expense categories (id : name) : {
            6 : "Housing",
            7 : "Food",
            8 : "Transportation",
            9 : "Utilities",
            10 : "Healthcare",
            11 : "Personal",
            12 : "Entertainment",
            13 : "Education",
            14 : "Investments",
            15 : "Other Expense"
        }

        Example:
        add_transaction(
            amount=1500.0,
            type="expense",
            category_id=3,
            payment_method="upi",
            description="Groceries",
            transaction_date="2025-03-01"
        )

        Returns:
        Structured response containing transaction ID and status.
        """

        conn = get_connection()
        try:
            category_repo = CategoryRepository(conn)
            transaction_repo = TransactionRepository(conn)
            engine = ExpenseEngine(category_repo, transaction_repo)

            data = {
                "amount": amount,
                "type": type,
                "category_id": category_id,
                "payment_method": payment_method,
                "description": description,
                "transaction_date": transaction_date,
            }

            return engine.add_transaction(data)
        finally:
            conn.close()

    @mcp.tool()
    def update_transaction(
        transaction_id: int,
        amount: float,
        type: str,
        category_id: int,
        payment_method: str,
        description: str,
        transaction_date: str,
    ):
        """
        Update an existing transaction.

        Parameters:
        - transaction_id (int): ID of transaction to update.
        - amount (float): Updated amount.
        - type (str): "income" or "expense".
        - category_id (int): Updated category ID.
        - payment_method (str): Updated payment method (cash / online / cheque).
        - description (str): Updated description.
        - transaction_date (str): Updated date (YYYY-MM-DD).

        Allowed income categories (id : name) : {
            1 : "Salary",
            2 : "Business",
            3 : "Investment",
            4 : "Rental"
        }

        Allowed expense categories (id : name) : {
            6 : "Housing",
            7 : "Food",
            8 : "Transportation",
            9 : "Utilities",
            10 : "Healthcare",
            11 : "Personal",
            12 : "Entertainment",
            13 : "Education",
            14 : "Investments",
            15 : "Other Expense"
        }

        Example:
        update_transaction(
            transaction_id=12,
            amount=2000.0,
            type="expense",
            category_id=5,
            payment_method="card",
            description="Updated groceries",
            transaction_date="2025-03-02"
        )

        Returns:
        Structured response confirming update.
        """

        conn = get_connection()
        try:
            category_repo = CategoryRepository(conn)
            transaction_repo = TransactionRepository(conn)
            engine = ExpenseEngine(category_repo, transaction_repo)

            data = {
                "amount": amount,
                "type": type,
                "category_id": category_id,
                "payment_method": payment_method,
                "description": description,
                "transaction_date": transaction_date,
            }

            return engine.update_transaction(transaction_id, data)
        finally:
            conn.close()

    @mcp.tool()
    def delete_transaction(transaction_id: int):
        """
        Soft delete a transaction.

        Parameters:
        - transaction_id (int): ID of transaction to delete.

        Example:
        delete_transaction(transaction_id=15)

        Returns:
        Confirmation of deletion status.
        """

        conn = get_connection()
        try:
            category_repo = CategoryRepository(conn)
            transaction_repo = TransactionRepository(conn)
            engine = ExpenseEngine(category_repo, transaction_repo)

            return engine.delete_transaction(transaction_id)
        finally:
            conn.close()

    @mcp.tool()
    def list_transactions():
        """
        Retrieve all active transactions.

        Parameters:
        None

        Example:
        list_transactions()

        Returns:
        List of transaction records with details.
        """
        
        conn = get_connection()
        try:
            category_repo = CategoryRepository(conn)
            transaction_repo = TransactionRepository(conn)
            engine = ExpenseEngine(category_repo, transaction_repo)

            return engine.list_transactions()
        finally:
            conn.close()