from rich.console import Console
from rich.table import Table
from rich.prompt import Prompt, IntPrompt
from rich.panel import Panel
from rich import box

from database.connection import get_connection
from database.category_repository import CategoryRepository
from database.transaction_repository import TransactionRepository
from database.forecast_model_repository import ForecastModelRepository
from intellitence.forecast_model_service import ForecastModelService

from engine.expense_engine import ExpenseEngine
from intellitence.summary_service import SummaryService
from intellitence.trend_service import TrendService
from intellitence.prediction_service import PredictionService
from register_model_to_database import register_model


console = Console()


def setup_services():
    conn = get_connection()

    category_repo = CategoryRepository(conn)
    transaction_repo = TransactionRepository(conn)
    forecast_repo = ForecastModelRepository(conn)

    engine = ExpenseEngine(category_repo, transaction_repo)
    summary_service = SummaryService(transaction_repo)
    trend_service = TrendService(transaction_repo)
    prediction_service = PredictionService(forecast_repo)

    return engine, summary_service, trend_service, prediction_service


# --------------------------------------------------
# MENU FUNCTIONS
# --------------------------------------------------

def add_transaction(engine):
    console.print("\n[bold cyan]Add Transaction[/bold cyan]")

    amount = float(Prompt.ask("Amount"))
    tx_type = Prompt.ask("Type (income/expense)")
    category_id = int(Prompt.ask("Category ID"))
    payment_method = Prompt.ask("Payment Method (cash/online/cheque)")
    description = Prompt.ask("Description")
    date = Prompt.ask("Transaction Date (YYYY-MM-DD)")

    data = {
        "amount": amount,
        "type": tx_type,
        "category_id": category_id,
        "payment_method": payment_method,
        "description": description,
        "transaction_date": date
    }

    result = engine.add_transaction(data)
    console.print(result)

def delete_transaction(engine):
    console.print("\n[bold cyan]Delete Transaction (Soft Delete)[/bold cyan]")

    transaction_id = IntPrompt.ask("Transaction ID to delete")

    confirm = Prompt.ask("Are you sure? (yes/no)")

    if confirm.lower() != "yes":
        console.print("[yellow]Deletion cancelled[/yellow]")
        return

    result = engine.delete_transaction(transaction_id)
    console.print(result)

def list_transactions(engine):
    console.print("\n[bold cyan]List Transactions[/bold cyan]")

    res = engine.list_transactions()
    
    if res.get("status") != "success":
        console.print(f"[red]Error: {res.get('message', 'Unknown error')}[/red]")
        return
        
    txs = res.get("data", [])

    table = Table(title="Transactions", box=box.MINIMAL_DOUBLE_HEAD)

    table.add_column("ID")
    table.add_column("Amount")
    table.add_column("Type")
    table.add_column("Category")
    table.add_column("Date")

    for tx in txs:
        table.add_row(
            str(tx["id"]),
            str(tx["amount"]),
            str(tx["type"]),
            str(tx["category_id"]),
            str(tx["transaction_date"])
        )

    console.print(table)


def monthly_summary(summary_service):
    year = IntPrompt.ask("Year")
    month = IntPrompt.ask("Month")

    result = summary_service.monthly_summary(year, month)
    console.print(result)


def category_breakdown(summary_service):
    year = IntPrompt.ask("Year")
    month = IntPrompt.ask("Month")
    tx_type = Prompt.ask("Type (income/expense)")

    result = summary_service.category_breakdown(year, month, tx_type)
    console.print(result)


def month_over_month(trend_service):
    year = IntPrompt.ask("Current Year")
    month = IntPrompt.ask("Current Month")

    result = trend_service.compare_months(year, month)
    console.print(result)


def predict_future(prediction_service):
    series = Prompt.ask("Series (income/expense)")
    months = IntPrompt.ask("Months Ahead (1-3)")

    result = prediction_service.predict(series, months)
    console.print(result)

def update_transaction(engine):
    console.print("\n[bold cyan]Update Transaction[/bold cyan]")

    transaction_id = IntPrompt.ask("Transaction ID to update")

    amount = float(Prompt.ask("New Amount"))
    tx_type = Prompt.ask("Type (income/expense)")
    category_id = int(Prompt.ask("Category ID"))
    payment_method = Prompt.ask("Payment Method (cash/online/cheque)")
    description = Prompt.ask("Description")
    date = Prompt.ask("Transaction Date (YYYY-MM-DD)")

    data = {
        "amount": amount,
        "type": tx_type,
        "category_id": category_id,
        "payment_method": payment_method,
        "description": description,
        "transaction_date": date
    }

    result = engine.update_transaction(transaction_id, data)
    console.print(result)


def register_models():
    ForecastModelService("D:\\languages\\python\\campusx-mcps\\AI_Powered_expense_rec\\expense_ai").register_model("income")
    ForecastModelService("D:\\languages\\python\\campusx-mcps\\AI_Powered_expense_rec\\expense_ai").register_model("expense")
    console.print("[green]Models registered successfully[/green]")


# --------------------------------------------------
# MAIN LOOP
# --------------------------------------------------

def main():

    engine, summary_service, trend_service, prediction_service = setup_services()

    while True:

        console.print(Panel.fit(
            "[bold yellow]AI Expense Intelligence System[/bold yellow]",
            border_style="bright_blue"
        ))

        console.print("""
        [1] Add Transaction
        [2] Update Transaction
        [3] Delete Transaction
        [4] List Transactions
        [5] Monthly Summary
        [6] Category Breakdown
        [7] Month-over-Month Growth
        [8] Predict Future
        [9] Register Latest Model
        [10] Exit
        """)

        choice = Prompt.ask("Select Option")

        if choice == "1":
            add_transaction(engine)
        elif choice == "2":
            update_transaction(engine)
        elif choice == "3":
            delete_transaction(engine)
        elif choice == "4":
            list_transactions(engine)
        elif choice == "5":
            monthly_summary(summary_service)
        elif choice == "6":
            category_breakdown(summary_service)
        elif choice == "7":
            month_over_month(trend_service)
        elif choice == "8":
            predict_future(prediction_service)
        elif choice == "9":
            register_models()
        elif choice == "10":
            console.print("[bold red]Exiting...[/bold red]")
            break
        else:
            console.print("[red]Invalid Option[/red]")

if __name__ == "__main__":
    main()