import unittest
from raft_transaction import TransactionSimulator

class RaftTransactionTest(unittest.TestCase):
    def test_successful_transaction_with_minimum_nodes(self):
        # Test successful transaction with the minimum number of nodes (3)
        simulator = TransactionSimulator(3)
        success = simulator.propose_transaction(0, "x", "1")
        
        self.assertTrue(success)
        
        # Check that all nodes have the transaction in their key-value store
        for node_id in range(3):
            self.assertEqual(simulator.get_node_data(node_id), {"x": "1"})
            
        # Check that all nodes have the transaction in their log
        expected_log = [{"key": "x", "value": "1"}]
        for node_id in range(3):
            self.assertEqual(simulator.get_node_log(node_id), expected_log)

    def test_successful_transaction_with_more_nodes(self):
        # Test successful transaction with more nodes (5)
        simulator = TransactionSimulator(5)
        success = simulator.propose_transaction(0, "x", "1")
        
        self.assertTrue(success)
        
        # Check that all nodes have the transaction in their key-value store
        for node_id in range(5):
            self.assertEqual(simulator.get_node_data(node_id), {"x": "1"})
            
        # Check that all nodes have the transaction in their log
        expected_log = [{"key": "x", "value": "1"}]
        for node_id in range(5):
            self.assertEqual(simulator.get_node_log(node_id), expected_log)

    def test_multiple_successful_transactions(self):
        # Test multiple successful transactions
        simulator = TransactionSimulator(3)
        
        # First transaction
        success1 = simulator.propose_transaction(0, "x", "1")
        self.assertTrue(success1)
        
        # Second transaction
        success2 = simulator.propose_transaction(0, "y", "2")
        self.assertTrue(success2)
        
        # Third transaction - updating an existing key
        success3 = simulator.propose_transaction(0, "x", "3")
        self.assertTrue(success3)
        
        # Check key-value store on all nodes
        expected_data = {"x": "3", "y": "2"}
        for node_id in range(3):
            self.assertEqual(simulator.get_node_data(node_id), expected_data)
            
        # Check logs on all nodes
        expected_log = [
            {"key": "x", "value": "1"},
            {"key": "y", "value": "2"},
            {"key": "x", "value": "3"}
        ]
        for node_id in range(3):
            self.assertEqual(simulator.get_node_log(node_id), expected_log)

    def test_non_leader_transaction_fails(self):
        # Test that a transaction proposed by a non-leader node fails
        simulator = TransactionSimulator(5)
        
        # First, a successful transaction from the leader
        success1 = simulator.propose_transaction(0, "x", "1")
        self.assertTrue(success1)
        
        # Now, a failed transaction from a non-leader
        success2 = simulator.propose_transaction(1, "y", "2")
        self.assertFalse(success2)
        
        # Check key-value store on all nodes - should only contain first transaction
        expected_data = {"x": "1"}
        for node_id in range(5):
            self.assertEqual(simulator.get_node_data(node_id), expected_data)
            
        # Check logs on all nodes - should contain both transactions
        # even though the second one failed
        expected_log = [
            {"key": "x", "value": "1"},
            {"key": "y", "value": "2"}
        ]
        for node_id in range(5):
            self.assertEqual(simulator.get_node_log(node_id), expected_log)

    def test_large_number_of_nodes(self):
        # Test with a larger number of nodes (11)
        simulator = TransactionSimulator(11)
        success = simulator.propose_transaction(0, "x", "1")
        
        self.assertTrue(success)
        
        # Check key-value store and logs on all nodes
        for node_id in range(11):
            self.assertEqual(simulator.get_node_data(node_id), {"x": "1"})
            self.assertEqual(simulator.get_node_log(node_id), [{"key": "x", "value": "1"}])

    def test_multiple_transactions_with_different_keys(self):
        # Test multiple transactions with different keys
        simulator = TransactionSimulator(5)
        
        # Propose multiple transactions
        keys = ["a", "b", "c", "d", "e"]
        values = ["1", "2", "3", "4", "5"]
        
        for i in range(len(keys)):
            success = simulator.propose_transaction(0, keys[i], values[i])
            self.assertTrue(success)
        
        # Check key-value store on all nodes
        expected_data = dict(zip(keys, values))
        for node_id in range(5):
            self.assertEqual(simulator.get_node_data(node_id), expected_data)
        
        # Check logs on all nodes
        expected_log = [{"key": keys[i], "value": values[i]} for i in range(len(keys))]
        for node_id in range(5):
            self.assertEqual(simulator.get_node_log(node_id), expected_log)

    def test_transaction_with_empty_key_or_value(self):
        # Test transactions with empty keys or values
        simulator = TransactionSimulator(3)
        
        # Empty key
        success1 = simulator.propose_transaction(0, "", "value")
        self.assertTrue(success1)
        
        # Empty value
        success2 = simulator.propose_transaction(0, "key", "")
        self.assertTrue(success2)
        
        # Check key-value store on all nodes
        expected_data = {"": "value", "key": ""}
        for node_id in range(3):
            self.assertEqual(simulator.get_node_data(node_id), expected_data)
        
        # Check logs on all nodes
        expected_log = [
            {"key": "", "value": "value"},
            {"key": "key", "value": ""}
        ]
        for node_id in range(3):
            self.assertEqual(simulator.get_node_log(node_id), expected_log)

    def test_transaction_with_same_key_multiple_times(self):
        # Test updating the same key multiple times
        simulator = TransactionSimulator(7)
        
        # Update the same key multiple times
        for i in range(5):
            success = simulator.propose_transaction(0, "counter", str(i))
            self.assertTrue(success)
        
        # Check key-value store on all nodes - should have the latest value
        expected_data = {"counter": "4"}
        for node_id in range(7):
            self.assertEqual(simulator.get_node_data(node_id), expected_data)
        
        # Check logs on all nodes - should contain all transactions
        expected_log = [{"key": "counter", "value": str(i)} for i in range(5)]
        for node_id in range(7):
            self.assertEqual(simulator.get_node_log(node_id), expected_log)

    def test_simulation_with_minimum_nodes_for_majority(self):
        # Test with minimal majority (e.g., 2 out of 3)
        simulator = TransactionSimulator(3)
        success = simulator.propose_transaction(0, "x", "1")
        
        self.assertTrue(success)
        
        # Verify that at least 2 nodes (majority) have the transaction
        nodes_with_transaction = 0
        for node_id in range(3):
            if simulator.get_node_data(node_id).get("x") == "1":
                nodes_with_transaction += 1
        
        self.assertGreaterEqual(nodes_with_transaction, 2)

if __name__ == "__main__":
    unittest.main()