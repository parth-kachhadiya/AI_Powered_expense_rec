# 📘 Layer-2 Documentation  
## Deterministic Financial Analytics Engine  
Project: AI-Powered Expense Intelligence System

---

# 🎯 Purpose of Layer-2

Layer-2 is responsible for **read-only deterministic analytics**.  
It transforms validated transaction data (Layer-1) into structured financial intelligence.

It does NOT:
- Modify database
- Call LLM
- Perform ML forecasting
- Contain business mutation logic

It ONLY:
- Analyze
- Compare
- Detect
- Signal

---

# 📂 Folder Structure

```
expense_ai/
│
├── intelligence/
│   ├── summary_service.py
│   ├── trend_service.py
│   ├── rule_service.py
│
├── database/
│   └── transaction_repository.py
```

---

# 1️⃣ SummaryService  
📍 Location: `expense_ai/intelligence/summary_service.py`

Responsible for **single-month snapshot intelligence**.

---

## 🔹 monthly_summary(year, month)

Returns total income, expense, and net cashflow for a given month.

Used as base for comparisons, rules, and rolling metrics.

---

## 🔹 category_breakdown(year, month, transaction_type)

Returns category-wise totals and percentage contribution (rounded to 2 decimals).

Used for ranking and behavior analysis.

---

## 🔹 top_categories(year, month, transaction_type, limit=3)

Returns highest contributing categories based on total amount.

Builds on `category_breakdown()`.

---

## 🔹 income_vs_expense_comparison(year, month)

Compares total income vs total expense and computes savings and expense ratio.

Provides immediate financial balance insight.

---

# 2️⃣ TrendService  
📍 Location: `expense_ai/intelligence/trend_service.py`

Responsible for **multi-month temporal analytics**.

---

## 🔹 compare_months(current_year, current_month, compare_year=None, compare_month=None)

Compares two months (default previous month).  
Returns:

- Income growth  
- Expense growth  
- Net growth  
- Category-wise growth  
- Absolute difference  
- Growth percentage  
- Behavioral status (NORMAL, ACTIVATED, DEACTIVATED)

Sorted by absolute growth impact.

---

## 🔹 rolling_average(current_year, current_month, window=3)

Computes Simple Moving Average (SMA) for:

- Income  
- Expense  
- Net  

Used for smoothing and rule detection.

---

## 🔹 expense_slope(current_year, current_month, last_n_months=6)

Computes linear regression slope for expense trend.

Returns slope value and direction (UPWARD, DOWNWARD, STABLE).

---

## 🔹 income_slope(current_year, current_month, last_n_months=6)

Same as expense_slope but applied to income.

---

## 🔹 net_cashflow_slope(current_year, current_month, last_n_months=6)

Same slope logic applied to net cashflow.

---

## 🔹 expense_volatility(current_year, current_month, last_n_months=6)

Computes:

- Mean
- Standard deviation
- Volatility ratio (σ / μ)

Measures financial stability.

---

## 🔹 income_volatility(...)

Same as expense_volatility for income.

---

## 🔹 net_cashflow_volatility(...)

Volatility measurement for net cashflow.

---

# 3️⃣ RuleService  
📍 Location: `expense_ai/intelligence/rule_service.py`

Responsible for converting analytics into structured alerts.

---

## 🔹 detect_expense_spike(year, month, window=3, threshold=0.25)

Triggers alert if expense exceeds rolling average by threshold %.

---

## 🔹 detect_income_drop(year, month, window=3, threshold=0.20)

Triggers alert if income falls below rolling average by threshold %.

---

## 🔹 detect_category_spike(year, month, threshold=40)

Flags category growth above threshold.

---

## 🔹 detect_statistical_anomaly(year, month, last_n_months=6, threshold=2)

Uses Z-score to detect statistically unusual expense behavior.

---

## 🔹 detect_category_anomaly(year, month, last_n_months=6, threshold=2)

Detects abnormal category-level deviation.

---

## 🔹 run_all_rules(year, month)

Executes all rules and returns structured alerts list.

---

# 📊 Mathematical Components Used

- Simple Moving Average (SMA)
- Linear Regression Slope
- Standard Deviation
- Z-score Anomaly Detection
- Growth Percentage & Absolute Difference

All deterministic.
No ML.
No LLM.
No mutation.

---

# 🏁 Layer-2 Status

Layer-2 is now a complete deterministic analytics engine featuring:

✔ Snapshot intelligence  
✔ Comparative intelligence  
✔ Rolling smoothing  
✔ Trend direction detection  
✔ Volatility measurement  
✔ Statistical anomaly detection  
✔ Rule-based signal generation  

Ready for Layer-3 (Forecasting & ML).
