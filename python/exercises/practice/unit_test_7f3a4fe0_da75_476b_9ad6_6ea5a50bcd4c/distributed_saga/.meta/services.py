class InventoryError(Exception):
    pass

class PaymentError(Exception):
    pass

class OrderError(Exception):
    pass

class InventoryService:
    def reserve_inventory(self, order_details):
        """Reserves the inventory for the given order.
        Raises InventoryError on failure."""
        pass

    def release_inventory(self, order_details):
        """Releases the reserved inventory. Idempotent."""
        pass

class PaymentService:
    def process_payment(self, order_details):
        """Processes the payment for the order.
        Raises PaymentError on failure."""
        pass

    def refund_payment(self, order_details):
        """Refunds the payment. Idempotent."""
        pass

class OrderService:
    def create_order(self, order_details):
        """Creates the order record.
        Raises OrderError on failure."""
        pass

class NotificationService:
    def send_confirmation(self, order_details):
        """Sends a confirmation email. No compensation required."""
        pass