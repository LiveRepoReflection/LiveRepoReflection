import unittest
import threading
from time import sleep

# Import the SagaCoordinator class from the dtc_saga module.
from dtc_saga import SagaCoordinator

# Define a DummyService to simulate each microservice behavior.
class DummyService:
    def __init__(self, name, succeed=True):
        self.name = name
        self.succeed = succeed
        self.call_count = 0
        self.compensate_count = 0

    def process(self, order):
        self.call_count += 1
        if self.succeed:
            return True
        else:
            raise Exception(f"{self.name} failure.")

    def compensate(self, order):
        self.compensate_count += 1
        return True

class TestSagaCoordinator(unittest.TestCase):
    def setUp(self):
        # Initialize dummy services with default success.
        self.inventory = DummyService("InventoryService", succeed=True)
        self.payment = DummyService("PaymentService", succeed=True)
        self.shipping = DummyService("ShippingService", succeed=True)
        self.order_service = DummyService("OrderService", succeed=True)
        # Create a coordinator instance.
        self.coordinator = SagaCoordinator(
            inventory_service=self.inventory,
            payment_service=self.payment,
            shipping_service=self.shipping,
            order_service=self.order_service
        )

    def test_successful_transaction(self):
        order = {"order_id": "order123", "details": "normal order"}
        result = self.coordinator.process_order(order)
        self.assertEqual(result, "SUCCESS")
        # Each service should have processed the order exactly once.
        self.assertEqual(self.inventory.call_count, 1)
        self.assertEqual(self.payment.call_count, 1)
        self.assertEqual(self.shipping.call_count, 1)
        self.assertEqual(self.order_service.call_count, 1)
        # Saga state should be marked as completed.
        self.assertEqual(self.coordinator.saga_states.get(order["order_id"]), "COMPLETED")

    def test_inventory_failure(self):
        # Simulate failure in the InventoryService.
        self.inventory.succeed = False
        order = {"order_id": "order124", "details": "inventory failure test"}
        with self.assertRaises(Exception) as context:
            self.coordinator.process_order(order)
        self.assertIn("InventoryService failure", str(context.exception))
        # Verify that the inventory service was called.
        self.assertEqual(self.inventory.call_count, 1)
        # No further services should have been invoked.
        self.assertEqual(self.payment.call_count, 0)
        self.assertEqual(self.shipping.call_count, 0)
        self.assertEqual(self.order_service.call_count, 0)
        # Saga state should be marked as compensated.
        self.assertEqual(self.coordinator.saga_states.get(order["order_id"]), "COMPENSATED")

    def test_payment_failure(self):
        # Simulate failure in the PaymentService.
        self.payment.succeed = False
        order = {"order_id": "order125", "details": "payment failure test"}
        with self.assertRaises(Exception) as context:
            self.coordinator.process_order(order)
        self.assertIn("PaymentService failure", str(context.exception))
        self.assertEqual(self.inventory.call_count, 1)
        self.assertEqual(self.payment.call_count, 1)
        # Shipping and OrderService should not have been attempted.
        self.assertEqual(self.shipping.call_count, 0)
        self.assertEqual(self.order_service.call_count, 0)
        # Compensation should be triggered for the successful services.
        self.assertEqual(self.inventory.compensate_count, 1)
        self.assertEqual(self.coordinator.saga_states.get(order["order_id"]), "COMPENSATED")

    def test_shipping_failure(self):
        # Simulate failure in the ShippingService.
        self.shipping.succeed = False
        order = {"order_id": "order126", "details": "shipping failure test"}
        with self.assertRaises(Exception) as context:
            self.coordinator.process_order(order)
        self.assertIn("ShippingService failure", str(context.exception))
        self.assertEqual(self.inventory.call_count, 1)
        self.assertEqual(self.payment.call_count, 1)
        self.assertEqual(self.shipping.call_count, 1)
        # OrderService should not be reached.
        self.assertEqual(self.order_service.call_count, 0)
        # Compensation should be triggered for Inventory and Payment.
        self.assertEqual(self.inventory.compensate_count, 1)
        self.assertEqual(self.payment.compensate_count, 1)
        self.assertEqual(self.coordinator.saga_states.get(order["order_id"]), "COMPENSATED")

    def test_idempotency(self):
        # Process the same order twice to test idempotency.
        order = {"order_id": "order127", "details": "idempotency test"}
        first_result = self.coordinator.process_order(order)
        second_result = self.coordinator.process_order(order)  # Duplicate processing
        self.assertEqual(first_result, "SUCCESS")
        self.assertEqual(second_result, "SUCCESS")
        # Services should have processed the order only once.
        self.assertEqual(self.inventory.call_count, 1)
        self.assertEqual(self.payment.call_count, 1)
        self.assertEqual(self.shipping.call_count, 1)
        self.assertEqual(self.order_service.call_count, 1)
        self.assertEqual(self.coordinator.saga_states.get(order["order_id"]), "COMPLETED")

    def test_concurrent_transactions(self):
        orders = [{"order_id": f"order_thread_{i}", "details": f"concurrent order {i}"} for i in range(10)]
        results = {}

        def process_order(order):
            try:
                res = self.coordinator.process_order(order)
                results[order["order_id"]] = res
            except Exception as e:
                results[order["order_id"]] = str(e)

        threads = [threading.Thread(target=process_order, args=(order,)) for order in orders]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        # Verify that all transactions succeed.
        for order in orders:
            self.assertEqual(results[order["order_id"]], "SUCCESS")
            self.assertEqual(self.coordinator.saga_states.get(order["order_id"]), "COMPLETED")

    def test_durability(self):
        # Process an order and simulate a coordinator restart.
        order = {"order_id": "order128", "details": "durability test"}
        result = self.coordinator.process_order(order)
        self.assertEqual(result, "SUCCESS")
        # Simulate storing persistent state.
        persistent_state = self.coordinator.persistent_state
        # Create a new coordinator instance with the same persistent state.
        new_coordinator = SagaCoordinator(
            inventory_service=self.inventory,
            payment_service=self.payment,
            shipping_service=self.shipping,
            order_service=self.order_service,
            persistent_state=persistent_state
        )
        # Check that the saga state for the order is retained.
        self.assertEqual(new_coordinator.saga_states.get(order["order_id"]), "COMPLETED")

if __name__ == "__main__":
    unittest.main()