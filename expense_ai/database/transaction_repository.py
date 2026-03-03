class TransactionRepository:
    """
    TransactionRepository

    Core data manipulation layer for financial events.

    Responsibilities:
    - Create, update, and soft-delete transactions
    - Validate input data
    - Enforce data integrity rules

    This layer operates strictly on event-level data.
    It does not perform aggregation or forecasting.
    """

    def __init__(self, connection):
        self.conn = connection

    def insert(self, data):
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO transactions
            (amount, type, category_id, payment_method, description, transaction_date)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            data["amount"],
            data["type"],
            data["category_id"],
            data["payment_method"],
            data.get("description"),
            data["transaction_date"],
        ))

        self.conn.commit()
        return cursor.lastrowid

    def get_by_id(self, transaction_id):
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT * FROM transactions
            WHERE id = ? AND is_deleted = 0
        """, (transaction_id,))
        return cursor.fetchone()

    def update(self, transaction_id, data):
        cursor = self.conn.cursor()
        cursor.execute("""
            UPDATE transactions
            SET amount = ?,
                type = ?,
                category_id = ?,
                payment_method = ?,
                description = ?,
                transaction_date = ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ? AND is_deleted = 0
        """, (
            data["amount"],
            data["type"],
            data["category_id"],
            data["payment_method"],
            data.get("description"),
            data["transaction_date"],
            transaction_id,
        ))

        self.conn.commit()
        return cursor.rowcount

    def soft_delete(self, transaction_id):
        cursor = self.conn.cursor()
        cursor.execute("""
            UPDATE transactions
            SET is_deleted = 1,
                deleted_at = CURRENT_TIMESTAMP
            WHERE id = ? AND is_deleted = 0
        """, (transaction_id,))

        self.conn.commit()
        return cursor.rowcount

    def list_transactions(
        self,
        start_date=None,
        end_date=None,
        transaction_type=None,
        category_id=None,
    ):
        cursor = self.conn.cursor()

        query = """
            SELECT *
            FROM transactions
            WHERE is_deleted = 0
        """

        params = []

        if start_date:
            query += " AND transaction_date >= ?"
            params.append(start_date)

        if end_date:
            query += " AND transaction_date <= ?"
            params.append(end_date)

        if transaction_type:
            query += " AND type = ?"
            params.append(transaction_type)

        if category_id:
            query += " AND category_id = ?"
            params.append(category_id)

        query += " ORDER BY transaction_date DESC"

        cursor.execute(query, params)

        return cursor.fetchall()

    def get_monthly_income_expense(self, start_date, end_date):
        cursor = self.conn.cursor()

        cursor.execute("""
            SELECT type, SUM(amount) as total
            FROM transactions
            WHERE is_deleted = 0
            AND transaction_date BETWEEN ? AND ?
            GROUP BY type
        """, (start_date, end_date))

        rows = cursor.fetchall()

        result = {
            "income": 0,
            "expense": 0
        }

        for row in rows:
            result[row["type"]] = row["total"] or 0

        return result

    def get_category_totals(self, start_date, end_date, transaction_type):
        cursor = self.conn.cursor()

        cursor.execute("""
            SELECT 
                c.id AS category_id,
                c.name AS category_name,
                SUM(t.amount) AS total
            FROM transactions t
            JOIN categories c ON t.category_id = c.id
            WHERE t.is_deleted = 0
            AND t.transaction_date BETWEEN ? AND ?
            AND t.type = ?
            GROUP BY c.id, c.name
            ORDER BY total DESC
        """, (start_date, end_date, transaction_type))

        rows = cursor.fetchall()

        return [
            {
                "category_id": row["category_id"],
                "category_name": row["category_name"],
                "total": row["total"] or 0
            }
            for row in rows
        ]

    def get_monthly_totals_for_range(self, start_date, end_date):
        cursor = self.conn.cursor()

        cursor.execute("""
            SELECT 
                substr(transaction_date, 1, 7) AS year_month,
                type,
                SUM(amount) AS total
            FROM transactions
            WHERE is_deleted = 0
            AND transaction_date BETWEEN ? AND ?
            GROUP BY year_month, type
            ORDER BY year_month ASC
        """, (start_date, end_date))

        rows = cursor.fetchall()

        result = {}

        for row in rows:
            ym = row["year_month"]

            if ym not in result:
                result[ym] = {"income": 0, "expense": 0}

            result[ym][row["type"]] = row["total"] or 0

        return result