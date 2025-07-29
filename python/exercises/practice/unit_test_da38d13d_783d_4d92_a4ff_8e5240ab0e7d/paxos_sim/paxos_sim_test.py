import unittest
from paxos_sim import simulate_paxos

class PaxosSimTest(unittest.TestCase):
    def test_consensus_reached(self):
        # Test a scenario with 5 non-faulty nodes and enough simulation steps to reach consensus
        N = 5
        F = 0
        proposals = [10, 20, 30, 40, 50]
        max_steps = 1000
        result = simulate_paxos(N, F, proposals, max_steps)
        # Verify that all nodes are present in the result
        self.assertEqual(set(result.keys()), set(range(N)))
        
        # Filter out nodes that did not learn any value (None)
        learned_values = [v for v in result.values() if v is not None]
        # At least one non-faulty node should have learned the value
        self.assertTrue(len(learned_values) > 0, "No node reached consensus within max_steps")
        
        # All non-None learned values must be identical
        consensus_value = learned_values[0]
        for value in learned_values:
            self.assertEqual(value, consensus_value)
        
        # The consensus value must be one of the proposed values
        self.assertIn(consensus_value, proposals)

    def test_timeout_without_consensus(self):
        # Test scenario with max_steps too low for the consensus to be reached.
        N = 5
        F = 0
        proposals = [1, 2, 3, 4, 5]
        max_steps = 1  # Not enough time steps
        result = simulate_paxos(N, F, proposals, max_steps)
        # All nodes should return None since consensus cannot be reached
        for node in range(N):
            self.assertIsNone(result.get(node), f"Node {node} should not have reached consensus.")

    def test_empty_system(self):
        # Test scenario when there are no nodes in the system.
        N = 0
        F = 0
        proposals = []
        max_steps = 100
        result = simulate_paxos(N, F, proposals, max_steps)
        # The result should be an empty dictionary
        self.assertEqual(result, {})

    def test_byzantine_fault_tolerance(self):
        # Test a system with faulty (Byzantine) nodes.
        # According to the Paxos condition N > 3F, we choose N=7 and F=1.
        N = 7
        F = 1
        proposals = [100, 200, 300, 400, 500, 600, 700]
        max_steps = 2000
        result = simulate_paxos(N, F, proposals, max_steps)
        self.assertEqual(set(result.keys()), set(range(N)))
        
        # Collect learned values that are not None
        learned_values = [v for v in result.values() if v is not None]
        # If consensus is reached, non-faulty nodes should agree on one value.
        if learned_values:
            consensus_value = learned_values[0]
            for value in learned_values:
                self.assertEqual(value, consensus_value)
            self.assertIn(consensus_value, proposals)
        else:
            # In cases where consensus isn't reached, all values should be None.
            for node in range(N):
                self.assertIsNone(result.get(node), f"Node {node} should not have reached consensus.")

if __name__ == '__main__':
    unittest.main()