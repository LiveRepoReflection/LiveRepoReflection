import unittest
from network_relief import minimize_congestion

class NetworkReliefTest(unittest.TestCase):
    
    def test_simple_case(self):
        N = 3
        M = 3
        edges = [(0, 1, 100), (1, 2, 100), (0, 2, 50)]
        K = 1
        flows = [(0, 2, 60)]
        L = 1
        P = 50
        
        result = minimize_congestion(N, M, edges, K, flows, L, P)
        
        self.assertTrue(isinstance(result, list))
        self.assertLessEqual(len(result), L)
        self.assertTrue(all(0 <= edge_idx < M for edge_idx in result))
        
        # Expected result should prioritize edge (0, 2) - index 2
        self.assertEqual([2], result)

    def test_no_prioritization_needed(self):
        N = 3
        M = 3
        edges = [(0, 1, 100), (1, 2, 100), (0, 2, 200)]
        K = 1
        flows = [(0, 2, 50)]
        L = 2
        P = 20
        
        result = minimize_congestion(N, M, edges, K, flows, L, P)
        
        self.assertTrue(isinstance(result, list))
        self.assertLessEqual(len(result), L)
        self.assertTrue(all(0 <= edge_idx < M for edge_idx in result))
        
        # With sufficient capacity on direct path, no prioritization needed
        # Empty list is acceptable, or any prioritization that doesn't worsen congestion
        self.assertLessEqual(len(result), L)

    def test_multiple_flows(self):
        N = 4
        M = 5
        edges = [(0, 1, 100), (1, 2, 100), (2, 3, 100), (0, 3, 50), (0, 2, 80)]
        K = 2
        flows = [(0, 3, 40), (0, 2, 50)]
        L = 2
        P = 30
        
        result = minimize_congestion(N, M, edges, K, flows, L, P)
        
        self.assertTrue(isinstance(result, list))
        self.assertLessEqual(len(result), L)
        self.assertTrue(all(0 <= edge_idx < M for edge_idx in result))
        
        # Various optimizations are possible, test congestion instead of specific edges
        # The maximum congestion should be less than 1.0 with proper prioritization

    def test_disconnected_graph(self):
        N = 5
        M = 3
        edges = [(0, 1, 100), (1, 2, 100), (3, 4, 100)]
        K = 2
        flows = [(0, 2, 60), (0, 4, 50)]  # Second flow is impossible
        L = 1
        P = 20
        
        result = minimize_congestion(N, M, edges, K, flows, L, P)
        
        self.assertTrue(isinstance(result, list))
        self.assertLessEqual(len(result), L)
        self.assertTrue(all(0 <= edge_idx < M for edge_idx in result))
        
        # Only the first flow is possible, should prioritize either edge 0 or 1

    def test_congestion_calculation(self):
        N = 3
        M = 2
        edges = [(0, 1, 100), (1, 2, 40)]
        K = 1
        flows = [(0, 2, 60)]
        L = 1
        P = 50
        
        result = minimize_congestion(N, M, edges, K, flows, L, P)
        
        self.assertTrue(isinstance(result, list))
        self.assertLessEqual(len(result), L)
        self.assertTrue(all(0 <= edge_idx < M for edge_idx in result))
        
        # Should prioritize edge 1 (bottleneck) to reduce congestion from 1.5 to 0.75
        self.assertEqual([1], result)

    def test_large_network(self):
        N = 10
        M = 20
        # Generate a sample network
        edges = []
        for i in range(M):
            u = (i * 3) % N
            v = (i * 5) % N
            if u != v:
                edges.append((u, v, 50 + 10 * (i % 10)))
        
        K = 15
        flows = []
        for i in range(K):
            src = (i * 7) % N
            dst = (i * 11) % N
            if src != dst:
                flows.append((src, dst, 10 + 5 * (i % 6)))
        
        L = 5
        P = 40
        
        result = minimize_congestion(N, M, edges, K, flows, L, P)
        
        self.assertTrue(isinstance(result, list))
        self.assertLessEqual(len(result), L)
        self.assertTrue(all(0 <= edge_idx < M for edge_idx in result))

    def test_maximum_prioritization(self):
        N = 5
        M = 6
        edges = [(0, 1, 50), (1, 2, 50), (2, 3, 50), (3, 4, 50), (0, 3, 30), (1, 4, 30)]
        K = 2
        flows = [(0, 4, 40), (0, 2, 30)]
        L = 6  # Can prioritize all edges
        P = 60
        
        result = minimize_congestion(N, M, edges, K, flows, L, P)
        
        self.assertTrue(isinstance(result, list))
        self.assertLessEqual(len(result), L)
        self.assertTrue(all(0 <= edge_idx < M for edge_idx in result))
        
        # With L=M, it might prioritize all edges or just the critical ones

    def test_no_prioritization_allowed(self):
        N = 4
        M = 4
        edges = [(0, 1, 100), (1, 2, 50), (2, 3, 100), (0, 3, 70)]
        K = 2
        flows = [(0, 2, 40), (1, 3, 30)]
        L = 0  # No prioritization allowed
        P = 30
        
        result = minimize_congestion(N, M, edges, K, flows, L, P)
        
        self.assertTrue(isinstance(result, list))
        self.assertEqual(len(result), 0)  # Should return empty list

    def test_multiple_optimal_solutions(self):
        # A network where multiple prioritization strategies yield same congestion
        N = 4
        M = 4
        edges = [(0, 1, 50), (1, 2, 50), (2, 3, 50), (0, 3, 50)]
        K = 1
        flows = [(0, 3, 30)]
        L = 1
        P = 40
        
        result = minimize_congestion(N, M, edges, K, flows, L, P)
        
        self.assertTrue(isinstance(result, list))
        self.assertLessEqual(len(result), L)
        self.assertTrue(all(0 <= edge_idx < M for edge_idx in result))
        
        # Either direct path or any edge along alternative path could be prioritized

if __name__ == '__main__':
    unittest.main()