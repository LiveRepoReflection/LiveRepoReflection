import threading

class SagaCoordinator:
    def __init__(self, inventory_service, payment_service, shipping_service, order_service, persistent_state=None):
        self.inventory_service = inventory_service
        self.payment_service = payment_service
        self.shipping_service = shipping_service
        self.order_service = order_service
        if persistent_state is None:
            self.persistent_state = {}
        else:
            self.persistent_state = persistent_state
        # Use persistent_state as the saga state storage
        self.saga_states = self.persistent_state
        self.lock = threading.Lock()

    def process_order(self, order):
        order_id = order.get("order_id")
        if order_id is None:
            raise Exception("Order must have an 'order_id'")
        with self.lock:
            # Idempotency: if order already processed successfully, return success.
            if order_id in self.saga_states and self.saga_states[order_id] == "COMPLETED":
                return "SUCCESS"

        successful_steps = []
        # Define the processing order for the Saga
        steps = [
            (self.inventory_service, "InventoryService"),
            (self.payment_service, "PaymentService"),
            (self.shipping_service, "ShippingService"),
            (self.order_service, "OrderService")
        ]

        try:
            # Execute the saga steps sequentially
            for service, service_name in steps:
                service.process(order)
                successful_steps.append(service)
            with self.lock:
                self.saga_states[order_id] = "COMPLETED"
            return "SUCCESS"
        except Exception as e:
            # Compensation: reverse the successful steps to rollback changes
            for service in reversed(successful_steps):
                try:
                    service.compensate(order)
                except Exception:
                    # Ignore compensation errors
                    pass
            with self.lock:
                self.saga_states[order_id] = "COMPENSATED"
            raise e