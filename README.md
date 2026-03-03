# AI-Powered Expense Intelligence System

## 🚀 Project Overview

This project is a **modular AI-powered financial intelligence system** designed for a single-user personal finance workflow.  

It is **not a basic CRUD expense tracker**.  
It is a structured, production-style system integrating:

- 🗄 Relational Database Architecture
- 🧠 Validation & Business Logic Layer
- 📊 Deterministic Analytics Engine
- 📈 Forecasting with Holt Linear Exponential Smoothing
- 🤖 LLM Integration via FastMCP (Claude Desktop)
- ⚙️ Modular Architecture with Clear Layer Separation

The system emphasizes:
- Clean architecture
- Controlled AI interaction
- Thread-safe execution
- Forecast explainability
- Structured data flow

---

# 🏗 System Architecture

## High-Level Architecture

```
User (CLI / Claude Desktop)
        ↓
FastMCP Tools
        ↓
Service Layer (Business Logic)
        ↓
Repository Layer
        ↓
SQLite Database
```

Forecasting Layer:

```
Forecast Model (.pkl)
        ↓
PredictionService (with caching)
        ↓
Confidence Interval Logic
        ↓
Structured JSON Output
```

---

# 📂 Project Structure

```
expense_ai/
│
├── database/
│   ├── connection.py
│   ├── category_repository.py
│   ├── transaction_repository.py
│   ├── forecast_model_repository.py
│
├── engine/
│   ├── expense_engine.py
│   ├── exceptions.py
│
├── analytics/
│   ├── analytics_service.py
│   ├── trend_service.py
│
├── forecasting/
│   ├── prediction_service.py
│   ├── model_registration.py
│
├── mcp/
│   ├── server.py
│   ├── transaction_tools.py
│   ├── analytics_tools.py
│   ├── forecast_tools.py
│
├── main.py (CLI testing interface)
```

---

# 🧱 Layer 1 – Transaction Intelligence Engine

## 🎯 Purpose
Handle transaction operations with strict validation and clean architecture.

## Key Components

### 1️⃣ Validation Layer
- Enforces allowed transaction types
- Enforces allowed payment methods
- Validates category-type mapping
- Ensures amount > 0
- Prevents invalid updates

### 2️⃣ Service Layer (`ExpenseEngine`)
Handles:
- Add transaction
- Update transaction
- Soft delete transaction
- List transactions

Returns structured JSON responses.

### 3️⃣ Repository Layer
Responsible for:
- All SQL queries
- No business logic
- No AI logic
- No validation logic

### 4️⃣ Soft Delete Strategy
Transactions are never hard-deleted.
- `is_deleted` flag
- `deleted_at` timestamp

Ensures audit integrity.

---

# 📊 Layer 2 – Financial Analytics Engine

This layer converts raw transactions into structured financial insights.

## Features Implemented

### 🔹 Monthly Summary
- Total income
- Total expense
- Net cashflow

### 🔹 Category Breakdown
- Category-wise totals
- Percentage contribution
- Structured JSON output

### 🔹 Month-over-Month Growth
- Expense growth
- Income growth
- Net cashflow comparison
- Handles zero-division cases safely

### 🔹 Structured Output
All analytics return:
- Structured JSON
- No formatted strings
- Ready for LLM explanation layer

---

# 📈 Layer 3 – Forecasting Engine

## 🎯 Objective
Predict future financial values (1–3 months horizon).

## Model Used
**Holt Linear Exponential Smoothing**

- Trend component
- Optional damped trend
- Controlled horizon (max 3 months)
- Suitable for short-term financial forecasting

---

## Model Registry System

### `forecast_models` Table Stores:
- Series name (income/expense)
- Model version
- Model file path
- Training window
- MAE
- RMSE
- Residual standard deviation
- Active model flag

This enables:
- Version control
- Model lifecycle management
- Controlled activation
- Performance tracking

---

## Confidence Interval Logic

Forecast output includes:

- Point prediction
- 95% confidence interval
- Upper bound
- Lower bound

Confidence interval is computed using:
- Stored residual standard deviation
- z-score (1.96 for 95%)

Residual metrics are not recomputed during prediction.

---

## Model Caching Strategy

To avoid:
- Disk I/O delays
- Thread blocking
- Repeated pickle loading

The system:
- Loads model once
- Caches in memory
- Reuses safely

This prevents MCP timeouts.

---

# 🤖 FastMCP + Claude Integration

## Tool-Based LLM Architecture

Claude does NOT:
- Access database
- Execute SQL
- Modify business logic

Claude:
- Extracts structured parameters
- Calls specific MCP tool
- Receives structured JSON
- Converts into natural explanation

---

## Example Flow

User:
> “I spent 2500 on groceries yesterday in cash.”

Flow:
1. Claude extracts fields
2. Calls `add_transaction`
3. Engine validates
4. Repository inserts
5. JSON response returned
6. Claude explains result

---

## Available MCP Tools

### Transaction Tools
- add_transaction
- update_transaction
- delete_transaction
- list_transactions

### Analytics Tools
- monthly_summary
- category_breakdown
- month_over_month_growth

### Forecast Tool
- predict_future

---

# 🔐 Concurrency & Thread Safety

SQLite connections:
- Created per request
- Closed after use
- Never shared across threads

Model object:
- Cached globally
- Safe for read-only use

This ensures:
- No SQLite thread errors
- No deadlocks
- Stable MCP execution

---

# 🖥 CLI Testing Layer

Before MCP integration, entire system was validated via:

- Rich-based menu-driven CLI
- CRUD testing
- Analytics validation
- Forecast testing
- Model registration verification

This ensured:
- System stability
- Proper data flow
- Layer isolation

---

# 🧠 Key Design Principles

- Separation of concerns
- LLM isolation from database
- Business logic independent of AI
- No tight coupling
- Incremental development
- Thread-safe server execution
- Version-controlled forecasting
- Structured response design

---

# 📌 Future Improvements

- Drift detection
- Automated retraining trigger
- Forecast logging
- Advanced anomaly detection
- Extended forecasting horizon
- Financial insight scoring
- Personalized AI financial advisor mode

---

# 🎯 What This Project Demonstrates

- AI system architecture design
- ML model lifecycle management
- Database normalization
- Forecast explainability
- MCP-based LLM orchestration
- Thread-safe backend design
- Structured tool-based AI control

---

# 🏁 Conclusion

This project represents a structured attempt to move from:

Basic expense tracking  
→ Financial intelligence system  

It combines:
- Data engineering
- ML forecasting
- AI orchestration
- System architecture
- Production-style thinking

The system is modular, extensible, and ready for further intelligence expansion.

---

## Author

Built with a focus on ML/DL systems design and production-level architecture thinking.

---
