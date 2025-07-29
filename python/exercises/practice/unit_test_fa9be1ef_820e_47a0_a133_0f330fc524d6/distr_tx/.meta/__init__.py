import time
import json

class TransactionOrchestrator:
    TIMEOUT = 5

    def __init__(self):
        self.completed_transactions = {}

    def process_order(self, order_data):
        start_time = time.perf_counter()
        order_key = json.dumps(order_data, sort_keys=True)

        # Return cached result if order has already been processed
        if order_key in self.completed_transactions:
            return self.completed_transactions[order_key]

        try:
            order_id = self._create_order(order_data)
            if self._check_timeout(start_time):
                return self._timeout_response(order_key)
        except Exception as e:
            self._rollback_create_order(None)
            result = {"status": "failure", "error": "Order creation failed", "reason": str(e)}
            self.completed_transactions[order_key] = result
            return result

        try:
            self._process_payment(order_data)
            if self._check_timeout(start_time):
                return self._timeout_response(order_key)
        except Exception as e:
            self._rollback_create_order(order_id)
            result = {"status": "failure", "error": "Payment failed", "reason": str(e)}
            self.completed_transactions[order_key] = result
            return result

        try:
            self._reserve_inventory(order_data)
            if self._check_timeout(start_time):
                return self._timeout_response(order_key)
        except Exception as e:
            self._rollback_create_order(order_id)
            self._rollback_payment(order_data)
            result = {"status": "failure", "error": "Inventory reservation failed", "reason": str(e)}
            self.completed_transactions[order_key] = result
            return result

        try:
            self._send_notification(order_data)
            if self._check_timeout(start_time):
                return self._timeout_response(order_key)
        except Exception as e:
            self._rollback_create_order(order_id)
            self._rollback_payment(order_data)
            self._rollback_inventory(order_data)
            result = {"status": "failure", "error": "Notification failed", "reason": str(e)}
            self.completed_transactions[order_key] = result
            return result

        result = {"status": "success", "order_id": order_id}
        self.completed_transactions[order_key] = result
        return result

    def _check_timeout(self, start_time):
        return (time.perf_counter() - start_time) > self.TIMEOUT

    def _timeout_response(self, order_key=None):
        result = {"status": "failure", "error": "Timeout"}
        if order_key:
            self.completed_transactions[order_key] = result
        return result

    def _create_order(self, order_data):
        # Simulate order creation. In a real system, this would involve database interactions.
        return "order456"

    def _process_payment(self, order_data):
        # Simulate payment processing. This might raise exceptions if payment fails.
        return True

    def _reserve_inventory(self, order_data):
        # Simulate inventory reservation. This might raise exceptions if inventory is insufficient.
        return True

    def _send_notification(self, order_data):
        # Simulate sending a notification (e.g., email) to the customer.
        return True

    def _rollback_create_order(self, order_id):
        # Simulate rollback of order creation if subsequent steps fail.
        return True

    def _rollback_payment(self, order_data):
        # Simulate rollback of payment (e.g., refund process).
        return True

    def _rollback_inventory(self, order_data):
        # Simulate rollback of inventory reservation (e.g., restock the items).
        return True