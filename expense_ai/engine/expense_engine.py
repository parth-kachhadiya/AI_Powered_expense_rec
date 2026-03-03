# from engine.exceptions import ExpenseEngineError
from expense_ai.engine.exceptions import ExpenseEngineError
from expense_ai.utils.logger import logger


class ExpenseEngine:

    ALLOWED_TYPES = {"income", "expense"}
    ALLOWED_PAYMENT_METHODS = {"cash", "online", "cheque"}

    def __init__(self, category_repo, transaction_repo):
        self.category_repo = category_repo
        self.transaction_repo = transaction_repo

    # ==========================================================
    # CREATE
    # ==========================================================
    def add_transaction(self, data):
        try:
            self._validate_transaction_data(data)

            transaction_id = self.transaction_repo.insert(data)

            logger.info(f"Transaction added | ID={transaction_id}")

            return {
                "status": "success",
                "transaction_id": transaction_id
            }

        except ExpenseEngineError as e:
            logger.warning(f"Business Error | Code={e.code} | Message={e.message}")
            return {
                "status": "error",
                "code": e.code,
                "message": e.message
            }

        except Exception as e:
            logger.error(f"Internal Error | {str(e)}")
            return {
                "status": "error",
                "code": "INTERNAL_ERROR",
                "message": str(e)
            }

    # ==========================================================
    # READ (Single)
    # ==========================================================
    def get_transaction(self, transaction_id):
        try:
            tx = self.transaction_repo.get_by_id(transaction_id)

            if not tx:
                raise ExpenseEngineError("NOT_FOUND", "Transaction not found.")

            return {
                "status": "success",
                "data": dict(tx)
            }

        except ExpenseEngineError as e:
            logger.warning(f"Business Error | Code={e.code} | Message={e.message}")
            return {
                "status": "error",
                "code": e.code,
                "message": e.message
            }

        except Exception as e:
            logger.error(f"Internal Error | {str(e)}")
            return {
                "status": "error",
                "code": "INTERNAL_ERROR",
                "message": str(e)
            }

    # ==========================================================
    # UPDATE
    # ==========================================================
    def update_transaction(self, transaction_id, data):
        try:
            self._validate_transaction_data(data)

            rows = self.transaction_repo.update(transaction_id, data)

            if rows == 0:
                raise ExpenseEngineError(
                    "NOT_FOUND",
                    "Transaction not found or already deleted."
                )

            logger.info(f"Transaction updated | ID={transaction_id}")

            return {
                "status": "success",
                "updated_transaction_id": transaction_id
            }

        except ExpenseEngineError as e:
            logger.warning(f"Business Error | Code={e.code} | Message={e.message}")
            return {
                "status": "error",
                "code": e.code,
                "message": e.message
            }

        except Exception as e:
            logger.error(f"Internal Error | {str(e)}")
            return {
                "status": "error",
                "code": "INTERNAL_ERROR",
                "message": str(e)
            }

    # ==========================================================
    # DELETE (Soft)
    # ==========================================================
    def delete_transaction(self, transaction_id):
        try:
            rows = self.transaction_repo.soft_delete(transaction_id)

            if rows == 0:
                raise ExpenseEngineError(
                    "NOT_FOUND",
                    "Transaction not found or already deleted."
                )

            logger.info(f"Transaction soft-deleted | ID={transaction_id}")

            return {
                "status": "success",
                "deleted_transaction_id": transaction_id
            }

        except ExpenseEngineError as e:
            logger.warning(f"Business Error | Code={e.code} | Message={e.message}")
            return {
                "status": "error",
                "code": e.code,
                "message": e.message
            }

        except Exception as e:
            logger.error(f"Internal Error | {str(e)}")
            return {
                "status": "error",
                "code": "INTERNAL_ERROR",
                "message": str(e)
            }

    # ==========================================================
    # LIST (Filtered)
    # ==========================================================
    def list_transactions(
        self,
        start_date=None,
        end_date=None,
        transaction_type=None,
        category_id=None,
    ):
        try:
            if transaction_type:
                transaction_type = transaction_type.strip().lower()
                if transaction_type not in self.ALLOWED_TYPES:
                    raise ExpenseEngineError(
                        "INVALID_TYPE",
                        "Invalid transaction type."
                    )

            transactions = self.transaction_repo.list_transactions(
                start_date=start_date,
                end_date=end_date,
                transaction_type=transaction_type,
                category_id=category_id,
            )

            logger.info(
                f"Transactions listed | Count={len(transactions)}"
            )

            return {
                "status": "success",
                "data": [dict(tx) for tx in transactions]
            }

        except ExpenseEngineError as e:
            logger.warning(f"Business Error | Code={e.code} | Message={e.message}")
            return {
                "status": "error",
                "code": e.code,
                "message": e.message
            }

        except Exception as e:
            logger.error(f"Internal Error | {str(e)}")
            return {
                "status": "error",
                "code": "INTERNAL_ERROR",
                "message": str(e)
            }

    # ==========================================================
    # PRIVATE VALIDATION
    # ==========================================================
    def _validate_transaction_data(self, data):

        data["type"] = data["type"].strip().lower()
        data["payment_method"] = data["payment_method"].strip().lower()

        required_fields = [
            "amount", "type", "category_id",
            "payment_method", "transaction_date"
        ]

        for field in required_fields:
            if field not in data:
                raise ExpenseEngineError(
                    "MISSING_FIELD",
                    f"Missing required field: {field}"
                )

        if data["amount"] <= 0:
            raise ExpenseEngineError(
                "INVALID_AMOUNT",
                "Amount must be greater than 0."
            )

        if data["type"] not in self.ALLOWED_TYPES:
            raise ExpenseEngineError(
                "INVALID_TYPE",
                "Invalid transaction type."
            )

        if data["payment_method"] not in self.ALLOWED_PAYMENT_METHODS:
            raise ExpenseEngineError(
                "INVALID_PAYMENT_METHOD",
                "Invalid payment method."
            )

        category = self.category_repo.get_by_id(data["category_id"])

        if not category:
            raise ExpenseEngineError(
                "CATEGORY_NOT_FOUND",
                "Category not found."
            )

        if category["type"] != data["type"]:
            raise ExpenseEngineError(
                "FIELD_MISMATCH",
                "Transaction type does not match category type."
            )