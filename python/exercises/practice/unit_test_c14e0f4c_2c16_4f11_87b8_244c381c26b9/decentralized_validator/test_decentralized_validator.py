import unittest
import hashlib
from decentralized_validator.node import Node
from decentralized_validator.simulation import simulate_network

class TestDecentralizedValidator(unittest.TestCase):
    def setUp(self):
        self.nodes = [
            Node(0, 10, 3),
            Node(1, 15, 3),
            Node(2, 20, 3)
        ]
        self.transactions = [
            "tx1",
            "tx2",
            "tx3"
        ]

    def test_node_initialization(self):
        node = self.nodes[0]
        self.assertEqual(node.node_id, 0)
        self.assertEqual(node.computational_power, 10)
        self.assertEqual(node.network_size, 3)
        self.assertEqual(node.get_global_state(), "")

    def test_state_transition(self):
        node = self.nodes[0]
        initial_state = node.get_global_state()
        new_state = hashlib.sha256((initial_state + "tx1").encode()).hexdigest()
        
        # Mock validation results to force commit
        validation_results = {0: True, 1: True, 2: True}
        node.commit_transaction("tx1", validation_results)
        self.assertEqual(node.get_global_state(), new_state)

    def test_weighted_majority_commit(self):
        node = self.nodes[0]
        # Test case where weighted majority approves
        validation_results = {0: True, 1: True, 2: False}  # Total weight 25 vs 20
        committed = node.commit_transaction("tx1", validation_results)
        self.assertTrue(committed)

        # Test case where weighted majority rejects
        validation_results = {0: False, 1: False, 2: True}  # Total weight 25 vs 20
        committed = node.commit_transaction("tx2", validation_results)
        self.assertFalse(committed)

    def test_validation_accuracy(self):
        node = self.nodes[0]
        # Run multiple validations to test probability
        true_count = 0
        for _ in range(1000):
            if node.validate_transaction("tx1", ""):
                true_count += 1
        # Should be mostly correct due to high computational power
        self.assertGreater(true_count, 900)

    def test_simulation_convergence(self):
        final_states = simulate_network(self.nodes, self.transactions)
        # After simulation, nodes should mostly agree on final state
        self.assertEqual(len(set(final_states.values())), 1)

    def test_empty_transactions(self):
        final_states = simulate_network(self.nodes, [])
        # All nodes should maintain empty state
        for state in final_states.values():
            self.assertEqual(state, "")

    def test_single_node_network(self):
        single_node = [Node(0, 10, 1)]
        final_states = simulate_network(single_node, ["tx1"])
        self.assertEqual(final_states[0], hashlib.sha256("tx1".encode()).hexdigest())

    def test_tie_breaker_scenario(self):
        # Create network with even weights
        nodes = [Node(0, 10, 2), Node(1, 10, 2)]
        # Test case where validation is split
        validation_results = {0: True, 1: False}
        committed = nodes[0].commit_transaction("tx1", validation_results)
        # In case of tie, should not commit
        self.assertFalse(committed)

if __name__ == '__main__':
    unittest.main()