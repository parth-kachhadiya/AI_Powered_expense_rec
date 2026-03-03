# AI-Powered Expense Intelligence System
# Layer-1: Core Engine Architecture (Frozen Version)

---

## 1. Overview

Layer-1 represents the **stable foundation** of the AI-Powered Expense Intelligence System.

It provides:

- Structured financial data storage
- Strict domain validation
- Clean layered architecture
- Soft delete protection
- Structured error handling
- Centralized logging
- Filterable transaction retrieval

Layer-1 is intentionally built to be:

- Modular
- Stable
- Adapter-ready
- Intelligence-ready
- Safe for future ML/LLM expansion

This layer does NOT include analytics, ML, forecasting, or automation.

---

## 2. Architectural Philosophy

Layer-1 follows these core architectural principles:

### 2.1 Layered Architecture
- **Adapter → ExpenseEngine → Repository → Database**

Adapters must NEVER directly access:
- Repository
- Database
- SQL

All business operations must pass through `ExpenseEngine`.

---

### 2.2 Separation of Concerns

+------------+-----------------------------+
|   Layer    | Responsibility              |
+------------+-----------------------------+
|  Database  | Data persistence            |
| Repository | SQL execution only          |
|   Engine   | Business logic & validation |
|    Utils   | Logging & shared utilities  |
+------------+-----------------------------+

---

### 2.3 Controlled Error Propagation

- Business errors are structured
- System errors are isolated
- No raw exceptions leak outward

---

### 2.4 Observability

All important events are logged to: `logs/app.logs`


---

## 3. Project Structure

```txt
expense_ai/
│
├── intelligence/
│   ├── summary_service.py
│   ├── trend_service.py
│   ├── rule_service.py
│   └── __init__.py
|
├── database/
│       ├── connection.py
│       ├── init_db.py
│       ├── category_repository.py
│       └── transaction_repository.py
│
├── engine/
│      ├── expense_engine.py
│      └── exceptions.py
│
├── utils/
│     └── logger.py
│
├── data/
│    └── expense.db
│
├── logs/
│    └── app.log
│
└── main.py
```


---

## 4. Database Design

### 4.1 Categories Table

```sql
CREATE TABLE categories (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    type TEXT NOT NULL CHECK(type IN ('income','expense')),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT 1
);

CREATE TABLE transactions (
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
```