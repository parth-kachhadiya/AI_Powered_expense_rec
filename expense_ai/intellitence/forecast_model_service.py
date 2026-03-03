from expense_ai.engine.exceptions import ExpenseEngineError
from expense_ai.database.forecast_model_repository import ForecastModelRepository
from expense_ai.database.connection import get_connection
from expense_ai.register_model_to_database import extract_model_metadata

import os
from datetime import datetime

class ForecastModelService:

    ALLOWED_SERIES = {"income", "expense", "net_cashflow"}

    def __init__(self, forecast_model_repo):
        self.repo = forecast_model_repo

    # -----------------------------------------------------
    # Register New Model (After Training)
    # -----------------------------------------------------
    def register_model(self, series_name):
        conn = get_connection()
        repo = ForecastModelRepository(conn)

        # ----------------------------
        # Step 1: Find Latest Model File
        # ----------------------------
        PROJECT_ROOT = "D:\\languages\\python\\campusx-mcps\\AI_Powered_expense_rec\\expense_ai"
        MODELS_BASE_DIR = os.path.join(PROJECT_ROOT, "models")
        model_dir = os.path.join(MODELS_BASE_DIR, series_name)

        if not os.path.exists(model_dir):
            print(f"Model directory not found: {model_dir}")
            return

        files = [f for f in os.listdir(model_dir) if f.endswith(".pkl")]

        if not files:
            print(f"No model files found for {series_name}")
            return

        # Sort by date in filename
        files_sorted = sorted(
            files,
            key=lambda x: datetime.strptime(
                x.replace(".pkl", "").split("_")[-1],
                "%Y-%m-%d"
            ),
            reverse=True
        )

        latest_file = files_sorted[0]
        model_version = latest_file.replace(".pkl", "")

        # ----------------------------
        # Step 2: Check DB for Existing Version
        # ----------------------------
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id FROM forecast_models
            WHERE series_name = ?
            AND model_version = ?
        """, (series_name, model_version))

        existing = cursor.fetchone()

        # ----------------------------
        # Step 3: If Exists → Activate Only
        # ----------------------------
        if existing:

            # deactivate other models
            cursor.execute("""
                UPDATE forecast_models
                SET is_active = 0
                WHERE series_name = ?
            """, (series_name,))

            # activate this one
            cursor.execute("""
                UPDATE forecast_models
                SET is_active = 1
                WHERE series_name = ?
                AND model_version = ?
            """, (series_name, model_version))

            conn.commit()
            conn.close()

            print(f"Model '{model_version}' already exists. Activated successfully.")
            return

        # ----------------------------
        # Step 4: If Not Exists → Insert
        # ----------------------------
        metadata = extract_model_metadata(series_name)

        # deactivate previous models
        repo.deactivate_active_models(series_name)

        repo.insert_model(metadata)

        conn.close()


    # -----------------------------------------------------
    # Get Active Model Path (For Prediction)
    # -----------------------------------------------------
    def get_active_model_path(self, series_name):
        try:
            series_name = series_name.strip().lower()

            model = self.repo.get_active_model(series_name)

            if not model:
                raise ExpenseEngineError(
                    "MODEL_NOT_FOUND",
                    f"No active model found for {series_name}"
                )

            return {
                "status": "success",
                "model_path": model["model_path"],
                "model_version": model["model_version"]
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