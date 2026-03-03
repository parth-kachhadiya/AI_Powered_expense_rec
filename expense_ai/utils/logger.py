import logging
from pathlib import Path


LOG_PATH = Path("D:\\languages\\python\\campusx-mcps\\AI_Powered_expense_rec\\expense_ai\\logs\\app.log")
LOG_PATH.parent.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    filename=LOG_PATH,
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)

logger = logging.getLogger("ExpenseAI")