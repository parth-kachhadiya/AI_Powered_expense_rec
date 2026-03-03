from expense_ai.database.forecast_model_repository import ForecastModelRepository
from expense_ai.intellitence.prediction_service import PredictionService
from expense_ai.database.connection import get_connection

_prediction_service = None

def _get_prediction_service():
    global _prediction_service

    if _prediction_service is None:
        conn = get_connection()
        repo = ForecastModelRepository()
        _prediction_service = PredictionService(repo)

    return _prediction_service


def register_forecast_tools(mcp):

    @mcp.tool()
    def predict_future(series: str, months_ahead: int):
        """
        Generate ML-based forecast for selected financial series.

        Parameters:
        - series (str): "income", "expense", or "net_cashflow".
        - months_ahead (int): Forecast horizon (1–3 months).

        Example:
        predict_future("income", 3)

        Returns:
        Predicted values with 95% confidence intervals.
        """
        service = _get_prediction_service()
        return service.predict(series, months_ahead)