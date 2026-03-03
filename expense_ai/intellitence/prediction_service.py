import os
import pickle
from datetime import timedelta
import pandas as pd
from statsmodels.tsa.holtwinters import ExponentialSmoothing

from expense_ai.engine.exceptions import ExpenseEngineError


class PredictionService:
    """
    PredictionService

    Responsible for ML-based financial forecasting.

    This service:
    - Loads active forecasting model metadata from repository
    - Reconstructs a Holt-Winters model using stored parameters
    - Generates short-horizon forecasts (1–3 months)
    - Computes 95% confidence intervals using residual standard deviation

    Important:
    - This service does NOT retrain models.
    - It assumes model configuration consistency.
    - It performs inference only.
    - Net cashflow forecasts should be derived, not independently trained.

    Failure Modes:
    - MODEL_NOT_FOUND if no active model exists
    - INVALID_SERIES for unsupported series
    - INVALID_HORIZON if months exceed allowed range
    """

    MAX_HORIZON = 3
    ALLOWED_SERIES = {"income", "expense", "net_cashflow"}

    def __init__(self, forecast_model_repo):
        self.repo = forecast_model_repo
        self._model_cache = {}   # 🔥 cache models in memory

    # -------------------------------------
    # Load Active Model (Cached)
    # -------------------------------------

    def _load_active_model(self, series_name, model_record):

        model_path = model_record["model_path"]

        if not os.path.exists(model_path):
            return None, None

        with open(model_path, "rb") as f:
            saved = pickle.load(f)

        # Reconstruct training series
        series = pd.Series(
            saved["series_values"],
            index=pd.to_datetime(saved["series_index"])
        )

        config = saved["config"]

        model = ExponentialSmoothing(
            series,
            trend=config["trend"],
            seasonal=config["seasonal"],
            seasonal_periods=config["seasonal_periods"],
            damped_trend=config["damped_trend"]
        ).fit()

        # Inject saved parameters
        model.params = saved["params"]

        return model, model_record

    # -------------------------------------
    # Predict
    # -------------------------------------

    def predict(self, series_name, months_ahead):

        try:
            series_name = series_name.strip().lower()

            if series_name not in self.ALLOWED_SERIES:
                raise ExpenseEngineError(
                    "INVALID_SERIES",
                    f"Invalid series name: {series_name}"
                )

            if not isinstance(months_ahead, int):
                raise ExpenseEngineError(
                    "INVALID_HORIZON",
                    "Prediction months must be integer"
                )

            if months_ahead < 1 or months_ahead > self.MAX_HORIZON:
                raise ExpenseEngineError(
                    "INVALID_HORIZON",
                    f"Months must be between 1 and {self.MAX_HORIZON}"
                )

            model_record = self.repo.get_active_model(series_name)

            if not model_record:
                raise ExpenseEngineError(
                    "MODEL_NOT_FOUND",
                    f"No active model found for {series_name}"
                )

            residual_std = float(model_record["residual_std"])
            z_score = 1.96

            # 🔥 Load reconstructed model (safe)
            model, _ = self._load_active_model(series_name, model_record)

            forecast_values = model.forecast(months_ahead)

            forecast_results = []

            # 🔥 No risky date arithmetic for now
            for idx, value in enumerate(forecast_values):
                forecast_results.append({
                    "month": f"Month+{idx+1}",
                    "predicted_value": float(value),
                    "lower_bound_95": float(value - z_score * residual_std),
                    "upper_bound_95": float(value + z_score * residual_std),
                })

            return {
                "status": "success",
                "series": series_name,
                "horizon": months_ahead,
                "confidence_level": "95%",
                "forecast": forecast_results
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