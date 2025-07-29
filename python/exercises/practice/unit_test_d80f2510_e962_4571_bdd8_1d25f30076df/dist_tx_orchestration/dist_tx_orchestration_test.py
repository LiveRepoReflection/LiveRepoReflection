import unittest
import threading
import time

from dist_tx_orchestration import orchestrate_transaction

class DistributedTxOrchestrationTest(unittest.TestCase):
    def test_successful_transaction(self):
        # All operations succeed
        operations = [
            ("OrderService", "createOrder", {"order_id": 1}),
            ("InventoryService", "reserveItems", {"items": [1, 2, 3]}),
            ("PaymentService", "processPayment", {"amount": 100}),
            ("ShippingService", "scheduleShipment", {"address": "123 Main St"})
        ]
        result = orchestrate_transaction(operations)
        self.assertTrue(result)
    
    def test_failure_mid_transaction(self):
        # Simulate a failure in PaymentService by including "fail": True in payload.
        # The orchestrator should trigger compensations and return False.
        operations = [
            ("OrderService", "createOrder", {"order_id": 2}),
            ("InventoryService", "reserveItems", {"items": [4, 5, 6]}),
            ("PaymentService", "processPayment", {"amount": 200, "fail": True}),
            ("ShippingService", "scheduleShipment", {"address": "456 Elm St"})
        ]
        result = orchestrate_transaction(operations)
        self.assertFalse(result)
    
    def test_timeout_handling(self):
        # Simulate a timeout scenario in ShippingService by adding a delay longer than allowed.
        # Assume that the orchestrator regards any operation exceeding the 10-second timeout as a failure.
        operations = [
            ("OrderService", "createOrder", {"order_id": 3}),
            ("InventoryService", "reserveItems", {"items": [7, 8, 9]}),
            ("PaymentService", "processPayment", {"amount": 300}),
            ("ShippingService", "scheduleShipment", {"address": "789 Oak St", "delay": 11})
        ]
        result = orchestrate_transaction(operations)
        self.assertFalse(result)
    
    def test_concurrent_transactions(self):
        # Run multiple transactions concurrently to test isolation and concurrency support.
        results = []
        lock = threading.Lock()

        def run_transaction(order_id):
            ops = [
                ("OrderService", "createOrder", {"order_id": order_id}),
                ("InventoryService", "reserveItems", {"items": [order_id, order_id + 1]}),
                ("PaymentService", "processPayment", {"amount": 50 * order_id}),
                ("ShippingService", "scheduleShipment", {"address": f"{order_id} Main Ave"})
            ]
            res = orchestrate_transaction(ops)
            with lock:
                results.append(res)
        
        threads = []
        for i in range(5):
            t = threading.Thread(target=run_transaction, args=(i + 10,))
            threads.append(t)
            t.start()
        
        for t in threads:
            t.join()
        
        # In a fully functioning system, all transactions should succeed.
        for res in results:
            self.assertTrue(res)

if __name__ == '__main__':
    unittest.main()