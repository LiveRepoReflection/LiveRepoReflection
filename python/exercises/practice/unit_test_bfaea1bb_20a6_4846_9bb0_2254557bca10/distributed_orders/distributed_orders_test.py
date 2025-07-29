import unittest
import threading
from time import sleep
from unittest.mock import patch

# Import the function that processes the order from the distributed_orders module.
# It is assumed that 'process_order' is defined in distributed_orders.py.
from distributed_orders import process_order

def get_sample_order(order_id="order123"):
    return {
        "user_id": 1,
        "order_id": order_id,
        "items": [{"product_id": 101, "quantity": 2}],
        "payment_info": {
            "card_number": "4111111111111111",
            "expiry_date": "12/25",
            "amount": 100.00
        }
    }

class DistributedOrdersTest(unittest.TestCase):

    def test_successful_order(self):
        """Test that a valid order processes successfully."""
        order = get_sample_order()
        result = process_order(order)
        self.assertTrue(result, "Valid order should commit successfully")

    def test_missing_user_id(self):
        """Test that an order with missing user_id raises an error."""
        order = get_sample_order()
        order.pop("user_id")
        with self.assertRaises(ValueError):
            process_order(order)

    def test_missing_order_id(self):
        """Test that an order with missing order_id raises an error."""
        order = get_sample_order()
        order.pop("order_id")
        with self.assertRaises(ValueError):
            process_order(order)

    def test_missing_items(self):
        """Test that an order with missing items raises an error."""
        order = get_sample_order()
        order.pop("items")
        with self.assertRaises(ValueError):
            process_order(order)

    def test_missing_payment_info(self):
        """Test that an order with missing payment_info raises an error."""
        order = get_sample_order()
        order.pop("payment_info")
        with self.assertRaises(ValueError):
            process_order(order)

    def test_duplicate_order(self):
        """Test idempotency: processing the same order twice should yield the same result."""
        order = get_sample_order(order_id="dup_order")
        first_result = process_order(order)
        second_result = process_order(order)
        self.assertEqual(first_result, second_result, "Duplicate orders should be processed idempotently")

    def test_payment_failure(self):
        """Simulate PaymentService failure by patching the payment authorization to always fail."""
        order = get_sample_order(order_id="fail_payment")
        # Assuming that in the process_order function, PaymentService.authorize_payment is called.
        # We patch it to raise an Exception or return False to simulate failure.
        with patch("distributed_orders.PaymentService.authorize_payment", return_value=False):
            result = process_order(order)
            self.assertFalse(result, "Order should rollback when payment fails")

    def test_inventory_failure(self):
        """Simulate InventoryService failure by patching the inventory reservation to always fail."""
        order = get_sample_order(order_id="fail_inventory")
        # Assuming that in the process_order function, InventoryService.reserve_inventory is called.
        with patch("distributed_orders.InventoryService.reserve_inventory", side_effect=Exception("Inventory failure")):
            result = process_order(order)
            self.assertFalse(result, "Order should rollback when inventory reservation fails")

    def test_concurrent_orders(self):
        """Test that concurrent order processing does not interfere with each order's atomic transaction."""
        order_ids = [f"concurrent_{i}" for i in range(10)]
        results = {}
        lock = threading.Lock()

        def process_in_thread(order_id):
            order = get_sample_order(order_id=order_id)
            result = process_order(order)
            with lock:
                results[order_id] = result

        threads = []
        for order_id in order_ids:
            t = threading.Thread(target=process_in_thread, args=(order_id,))
            threads.append(t)
            t.start()

        for t in threads:
            t.join()

        # Verify that each concurrent order processed correctly (committed or rolled back appropriately).
        for order_id in order_ids:
            self.assertIn(order_id, results)
            # Since this is a valid order, we expect True in committed orders.
            # In real scenarios, transient failures might cause rollbacks even in valid orders.
            # Here we assume the implementation retries sufficiently so that valid orders commit.
            self.assertTrue(results[order_id], f"Concurrent order {order_id} should commit successfully")

if __name__ == '__main__':
    unittest.main()