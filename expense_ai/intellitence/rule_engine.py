from expense_ai.engine.exceptions import ExpenseEngineError


class RuleService:

    def __init__(self, trend_service, summary_service):
        self.trend_service = trend_service
        self.summary_service = summary_service

    # ======================================================
    # EXPENSE SPIKE RULE
    # ======================================================
    def detect_expense_spike(self, year, month, window=3, threshold=0.25):
        try:
            summary = self.summary_service.monthly_summary(year, month)
            rolling = self.trend_service.rolling_average(year, month, window)

            if summary["status"] != "success" or rolling["status"] != "success":
                return []

            current_expense = summary["data"]["total_expense"]
            rolling_avg = rolling["data"]["expense_sma"]

            if rolling_avg == 0:
                return []

            if current_expense > rolling_avg * (1 + threshold):
                return [{
                    "rule_id": "EXPENSE_SPIKE",
                    "severity": "HIGH",
                    "message": "Expense significantly above rolling average.",
                    "data": {
                        "current_expense": current_expense,
                        "rolling_average": rolling_avg
                    }
                }]

            return []

        except Exception:
            return []

    def detect_income_drop(self, year, month, window=3, threshold=0.20):
        try:
            summary = self.summary_service.monthly_summary(year, month)
            rolling = self.trend_service.rolling_average(year, month, window)

            if summary["status"] != "success" or rolling["status"] != "success":
                return []

            current_income = summary["data"]["total_income"]
            rolling_avg = rolling["data"]["income_sma"]

            if rolling_avg == 0:
                return []

            if current_income < rolling_avg * (1 - threshold):
                return [{
                    "rule_id": "INCOME_DROP",
                    "severity": "HIGH",
                    "message": "Income dropped significantly below rolling average.",
                    "data": {
                        "current_income": current_income,
                        "rolling_average": rolling_avg
                    }
                }]

            return []

        except Exception:
            return []

    def detect_category_spike(self, year, month, threshold=40):
        try:
            comparison = self.trend_service.compare_months(year, month)

            if comparison["status"] != "success":
                return []

            alerts = []

            categories = comparison["data"]["category_growth"]["expense"]

            for cat in categories:
                if cat["growth_status"] == "NORMAL" and \
                cat["growth_percentage"] and \
                cat["growth_percentage"] > threshold:

                    alerts.append({
                        "rule_id": "CATEGORY_SPIKE",
                        "severity": "MEDIUM",
                        "message": f"Spike detected in category {cat['category_name']}.",
                        "data": cat
                    })

            return alerts

        except Exception:
            return []


    def run_all_rules(self, year, month):
        alerts = []

        alerts.extend(self.detect_expense_spike(year, month))
        alerts.extend(self.detect_income_drop(year, month))
        alerts.extend(self.detect_category_spike(year, month))

        return {
            "status": "success",
            "metric": "rule_evaluation",
            "alerts": alerts
        }

    def detect_statistical_anomaly(self, year, month, last_n_months=6, threshold=2):
        try:
            summary = self.summary_service.monthly_summary(year, month)
            volatility = self.trend_service.expense_volatility(year, month, last_n_months)

            if summary["status"] != "success" or volatility["status"] != "success":
                return []

            current_expense = summary["data"]["total_expense"]
            mean = volatility["data"]["mean"]
            std_dev = volatility["data"]["std_dev"]

            if std_dev == 0:
                return []   

            z_score = round((current_expense - mean) / std_dev, 2)

            if abs(z_score) >= threshold:
                return [{
                "rule_id": "STATISTICAL_ANOMALY",
                "severity": "HIGH",
                "message": "Expense statistically deviates from historical pattern.",
                "data": {
                    "z_score": z_score,
                    "mean": mean,
                    "std_dev": std_dev,
                    "current_expense": current_expense
                }
            }]

            return []

        except Exception:
            return []

    def detect_category_anomaly(self, year, month, last_n_months=6, threshold=2):
        try:
            comparison = self.trend_service.compare_months(year, month)
            if comparison["status"] != "success":
                return []

            alerts = []

            categories = comparison["data"]["category_growth"]["expense"]

            for cat in categories:
                if cat["growth_status"] == "NORMAL" and \
                cat["growth_percentage"] and \
                abs(cat["growth_percentage"]) > 100:

                    alerts.append({
                        "rule_id": "CATEGORY_ANOMALY",
                        "severity": "MEDIUM",
                        "message": f"Unusual change in {cat['category_name']}.",
                        "data": cat
                    })

            return alerts

        except Exception:
            return []