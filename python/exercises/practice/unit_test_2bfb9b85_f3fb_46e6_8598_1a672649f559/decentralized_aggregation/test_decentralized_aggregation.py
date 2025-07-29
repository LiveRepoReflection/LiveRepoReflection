import unittest
import numpy as np
from decentralized_aggregation import aggregate_updates

class TestDecentralizedAggregation(unittest.TestCase):
    def test_basic_aggregation(self):
        updates = [
            [1.0, 2.0, 3.0],
            [1.1, 2.1, 3.1],
            [1.2, 2.2, 3.2]
        ]
        graph = [[1, 2], [0, 2], [0, 1]]
        f = 0
        rounds = 2
        k = 2
        
        result = aggregate_updates(updates, graph, f, rounds, k)
        
        self.assertEqual(len(result), len(updates))
        self.assertEqual(len(result[0]), len(updates[0]))
        
        # Check if results are floating point numbers
        for client_update in result:
            for value in client_update:
                self.assertIsInstance(value, float)

    def test_byzantine_resistance(self):
        # Normal updates
        honest_updates = [
            [1.0, 1.0, 1.0],
            [1.1, 1.1, 1.1],
            [0.9, 0.9, 0.9]
        ]
        # Byzantine update (significantly different)
        byzantine_update = [100.0, 100.0, 100.0]
        
        updates = honest_updates + [byzantine_update]
        graph = [[1, 2, 3], [0, 2, 3], [0, 1, 3], [0, 1, 2]]
        f = 1
        rounds = 3
        k = 2
        
        result = aggregate_updates(updates, graph, f, rounds, k)
        
        # Check if result is closer to honest updates than byzantine update
        for client_result in result:
            honest_dist = np.mean([np.linalg.norm(np.array(client_result) - np.array(h)) 
                                 for h in honest_updates])
            byzantine_dist = np.linalg.norm(np.array(client_result) - np.array(byzantine_update))
            
            self.assertLess(honest_dist, byzantine_dist)

    def test_disconnected_graph(self):
        updates = [
            [1.0, 1.0],
            [2.0, 2.0],
            [3.0, 3.0],
            [4.0, 4.0]
        ]
        # Two disconnected components: (0,1) and (2,3)
        graph = [[1], [0], [3], [2]]
        f = 0
        rounds = 2
        k = 1
        
        result = aggregate_updates(updates, graph, f, rounds, k)
        
        # Check if nodes in same component converge to similar values
        dist_01 = np.linalg.norm(np.array(result[0]) - np.array(result[1]))
        dist_23 = np.linalg.norm(np.array(result[2]) - np.array(result[3]))
        dist_02 = np.linalg.norm(np.array(result[0]) - np.array(result[2]))
        
        self.assertLess(dist_01, dist_02)
        self.assertLess(dist_23, dist_02)

    def test_input_validation(self):
        with self.assertRaises(ValueError):
            # Test with f >= n/2
            updates = [[1.0], [2.0], [3.0]]
            graph = [[1, 2], [0, 2], [0, 1]]
            aggregate_updates(updates, graph, 2, 1, 2)
        
        with self.assertRaises(ValueError):
            # Test with invalid k
            updates = [[1.0], [2.0]]
            graph = [[1], [0]]
            aggregate_updates(updates, graph, 0, 1, 3)
        
        with self.assertRaises(ValueError):
            # Test with inconsistent update dimensions
            updates = [[1.0], [2.0, 2.0]]
            graph = [[1], [0]]
            aggregate_updates(updates, graph, 0, 1, 1)
        
        with self.assertRaises(ValueError):
            # Test with invalid graph (not symmetric)
            updates = [[1.0], [2.0]]
            graph = [[1], []]
            aggregate_updates(updates, graph, 0, 1, 1)

    def test_convergence(self):
        updates = [
            [1.0, 1.0],
            [1.1, 1.1],
            [0.9, 0.9],
            [1.0, 1.0]
        ]
        graph = [[1, 2, 3], [0, 2, 3], [0, 1, 3], [0, 1, 2]]
        f = 0
        rounds = 5
        k = 2
        
        result = aggregate_updates(updates, graph, f, rounds, k)
        
        # Check if all clients converge to similar values
        mean_update = np.mean(result, axis=0)
        max_deviation = max(np.linalg.norm(np.array(r) - mean_update) for r in result)
        
        self.assertLess(max_deviation, 0.1)

    def test_security(self):
        updates = [
            [1.0, 2.0],
            [2.0, 3.0],
            [3.0, 4.0]
        ]
        graph = [[1, 2], [0, 2], [0, 1]]
        f = 0
        rounds = 2
        k = 2
        
        # Store original updates
        original_updates = [u.copy() for u in updates]
        
        result = aggregate_updates(updates, graph, f, rounds, k)
        
        # Check if original updates remained unchanged
        for original, current in zip(original_updates, updates):
            self.assertEqual(original, current)

if __name__ == '__main__':
    unittest.main()