import unittest
from network_resilience import simulate_failures

class NetworkResilienceTest(unittest.TestCase):
    def test_example(self):
        # Example provided in the problem description.
        n = 4
        edges = [(0, 1, 50), (0, 2, 30), (1, 2, 20), (2, 3, 60)]
        initial_failures = {0}
        threshold = 0.6
        # Expected propagation:
        # Iteration 0: {0} fails.
        # Iteration 1: Node 1 (incoming from 0) fails; Node 2 (incoming from 0 and 1; previous state: 1 operational) does not fail yet; Node 3 remains operational.
        # Iteration 2: With node 1 now failed, Node 2 fails; then Node 3, with dependency from 2, eventually fails.
        # Final state: all nodes fail.
        expected = [0, 1, 2, 3]
        result = simulate_failures(n, edges, initial_failures, threshold)
        self.assertEqual(result, expected)

    def test_no_initial_failures(self):
        # With no initial failures, no propagation should occur.
        n = 3
        edges = [(0, 1, 10), (1, 2, 10)]
        initial_failures = set()
        threshold = 0.5
        expected = []
        result = simulate_failures(n, edges, initial_failures, threshold)
        self.assertEqual(result, expected)

    def test_disconnected_graph(self):
        # Two disconnected components:
        # Component 1: 0 -> 1 -> 2
        # Component 2: 3 -> 4
        # Initial failures in both components lead to full collapse.
        n = 5
        edges = [(0, 1, 10), (1, 2, 10), (3, 4, 20)]
        initial_failures = {0, 3}
        threshold = 0.5
        # For component 1:
        # Node 1: incoming from 0 (failed) => fails
        # Node 2: incoming from 1 (will eventually be failed) => fails
        # For component 2:
        # Node 4: incoming from 3 (failed) => fails
        expected = [0, 1, 2, 3, 4]
        result = simulate_failures(n, edges, initial_failures, threshold)
        self.assertEqual(result, expected)

    def test_star_graph(self):
        # One central node pointing to several leaves.
        n = 4
        edges = [(0, 1, 10), (0, 2, 20), (0, 3, 30)]
        initial_failures = {0}
        threshold = 0.5
        # Leaves each have a single incoming edge from 0 (failed), so they fail.
        expected = [0, 1, 2, 3]
        result = simulate_failures(n, edges, initial_failures, threshold)
        self.assertEqual(result, expected)

    def test_cycle(self):
        # Create a cycle: 0 -> 1 -> 2 -> 0
        n = 3
        edges = [(0, 1, 10), (1, 2, 10), (2, 0, 10)]
        initial_failures = {0}
        threshold = 0.5
        # Iteration 0: Node 0 fails.
        # Iteration 1: 
        #   Node 1: incoming from 0 (failed) => fails.
        #   Node 2: incoming from 1 (was operational in previous state) remains operational.
        # Iteration 2:
        #   Node 2: now incoming from 1 (failed) => fails.
        expected = [0, 1, 2]
        result = simulate_failures(n, edges, initial_failures, threshold)
        self.assertEqual(result, expected)

    def test_threshold_one(self):
        # With threshold = 1, a node requires all incoming support to remain operational.
        n = 3
        edges = [(0, 1, 10), (1, 2, 10)]
        initial_failures = {0}
        threshold = 1.0
        # Node 1: incoming from 0 is failed => fails.
        # Node 2: incoming from 1 (which will then fail) => fails.
        expected = [0, 1, 2]
        result = simulate_failures(n, edges, initial_failures, threshold)
        self.assertEqual(result, expected)

    def test_no_incoming_edges(self):
        # Nodes with no incoming edges should never change state if they are not initially failed.
        n = 3
        edges = []
        initial_failures = set()
        threshold = 0.7
        expected = []
        result = simulate_failures(n, edges, initial_failures, threshold)
        self.assertEqual(result, expected)

    def test_node_with_single_dependency(self):
        # One dependency edge where the dependency remains operational.
        n = 3
        edges = [(0, 1, 10)]
        initial_failures = set()
        threshold = 0.5
        # Node 0 has no incoming edges and remains operational.
        # Node 1: incoming from node 0 (operational) gives S_op = 10 equal to total 10.
        # Since the ratio meets the required support (10 is not less than 0.5*10), node 1 remains operational.
        # Node 2 has no incoming edges.
        expected = []
        result = simulate_failures(n, edges, initial_failures, threshold)
        self.assertEqual(result, expected)

if __name__ == '__main__':
    unittest.main()