import unittest
from influence_network import find_influential_users
import random
import time

class TestInfluenceNetwork(unittest.TestCase):

    def test_small_graph(self):
        # Simple graph where node 1 can influence the most
        graph = {
            1: {2: 1.0, 3: 1.0},
            2: {4: 1.0},
            3: {5: 1.0},
            4: {},
            5: {},
        }
        # With deterministic probabilities of 1.0, node 1 should always be selected
        result = find_influential_users(graph, k=1, iterations=10)
        self.assertEqual(result, {1})

    def test_empty_graph(self):
        graph = {}
        result = find_influential_users(graph, k=3, iterations=10)
        self.assertEqual(result, set())

    def test_k_equals_number_of_nodes(self):
        graph = {
            1: {2: 0.5},
            2: {3: 0.5},
            3: {4: 0.5},
            4: {5: 0.5},
            5: {},
        }
        result = find_influential_users(graph, k=5, iterations=10)
        self.assertEqual(len(result), 5)
        self.assertEqual(result, {1, 2, 3, 4, 5})

    def test_k_greater_than_nodes(self):
        graph = {
            1: {2: 0.5},
            2: {3: 0.5},
            3: {},
        }
        result = find_influential_users(graph, k=5, iterations=10)
        self.assertEqual(len(result), 3)
        self.assertEqual(result, {1, 2, 3})

    def test_isolated_nodes(self):
        graph = {
            1: {},
            2: {},
            3: {},
            4: {5: 0.9},
            5: {},
        }
        # Node 4 should be selected as it can influence node 5
        result = find_influential_users(graph, k=1, iterations=10)
        self.assertEqual(result, {4})

    def test_cycle_graph(self):
        graph = {
            1: {2: 0.5},
            2: {3: 0.5},
            3: {1: 0.5},
        }
        # Any node could be selected as they all have similar influence
        result = find_influential_users(graph, k=1, iterations=20)
        self.assertTrue(result <= {1, 2, 3})
        self.assertEqual(len(result), 1)

    def test_probabilistic_influence(self):
        # Fix the seed for reproducibility
        random.seed(42)
        
        graph = {
            1: {2: 0.8, 3: 0.8, 4: 0.8},
            2: {5: 0.2},
            3: {5: 0.2},
            4: {5: 0.2},
            5: {},
        }
        # Node 1 should be selected as it has higher probability to influence others
        result = find_influential_users(graph, k=1, iterations=50)
        self.assertEqual(result, {1})

    def test_complex_network(self):
        # A more complex network with multiple influence paths
        graph = {
            1: {2: 0.3, 3: 0.5},
            2: {4: 0.7, 5: 0.2},
            3: {5: 0.8, 6: 0.4},
            4: {7: 0.9},
            5: {7: 0.5, 8: 0.1},
            6: {8: 0.6, 9: 0.3},
            7: {10: 0.2},
            8: {10: 0.7},
            9: {},
            10: {},
        }
        result = find_influential_users(graph, k=2, iterations=50)
        # The best 2 nodes should be selected
        self.assertEqual(len(result), 2)
        # result should be a subset of all nodes
        self.assertTrue(result <= {1, 2, 3, 4, 5, 6, 7, 8, 9, 10})

    def test_performance_medium_graph(self):
        # Generate a medium-sized graph
        random.seed(42)
        num_nodes = 100
        graph = {i: {} for i in range(1, num_nodes + 1)}
        
        # Add random edges
        for i in range(1, num_nodes + 1):
            num_edges = random.randint(1, 10)
            for _ in range(num_edges):
                target = random.randint(1, num_nodes)
                if target != i:  # No self-loops
                    graph[i][target] = random.random()
        
        start_time = time.time()
        result = find_influential_users(graph, k=5, iterations=10)
        end_time = time.time()
        
        # Check basic properties
        self.assertEqual(len(result), 5)
        self.assertTrue(all(node in graph for node in result))
        
        # Check performance (should run in reasonable time)
        self.assertLess(end_time - start_time, 30)  # 30 seconds limit

    def test_invalid_probabilities(self):
        # Graph with invalid probabilities
        graph = {
            1: {2: 1.5, 3: -0.2, 4: 0.7},
            2: {5: 0.8},
            3: {5: 1.0},
            4: {5: "invalid"},
            5: {},
        }
        # Only valid edges should be considered
        result = find_influential_users(graph, k=2, iterations=20)
        self.assertEqual(len(result), 2)

    def test_disconnected_components(self):
        # Graph with two disconnected components
        graph = {
            1: {2: 0.5, 3: 0.5},
            2: {3: 0.5},
            3: {},
            4: {5: 0.8, 6: 0.8},
            5: {6: 0.5},
            6: {},
        }
        # Should select nodes from both components
        result = find_influential_users(graph, k=2, iterations=20)
        self.assertEqual(len(result), 2)
        
        # One node from each component would be optimal
        component1 = {1, 2, 3}
        component2 = {4, 5, 6}
        nodes_from_comp1 = result & component1
        nodes_from_comp2 = result & component2
        self.assertTrue(len(nodes_from_comp1) > 0)
        self.assertTrue(len(nodes_from_comp2) > 0)

    def test_deterministic_with_fixed_seed(self):
        # With fixed random seed, the result should be deterministic
        graph = {
            1: {2: 0.5, 3: 0.5, 4: 0.5},
            2: {5: 0.5, 6: 0.5},
            3: {7: 0.5, 8: 0.5},
            4: {9: 0.5, 10: 0.5},
            5: {}, 6: {}, 7: {}, 8: {}, 9: {}, 10: {},
        }
        
        random.seed(42)
        result1 = find_influential_users(graph, k=2, iterations=20)
        
        random.seed(42)
        result2 = find_influential_users(graph, k=2, iterations=20)
        
        self.assertEqual(result1, result2)

if __name__ == '__main__':
    unittest.main()