import os
import pickle
import numpy as np
from datetime import datetime

# from database.connection import get_connection
from expense_ai.database.connection import get_connection
from expense_ai.database.forecast_model_repository import ForecastModelRepository

PROJECT_ROOT = "D:\\languages\\python\\campusx-mcps\\AI_Powered_expense_rec\\expense_ai"
MODELS_BASE_DIR = os.path.join(PROJECT_ROOT, "models")

def extract_model_metadata(series_name):
    """
    Loads latest model for given series and extracts metadata
    directly from statsmodels ExponentialSmoothingResultsWrapper object.
    """

    model_dir = os.path.join(MODELS_BASE_DIR, series_name)

    if not os.path.exists(model_dir):
        raise Exception(f"Model directory does not exist: {model_dir}")

    files = [f for f in os.listdir(model_dir) if f.endswith(".pkl")]

    if not files:
        raise Exception(f"No model file found in {model_dir}")

    # Sort files by date in filename (YYYY-MM-DD)
    files_sorted = sorted(
        files,
        key=lambda x: datetime.strptime(
            x.replace(".pkl", "").split("_")[-1],
            "%Y-%m-%d"
        ),
        reverse=True
    )

    latest_file = files_sorted[0]
    model_path = os.path.join(model_dir, latest_file)

    # Load model object
    with open(model_path, "rb") as f:
        model = pickle.load(f)

    model_obj = model.model

    # -------------------------
    # Training Window Extraction (Safer Way)
    # -------------------------
    try:
        training_index = model.data.row_labels
    except Exception:
        training_index = model_obj._index  # fallback (private)

    training_start = str(training_index[0].date())
    training_end = str(training_index[-1].date())
    trained_on_months = len(model_obj.endog)

    # -------------------------
    # Model Configuration
    # -------------------------
    seasonal_period = model_obj.seasonal_periods
    trend_type = model_obj.trend
    seasonal_type = model_obj.seasonal

    # Correct Damping Detection
    damping_value = model.params.get("damping_trend")
    damped = 1 if damping_value is not None else 0

    # -------------------------
    # Metrics Computation
    # -------------------------
    fitted_values = model.fittedvalues
    actual_values = model_obj.endog

    mae = float(np.mean(np.abs(actual_values - fitted_values)))
    rmse = float(np.sqrt(np.mean((actual_values - fitted_values) ** 2)))

    residuals = model.resid
    residual_std = float(np.std(residuals))

    return {
        "series_name": series_name,
        "model_version": latest_file.replace(".pkl", ""),
        "model_path": model_path,
        "seasonal_period": seasonal_period,
        "trend_type": trend_type,
        "seasonal_type": seasonal_type,
        "damped": damped,
        "forecast_horizon": None,  # You can manually set if needed
        "training_start": training_start,
        "training_end": training_end,
        "trained_on_months": trained_on_months,
        "mae": mae,
        "rmse": rmse,
        "directional_accuracy": None,
        "residual_std": residual_std,
        "is_active": 1
    }

def register_model(series_name):
    conn = get_connection()
    repo = ForecastModelRepository(conn)

    metadata = extract_model_metadata(series_name)

    # deactivate previous models
    repo.deactivate_active_models(series_name)

    repo.insert_model(metadata)

    conn.close()

    print(f"{series_name} model registered successfully.")


if __name__ == "__main__":
    register_model("income")
    register_model("expense")