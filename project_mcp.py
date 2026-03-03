"""
Entry point for MCP server execution.

Adds project root to Python path and initializes the MCP application.
Used by FastMCP CLI for development and testing.

Run using:
fastmcp dev inspector project_mcp.py
"""

import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from expense_ai.mcp.server import create_app

app = create_app()