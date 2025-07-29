import unittest
import time
import threading
from txn_coordinator.txn_coordinator import Node, TransactionCoordinator

class TestNode(unittest.TestCase):
    def setUp(self):
        self.node = Node("test_node")
    
    def test_initialization(self):
        self.assertEqual(self.node.node_id, "test_node")
        self.assertIsNone(self.node.current_operation)
    
    def test_prepare_success(self):
        self.assertTrue(self.node.prepare("test_operation"))
        self.assertEqual(self.node.current_operation, "test_operation")
    
    def test_commit(self):
        self.node.prepare("test_operation")
        self.node.commit()
        self.assertIsNone(self.node.current_operation)
    
    def test_rollback(self):
        self.node.prepare("test_operation")
        self.node.rollback()
        self.assertIsNone(self.node.current_operation)

class MockNode(Node):
    def __init__(self, node_id, prepare_success=True, prepare_delay=0):
        super().__init__(node_id)
        self.prepare_success = prepare_success
        self.prepare_delay = prepare_delay
        self.prepare_called = False
        self.commit_called = False
        self.rollback_called = False

    def prepare(self, operation):
        self.prepare_called = True
        self.current_operation = operation
        if self.prepare_delay > 0:
            time.sleep(self.prepare_delay)
        return self.prepare_success

    def commit(self):
        self.commit_called = True
        self.current_operation = None

    def rollback(self):
        self.rollback_called = True
        self.current_operation = None

class TestTransactionCoordinator(unittest.TestCase):
    def setUp(self):
        self.coordinator = TransactionCoordinator(timeout=2)
        self.node1 = MockNode("node1")
        self.node2 = MockNode("node2")
        self.coordinator.register_node(self.node1)
        self.coordinator.register_node(self.node2)
    
    def test_initialization(self):
        self.assertEqual(self.coordinator.timeout, 2)
        self.assertEqual(len(self.coordinator.nodes), 2)
    
    def test_register_node(self):
        node3 = MockNode("node3")
        self.coordinator.register_node(node3)
        self.assertIn("node3", self.coordinator.nodes)
    
    def test_register_duplicate_node(self):
        with self.assertRaises(ValueError):
            self.coordinator.register_node(MockNode("node1"))
    
    def test_transaction_success(self):
        operations = [
            ("node1", "operation1"),
            ("node2", "operation2")
        ]
        result = self.coordinator.execute_transaction(operations)
        self.assertTrue(result)
        self.assertTrue(self.node1.commit_called)
        self.assertTrue(self.node2.commit_called)
    
    def test_transaction_failure_one_node_fails(self):
        self.node1.prepare_success = False
        operations = [
            ("node1", "operation1"),
            ("node2", "operation2")
        ]
        result = self.coordinator.execute_transaction(operations)
        self.assertFalse(result)
        self.assertTrue(self.node1.rollback_called)
        self.assertTrue(self.node2.rollback_called)
    
    def test_transaction_timeout(self):
        self.node1.prepare_delay = 3  # Greater than coordinator timeout
        operations = [
            ("node1", "operation1"),
            ("node2", "operation2")
        ]
        result = self.coordinator.execute_transaction(operations)
        self.assertFalse(result)
        # node1 might not get rollback called due to the timeout
        self.assertTrue(self.node2.rollback_called)
    
    def test_transaction_with_nonexistent_node(self):
        operations = [
            ("node1", "operation1"),
            ("nonexistent", "operation2")
        ]
        with self.assertRaises(ValueError):
            self.coordinator.execute_transaction(operations)
    
    def test_concurrent_transaction_execution(self):
        # This test simulates multiple transactions being executed concurrently
        coordinator = TransactionCoordinator(timeout=2)
        nodes = [MockNode(f"node{i}") for i in range(5)]
        for node in nodes:
            coordinator.register_node(node)
        
        def execute_transaction(node_ids):
            operations = [(node_id, f"op_{node_id}") for node_id in node_ids]
            return coordinator.execute_transaction(operations)
        
        # Create 3 concurrent transactions
        txn1 = threading.Thread(target=execute_transaction, args=(["node0", "node1"],))
        txn2 = threading.Thread(target=execute_transaction, args=(["node2", "node3"],))
        txn3 = threading.Thread(target=execute_transaction, args=(["node1", "node4"],))
        
        # Start all transactions and wait for them to finish
        txn1.start()
        txn2.start()
        txn3.start()
        
        txn1.join()
        txn2.join()
        txn3.join()
        
        # Verify all nodes were either committed or rolled back
        for node in nodes:
            self.assertTrue(node.commit_called or node.rollback_called)
    
    def test_empty_operations_list(self):
        result = self.coordinator.execute_transaction([])
        self.assertTrue(result)  # Empty transaction should succeed trivially

if __name__ == '__main__':
    unittest.main()