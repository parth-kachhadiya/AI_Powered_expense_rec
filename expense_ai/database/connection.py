import sqlite3
from pathlib import Path


DB_PATH = Path("D:\\languages\\python\\campusx-mcps\\AI_Powered_expense_rec\\expense_ai\\data\\expense.db")


def get_connection():
    """
    Create and return a SQLite database connection.
    Enables foreign key constraints and row access by column name.
    """
    # Ensure data directory exists
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(DB_PATH)

    # Enable foreign key support
    conn.execute("PRAGMA foreign_keys = ON;")

    # Return rows as dictionary-like objects
    conn.row_factory = sqlite3.Row

    return conn