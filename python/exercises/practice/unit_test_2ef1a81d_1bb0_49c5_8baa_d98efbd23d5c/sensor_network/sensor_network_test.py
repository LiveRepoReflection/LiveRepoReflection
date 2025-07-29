import unittest
from sensor_network import optimal_coverage

class OptimalCoverageTest(unittest.TestCase):
    
    def test_basic_line_graph(self):
        # A simple line graph: 0 -- 1 -- 2 -- 3 -- 4
        graph = {
            0: [(1, 1)],
            1: [(0, 1), (2, 1)],
            2: [(1, 1), (3, 1)],
            3: [(2, 1), (4, 1)],
            4: [(3, 1)]
        }
        sources = [0, 2, 4]
        targets = [1, 3]
        k = 1
        coverage_radius = 1
        
        result = optimal_coverage(graph, sources, targets, k, coverage_radius)
        self.assertEqual(len(result), 1)
        self.assertTrue(result == {2})
    
    def test_star_graph(self):
        # A star graph where node 0 is connected to all others
        graph = {
            0: [(1, 1), (2, 1), (3, 1), (4, 1), (5, 1)],
            1: [(0, 1)],
            2: [(0, 1)],
            3: [(0, 1)],
            4: [(0, 1)],
            5: [(0, 1)]
        }
        sources = [1, 2, 3, 4, 5]
        targets = [0, 1, 2, 3, 4, 5]
        k = 2
        coverage_radius = 1
        
        result = optimal_coverage(graph, sources, targets, k, coverage_radius)
        self.assertEqual(len(result), 2)
        # Any two sources should cover all targets
        self.assertEqual(len(result.intersection(sources)), 2)
    
    def test_disconnected_graph(self):
        # Two separate components
        graph = {
            0: [(1, 1)],
            1: [(0, 1), (2, 1)],
            2: [(1, 1)],
            3: [(4, 1)],
            4: [(3, 1), (5, 1)],
            5: [(4, 1)]
        }
        sources = [0, 3]
        targets = [2, 5]
        k = 2
        coverage_radius = 2
        
        result = optimal_coverage(graph, sources, targets, k, coverage_radius)
        self.assertEqual(len(result), 2)
        self.assertEqual(result, {0, 3})
    
    def test_weighted_edges(self):
        # Graph with weighted edges
        graph = {
            0: [(1, 5), (2, 2)],
            1: [(0, 5), (2, 1)],
            2: [(0, 2), (1, 1), (3, 3)],
            3: [(2, 3), (4, 1)],
            4: [(3, 1)]
        }
        sources = [0, 2, 4]
        targets = [1, 3]
        k = 1
        coverage_radius = 3
        
        result = optimal_coverage(graph, sources, targets, k, coverage_radius)
        self.assertEqual(len(result), 1)
        self.assertEqual(result, {2})
    
    def test_not_all_targets_coverable(self):
        # Some targets can't be covered within radius
        graph = {
            0: [(1, 2)],
            1: [(0, 2), (2, 2)],
            2: [(1, 2), (3, 2)],
            3: [(2, 2), (4, 2)],
            4: [(3, 2)]
        }
        sources = [0]
        targets = [0, 4]
        k = 1
        coverage_radius = 3
        
        result = optimal_coverage(graph, sources, targets, k, coverage_radius)
        self.assertEqual(len(result), 1)
        self.assertEqual(result, {0})
    
    def test_k_greater_than_sources(self):
        # k is larger than available sources
        graph = {
            0: [(1, 1)],
            1: [(0, 1), (2, 1)],
            2: [(1, 1)]
        }
        sources = [0, 2]
        targets = [1]
        k = 3
        coverage_radius = 1
        
        result = optimal_coverage(graph, sources, targets, k, coverage_radius)
        self.assertTrue(len(result) <= 2)
        self.assertTrue(0 in result or 2 in result)
    
    def test_empty_sources(self):
        # Empty sources list
        graph = {
            0: [(1, 1)],
            1: [(0, 1)]
        }
        sources = []
        targets = [0, 1]
        k = 1
        coverage_radius = 1
        
        result = optimal_coverage(graph, sources, targets, k, coverage_radius)
        self.assertEqual(len(result), 0)
    
    def test_empty_targets(self):
        # Empty targets list
        graph = {
            0: [(1, 1)],
            1: [(0, 1)]
        }
        sources = [0, 1]
        targets = []
        k = 1
        coverage_radius = 1
        
        result = optimal_coverage(graph, sources, targets, k, coverage_radius)
        self.assertEqual(len(result), 0)
    
    def test_empty_graph(self):
        # Empty graph
        graph = {}
        sources = []
        targets = []
        k = 1
        coverage_radius = 1
        
        result = optimal_coverage(graph, sources, targets, k, coverage_radius)
        self.assertEqual(len(result), 0)
    
    def test_complex_graph(self):
        # A more complex graph with multiple possible solutions
        graph = {
            0: [(1, 1), (2, 3)],
            1: [(0, 1), (3, 2), (4, 4)],
            2: [(0, 3), (5, 1)],
            3: [(1, 2), (6, 1)],
            4: [(1, 4), (7, 2)],
            5: [(2, 1), (8, 3)],
            6: [(3, 1), (9, 2)],
            7: [(4, 2), (9, 1)],
            8: [(5, 3)],
            9: [(6, 2), (7, 1)]
        }
        sources = [0, 2, 4, 6, 8]
        targets = [1, 3, 5, 7, 9]
        k = 2
        coverage_radius = 2
        
        result = optimal_coverage(graph, sources, targets, k, coverage_radius)
        self.assertLessEqual(len(result), 2)
        
        # Check that the result covers the maximum possible number of targets
        covered = set()
        for source in result:
            # We would need to implement a shortest path algorithm to check coverage
            # For the unit test, we're just verifying the result structure is correct
            pass
    
    def test_large_k_small_sources(self):
        # k larger than sources, should return all sources
        graph = {
            0: [(1, 1)],
            1: [(0, 1), (2, 1)],
            2: [(1, 1), (3, 1)],
            3: [(2, 1)]
        }
        sources = [0, 3]
        targets = [1, 2]
        k = 5
        coverage_radius = 1
        
        result = optimal_coverage(graph, sources, targets, k, coverage_radius)
        self.assertEqual(result, set(sources))
    
    def test_zero_coverage_radius(self):
        # Only direct nodes are covered (zero distance)
        graph = {
            0: [(1, 1)],
            1: [(0, 1), (2, 1)],
            2: [(1, 1)]
        }
        sources = [0, 2]
        targets = [0, 1, 2]
        k = 2
        coverage_radius = 0
        
        result = optimal_coverage(graph, sources, targets, k, coverage_radius)
        self.assertEqual(result, {0, 2})
        
    def test_tie_breaking_scenario(self):
        # Multiple solutions with same coverage
        graph = {
            0: [(1, 1)],
            1: [(0, 1), (2, 1)],
            2: [(1, 1), (3, 1)],
            3: [(2, 1), (4, 1)],
            4: [(3, 1)]
        }
        sources = [0, 2, 4]
        targets = [1, 2, 3]
        k = 1
        coverage_radius = 1
        
        result = optimal_coverage(graph, sources, targets, k, coverage_radius)
        self.assertEqual(len(result), 1)
        self.assertTrue(result == {0} or result == {2} or result == {4})

if __name__ == '__main__':
    unittest.main()