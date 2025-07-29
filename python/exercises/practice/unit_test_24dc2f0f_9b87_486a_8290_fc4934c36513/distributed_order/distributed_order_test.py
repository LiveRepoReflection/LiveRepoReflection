import unittest
import threading
import time

from distributed_order import (
    place_order,
    reserve_inventory,
    process_payment,
    schedule_shipping,
    send_confirmation_notification,
    compensate_inventory_reservation,
    refund_payment,
    cancel_shipping,
    resend_confirmation_notification,
    inventory,
    payment_records,
    item_prices,
    blacklist_order_ids,
    shipping_error_order_ids,
    inventory_lock,
    payment_lock,
    shipping_lock,
    notification_lock,
)

class DistributedOrderTest(unittest.TestCase):

    def setUp(self):
        # Reset shared resources
        with inventory_lock:
            inventory.clear()
        with payment_lock:
            payment_records.clear()
        item_prices.clear()
        blacklist_order_ids.clear()
        shipping_error_order_ids.clear()

        # Initialize inventory and pricing
        with inventory_lock:
            inventory.update({
                "item1": 5,
                "item2": 5,
            })
        item_prices.update({
            "item1": 10.0,
            "item2": 20.0,
        })

    def test_order_success(self):
        order_id = "order_success"
        user_id = "user123"
        payment_info = {"credit_card": "1234-5678"}
        shipping_address = {"street": "123 Main St", "city": "Testville"}
        items = [{"item_id": "item1", "quantity": 2}, {"item_id": "item2", "quantity": 3}]
        result = place_order(order_id, items, user_id, payment_info, shipping_address)
        self.assertTrue(result)
        with payment_lock:
            self.assertEqual(payment_records.get(order_id), 'processed')
        with inventory_lock:
            self.assertEqual(inventory["item1"], 5 - 2)
            self.assertEqual(inventory["item2"], 5 - 3)

    def test_inventory_failure(self):
        order_id = "order_inv_fail"
        user_id = "user123"
        payment_info = {"credit_card": "1111-2222"}
        shipping_address = {"street": "456 Side Rd", "city": "Testville"}
        # Request more than available inventory
        items = [{"item_id": "item1", "quantity": 10}]
        result = place_order(order_id, items, user_id, payment_info, shipping_address)
        self.assertFalse(result)
        with inventory_lock:
            # Inventory should remain unchanged
            self.assertEqual(inventory["item1"], 5)

    def test_payment_failure(self):
        order_id = "order_payment_fail"
        user_id = "user456"
        payment_info = {"credit_card": "3333-4444"}
        shipping_address = {"street": "789 Other Ave", "city": "Testopolis"}
        items = [{"item_id": "item1", "quantity": 1}]
        # Simulate payment failure by adding order id to blacklist
        blacklist_order_ids.add(order_id)
        result = place_order(order_id, items, user_id, payment_info, shipping_address)
        self.assertFalse(result)
        with inventory_lock:
            # Inventory should be restored if compensation was triggered
            self.assertEqual(inventory["item1"], 5)
        with payment_lock:
            self.assertNotIn(order_id, payment_records)

    def test_shipping_failure(self):
        order_id = "order_shipping_fail"
        user_id = "user789"
        payment_info = {"credit_card": "5555-6666"}
        shipping_address = {"street": "321 Back Ln", "city": "Examplestan"}
        items = [{"item_id": "item2", "quantity": 2}]
        # Simulate shipping failure by adding order id to shipping error set
        shipping_error_order_ids.add(order_id)
        result = place_order(order_id, items, user_id, payment_info, shipping_address)
        self.assertFalse(result)
        with inventory_lock:
            self.assertEqual(inventory["item2"], 5)
        with payment_lock:
            self.assertNotIn(order_id, payment_records)

    def test_concurrent_orders(self):
        orders = []
        results = []
        threads = []

        def place(order_id):
            user_id = "concurrent_user"
            payment_info = {"credit_card": "7777-8888"}
            shipping_address = {"street": "654 Parallel Rd", "city": "Concurrentville"}
            items = [{"item_id": "item1", "quantity": 1}]
            res = place_order(order_id, items, user_id, payment_info, shipping_address)
            results.append((order_id, res))

        order_count = 5
        for i in range(order_count):
            order_id = f"concurrent_order_{i}"
            thread = threading.Thread(target=place, args=(order_id,))
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()

        self.assertEqual(len(results), order_count)
        for order_id, res in results:
            self.assertTrue(res)
        with inventory_lock:
            self.assertEqual(inventory["item1"], 5 - order_count)

if __name__ == '__main__':
    unittest.main()