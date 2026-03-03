from expense_ai.database.connection import get_connection

class ForecastModelRepository:
    """
    ForecastModelRepository

    Persistence layer for forecast model metadata.

    Responsibilities:
    - Store model metadata records
    - Manage active/inactive model versions
    - Retrieve active model configuration
    - Provide model lineage history

    This repository does NOT:
    - Train models
    - Perform forecasting

    Connection lifecycle is managed per-method to ensure
    thread safety and avoid SQLite locking.
    """

    # -----------------------------------------------------
    # Insert new model metadata
    # -----------------------------------------------------
    def insert_model(self, data):
        with get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute("""
                INSERT INTO forecast_models (
                    series_name,
                    model_version,
                    model_path,
                    seasonal_period,
                    trend_type,
                    seasonal_type,
                    damped,
                    forecast_horizon,
                    training_start,
                    training_end,
                    trained_on_months,
                    mae,
                    rmse,
                    directional_accuracy,
                    residual_std,
                    is_active
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                data["series_name"],
                data["model_version"],
                data["model_path"],
                data.get("seasonal_period"),
                data.get("trend_type"),
                data.get("seasonal_type"),
                data.get("damped"),
                data.get("forecast_horizon"),
                data.get("training_start"),
                data.get("training_end"),
                data.get("trained_on_months"),
                data.get("mae"),
                data.get("rmse"),
                data.get("directional_accuracy"),
                data.get("residual_std"),
                data.get("is_active", 1),
            ))

            conn.commit()
            return cursor.lastrowid

    # -----------------------------------------------------
    # Deactivate previous active models
    # -----------------------------------------------------
    def deactivate_active_models(self, series_name):
        with get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute("""
                UPDATE forecast_models
                SET is_active = 0
                WHERE series_name = ?
                AND is_active = 1
            """, (series_name,))

            conn.commit()

    # -----------------------------------------------------
    # Get active model
    # -----------------------------------------------------
    def get_active_model(self, series_name):
        with get_connection() as conn:
            conn.row_factory = self._dict_factory
            cursor = conn.cursor()

            cursor.execute("""
                SELECT *
                FROM forecast_models
                WHERE series_name = ?
                AND is_active = 1
                ORDER BY created_at DESC
                LIMIT 1
            """, (series_name,))

            return cursor.fetchone()

    # -----------------------------------------------------
    # Get model by version
    # -----------------------------------------------------
    def get_model_by_version(self, series_name, model_version):
        with get_connection() as conn:
            conn.row_factory = self._dict_factory
            cursor = conn.cursor()

            cursor.execute("""
                SELECT *
                FROM forecast_models
                WHERE series_name = ?
                AND model_version = ?
            """, (series_name, model_version))

            return cursor.fetchone()

    # -----------------------------------------------------
    # List all models for a series
    # -----------------------------------------------------
    def list_models(self, series_name):
        with get_connection() as conn:
            conn.row_factory = self._dict_factory
            cursor = conn.cursor()

            cursor.execute("""
                SELECT *
                FROM forecast_models
                WHERE series_name = ?
                ORDER BY created_at DESC
            """, (series_name,))

            return cursor.fetchall()

    # -----------------------------------------------------
    # Row → Dict converter
    # -----------------------------------------------------
    @staticmethod
    def _dict_factory(cursor, row):
        return {col[0]: row[idx] for idx, col in enumerate(cursor.description)}