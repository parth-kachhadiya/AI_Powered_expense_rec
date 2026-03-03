from fastmcp import FastMCP

from expense_ai.mcp.transaction_tools import register_transaction_tools
from expense_ai.mcp.analytics_tools import register_analytics_tools
from expense_ai.mcp.forecast_tools import register_forecast_tools


def create_app():
    """
    create_app

    Initializes and configures the FastMCP server.

    Registers:
    - Transaction tools (CRUD operations)
    - Analytics tools (descriptive intelligence)
    - Forecast tools (ML-based prediction)

    Acts as integration layer between Claude and
    the AI Expense Intelligence system.
    """
    mcp = FastMCP("AI Expense Intelligence")

    register_transaction_tools(mcp)
    register_analytics_tools(mcp)
    register_forecast_tools(mcp)

    return mcp


app = create_app()