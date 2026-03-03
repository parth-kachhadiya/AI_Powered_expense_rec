from database.connection import get_connection


def create_tables(conn):
    cursor = conn.cursor()

    # Categories table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS categories (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL UNIQUE,
            type TEXT NOT NULL CHECK(type IN ('income','expense')),
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            is_active BOOLEAN DEFAULT 1
        );
    """)

    # Transactions table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY,
            amount REAL NOT NULL CHECK(amount > 0),
            type TEXT NOT NULL CHECK(type IN ('income','expense')),
            category_id INTEGER NOT NULL,
            payment_method TEXT NOT NULL CHECK(payment_method IN ('cash','online','cheque')),
            description TEXT,
            transaction_date DATE NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME,
            is_deleted BOOLEAN DEFAULT 0,
            deleted_at DATETIME,
            FOREIGN KEY(category_id) REFERENCES categories(id)
        );
    """)

    conn.commit()


def seed_categories(conn):
    cursor = conn.cursor()

    categories = [
        # Income
        ("Salary", "income"),
        ("Business", "income"),
        ("Investment", "income"),
        ("Rental", "income"),
        ("Other Income", "income"),

        # Expense
        ("Housing", "expense"),
        ("Food", "expense"),
        ("Transportation", "expense"),
        ("Utilities", "expense"),
        ("Healthcare", "expense"),
        ("Personal", "expense"),
        ("Entertainment", "expense"),
        ("Education", "expense"),
        ("Investments", "expense"),
        ("Other Expense", "expense"),
    ]

    for name, category_type in categories:
        cursor.execute("""
            INSERT OR IGNORE INTO categories (name, type)
            VALUES (?, ?)
        """, (name, category_type))

    conn.commit()


def initialize_database():
    conn = get_connection()
    create_tables(conn)
    seed_categories(conn)
    conn.close()