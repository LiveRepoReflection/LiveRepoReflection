import unittest
from unittest.mock import Mock, patch
import threading
import time
from transaction_flow import (
    orchestrate_transaction,
    ServiceError
)

class MockService:
    def __init__(self, name, failure_actions=None, rollback_failures=None, delay=0):
        self.name = name
        self.failure_actions = failure_actions or []
        self.rollback_failures = rollback_failures or []
        self.delay = delay
        self.transaction_log = {}
        self.perform_count = {}
        self.lock = threading.Lock()
        
    def perform(self, action, data):
        # Simulate delay
        if self.delay > 0:
            time.sleep(self.delay)
            
        with self.lock:
            # Track number of attempts for this action
            key = f"{action}:{str(data)}"
            self.perform_count[key] = self.perform_count.get(key, 0) + 1
            
            # Check if this is a failing action
            if action in self.failure_actions:
                if self.perform_count[key] <= 3:  # Allow retries to succeed on the 4th attempt
                    raise ServiceError(f"Service {self.name} failed to perform {action}")
            
            # Generate a transaction ID
            transaction_id = f"{self.name}-{action}-{hash(str(data))}"
            
            # Store transaction for potential rollback
            self.transaction_log[transaction_id] = (action, data)
            
            # Return the transaction ID
            return transaction_id
    
    def rollback(self, action, transaction_id):
        # Simulate delay
        if self.delay > 0:
            time.sleep(self.delay)
            
        with self.lock:
            # Check if this transaction exists
            if transaction_id not in self.transaction_log:
                # Idempotent behavior: if already rolled back, just return success
                return True
            
            # Check if rollback should fail
            if action in self.rollback_failures:
                raise ServiceError(f"Service {self.name} failed to rollback {action}")
            
            # Remove from log to simulate successful rollback
            if transaction_id in self.transaction_log:
                del self.transaction_log[transaction_id]
                
            return True

class TransactionFlowTest(unittest.TestCase):

    def setUp(self):
        # Create mock services
        self.inventory_service = MockService("InventoryService")
        self.payment_service = MockService("PaymentService")
        self.order_service = MockService("OrderService")
        self.shipping_service = MockService("ShippingService")
        
        # Dictionary of services
        self.services = {
            "InventoryService": self.inventory_service,
            "PaymentService": self.payment_service,
            "OrderService": self.order_service,
            "ShippingService": self.shipping_service
        }
        
        # Sample operations
        self.sample_operations = [
            ("InventoryService", "reserve_item", {"item_id": 123, "quantity": 1}),
            ("PaymentService", "charge", {"user_id": 456, "amount": 99.99}),
            ("OrderService", "create_order", {"user_id": 456, "items": [123]}),
            ("ShippingService", "schedule_delivery", {"order_id": 789, "address": "123 Main St"})
        ]

    def test_successful_transaction(self):
        result = orchestrate_transaction(self.sample_operations, self.services)
        self.assertTrue(result)
        
        # Check that all services performed their operations
        self.assertIn("reserve_item:{'item_id': 123, 'quantity': 1}", self.inventory_service.perform_count)
        self.assertIn("charge:{'user_id': 456, 'amount': 99.99}", self.payment_service.perform_count)
        self.assertIn("create_order:{'user_id': 456, 'items': [123]}", self.order_service.perform_count)
        self.assertIn("schedule_delivery:{'order_id': 789, 'address': '123 Main St'}", self.shipping_service.perform_count)
        
        # Check that transactions were recorded
        for service in self.services.values():
            self.assertTrue(len(service.transaction_log) > 0)

    def test_failed_transaction_rollback(self):
        # Setup payment service to fail
        failing_service = MockService("PaymentService", failure_actions=["charge"])
        self.services["PaymentService"] = failing_service
        
        result = orchestrate_transaction(self.sample_operations, self.services)
        self.assertFalse(result)
        
        # Check that inventory was rolledback (no active transactions)
        self.assertEqual(len(self.inventory_service.transaction_log), 0)
        
        # Check that payment service attempted to perform the action
        self.assertIn("charge:{'user_id': 456, 'amount': 99.99}", failing_service.perform_count)
        
        # Check that later operations weren't executed
        self.assertNotIn("create_order:{'user_id': 456, 'items': [123]}", self.order_service.perform_count)
        self.assertNotIn("schedule_delivery:{'order_id': 789, 'address': '123 Main St'}", self.shipping_service.perform_count)

    def test_retry_on_failure(self):
        # Service that will fail twice but succeed on third attempt
        retryable_service = MockService("PaymentService", failure_actions=["charge"])
        self.services["PaymentService"] = retryable_service
        
        # Override perform method to succeed on third try
        original_perform = retryable_service.perform
        def mock_perform(action, data):
            key = f"{action}:{str(data)}"
            count = retryable_service.perform_count.get(key, 0) + 1
            retryable_service.perform_count[key] = count
            
            if action in retryable_service.failure_actions and count < 3:
                raise ServiceError(f"Service {retryable_service.name} failed to perform {action}")
            
            # Generate transaction ID
            transaction_id = f"{retryable_service.name}-{action}-{hash(str(data))}"
            retryable_service.transaction_log[transaction_id] = (action, data)
            return transaction_id
            
        retryable_service.perform = mock_perform
        
        result = orchestrate_transaction(self.sample_operations, self.services)
        self.assertTrue(result)
        
        # Check that payment service attempted multiple times
        self.assertEqual(retryable_service.perform_count.get("charge:{'user_id': 456, 'amount': 99.99}", 0), 3)
        
        # Check that later operations were executed
        self.assertIn("create_order:{'user_id': 456, 'items': [123]}", self.order_service.perform_count)
        self.assertIn("schedule_delivery:{'order_id': 789, 'address': '123 Main St'}", self.shipping_service.perform_count)

    def test_rollback_failure(self):
        # Setup inventory service to fail during rollback
        self.inventory_service = MockService("InventoryService")
        # Payment service will fail on perform
        self.payment_service = MockService("PaymentService", failure_actions=["charge"])
        
        self.services = {
            "InventoryService": self.inventory_service,
            "PaymentService": self.payment_service,
            "OrderService": self.order_service,
            "ShippingService": self.shipping_service
        }
        
        with patch.object(self.inventory_service, 'rollback', side_effect=ServiceError("Rollback failed")):
            result = orchestrate_transaction(self.sample_operations, self.services)
            self.assertFalse(result)
    
    def test_idempotent_rollback(self):
        # Service that has already rolled back a transaction
        idempotent_service = MockService("InventoryService")
        self.services["InventoryService"] = idempotent_service
        
        # First, perform an operation
        tx_id = idempotent_service.perform("reserve_item", {"item_id": 123, "quantity": 1})
        
        # Now simulate it's already been rolled back
        idempotent_service.rollback("reserve_item", tx_id)
        
        # Setup payment to fail so rollback is triggered
        self.payment_service = MockService("PaymentService", failure_actions=["charge"])
        self.services["PaymentService"] = self.payment_service
        
        result = orchestrate_transaction(self.sample_operations, self.services)
        self.assertFalse(result)
        
        # The inventory service should have been asked to rollback again (idempotent)
        # and that should have succeeded despite the transaction being already rolled back

    def test_concurrent_transactions(self):
        # Test that multiple concurrent transactions work correctly
        results = []
        threads = []
        
        # Create multiple operations sets with different data
        operations_list = []
        for i in range(5):
            ops = [
                ("InventoryService", "reserve_item", {"item_id": 100+i, "quantity": 1}),
                ("PaymentService", "charge", {"user_id": 400+i, "amount": 99.99}),
                ("OrderService", "create_order", {"user_id": 400+i, "items": [100+i]}),
                ("ShippingService", "schedule_delivery", {"order_id": 700+i, "address": f"{i} Main St"})
            ]
            operations_list.append(ops)
        
        # Function to run in thread
        def run_transaction(ops, idx):
            result = orchestrate_transaction(ops, self.services)
            results.append((idx, result))
        
        # Start all threads
        for i, ops in enumerate(operations_list):
            thread = threading.Thread(target=run_transaction, args=(ops, i))
            threads.append(thread)
            thread.start()
        
        # Wait for all to complete
        for thread in threads:
            thread.join()
        
        # All should have succeeded
        for idx, result in results:
            self.assertTrue(result, f"Transaction {idx} failed")
        
        # Check that correct number of transactions were performed
        total_ops = 0
        for service in self.services.values():
            total_ops += len(service.perform_count)
        
        # 4 operations per transaction * 5 transactions = 20 operations
        self.assertEqual(total_ops, 20)

    def test_service_delay(self):
        # Test with a service that has significant delay
        slow_service = MockService("PaymentService", delay=0.1)  # 100ms delay
        self.services["PaymentService"] = slow_service
        
        start_time = time.time()
        result = orchestrate_transaction(self.sample_operations, self.services)
        end_time = time.time()
        
        self.assertTrue(result)
        # Ensure it took at least the delay time
        self.assertGreaterEqual(end_time - start_time, 0.1)

    def test_empty_operations_list(self):
        # Test with empty operations list
        result = orchestrate_transaction([], self.services)
        self.assertTrue(result)
        
        # No services should have been called
        for service in self.services.values():
            self.assertEqual(len(service.perform_count), 0)

    def test_missing_service(self):
        # Test with an operation that references a non-existent service
        operations = [
            ("NonExistentService", "do_something", {"data": "value"})
        ]
        
        result = orchestrate_transaction(operations, self.services)
        self.assertFalse(result)

if __name__ == '__main__':
    unittest.main()