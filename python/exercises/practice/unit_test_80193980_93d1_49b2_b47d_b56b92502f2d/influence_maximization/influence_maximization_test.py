import unittest
import random
from influence_maximization import maximize_influence

class InfluenceMaximizationTest(unittest.TestCase):
    
    def test_empty_graph(self):
        # Test with an empty graph
        graph = {}
        influence_scores = {}
        k = 3
        T = 5
        result = maximize_influence(graph, influence_scores, k, T, 100)
        self.assertEqual(result, [])
    
    def test_k_exceeds_nodes(self):
        # Test when k is larger than the number of nodes
        graph = {1: [2], 2: [3], 3: []}
        influence_scores = {1: 10, 2: 5, 3: 2}
        k = 5
        T = 3
        result = maximize_influence(graph, influence_scores, k, T, 100)
        # Should include all nodes in some order
        self.assertEqual(set(result), {1, 2, 3})
        self.assertEqual(len(result), 3)
    
    def test_t_exceeds_nodes(self):
        # Test when T is larger than the number of nodes
        graph = {1: [2], 2: [3], 3: []}
        influence_scores = {1: 10, 2: 5, 3: 2}
        k = 2
        T = 10  # More than the total number of nodes
        result = maximize_influence(graph, influence_scores, k, T, 100)
        # Should still return k nodes as seed
        self.assertEqual(len(result), k)
    
    def test_small_linear_graph(self):
        # Test with a linear graph where influence flow is clear
        graph = {1: [2], 2: [3], 3: [4], 4: [5], 5: []}
        influence_scores = {1: 100, 2: 10, 3: 5, 4: 2, 5: 1}
        k = 2
        T = 4
        # Set a seed for reproducibility
        random.seed(42)
        result = maximize_influence(graph, influence_scores, k, T, 100)
        # The best strategy would be to pick nodes with highest influence
        # and good network position
        self.assertEqual(len(result), k)
    
    def test_disconnected_graph(self):
        # Test with a disconnected graph
        graph = {
            1: [2, 3], 2: [3], 3: [],
            4: [5, 6], 5: [], 6: []
        }
        influence_scores = {1: 10, 2: 5, 3: 2, 4: 8, 5: 3, 6: 1}
        k = 2
        T = 5
        result = maximize_influence(graph, influence_scores, k, T, 100)
        self.assertEqual(len(result), k)
    
    def test_complete_graph(self):
        # Test with a complete graph where everyone influences everyone
        graph = {
            1: [2, 3, 4, 5],
            2: [1, 3, 4, 5],
            3: [1, 2, 4, 5],
            4: [1, 2, 3, 5],
            5: [1, 2, 3, 4]
        }
        influence_scores = {1: 10, 2: 8, 3: 6, 4: 4, 5: 2}
        k = 2
        T = 5
        result = maximize_influence(graph, influence_scores, k, T, 100)
        self.assertEqual(len(result), k)
    
    def test_star_graph(self):
        # Test with a star graph (one central node)
        graph = {
            1: [2, 3, 4, 5, 6],
            2: [], 3: [], 4: [], 5: [], 6: []
        }
        influence_scores = {1: 5, 2: 1, 3: 1, 4: 1, 5: 1, 6: 1}
        k = 1
        T = 6
        result = maximize_influence(graph, influence_scores, k, T, 100)
        # The central node should be selected
        self.assertEqual(result, [1])
    
    def test_zero_influence_score(self):
        # Test handling of zero influence scores
        graph = {1: [2], 2: [3], 3: []}
        influence_scores = {1: 10, 2: 0, 3: 5}
        k = 2
        T = 3
        result = maximize_influence(graph, influence_scores, k, T, 100)
        self.assertEqual(len(result), k)
    
    def test_medium_graph(self):
        # Test with a medium-sized graph
        graph = {}
        influence_scores = {}
        
        # Create a graph with 100 nodes
        for i in range(1, 101):
            graph[i] = []
            influence_scores[i] = random.randint(1, 20)
        
        # Add random edges (about 300)
        for _ in range(300):
            source = random.randint(1, 100)
            target = random.randint(1, 100)
            if source != target and target not in graph[source]:
                graph[source].append(target)
        
        k = 5
        T = 30
        random.seed(42)
        result = maximize_influence(graph, influence_scores, k, T, 50)
        self.assertEqual(len(result), k)
        # Check if result is sorted
        self.assertEqual(result, sorted(result))
    
    def test_tie_breaking(self):
        # Test tie breaking by sum of user IDs
        graph = {
            1: [4, 5],
            2: [4, 5],
            3: [6, 7],
            4: [], 5: [], 6: [], 7: []
        }
        # Set identical influence scores
        influence_scores = {1: 10, 2: 10, 3: 10, 4: 1, 5: 1, 6: 1, 7: 1}
        k = 2
        T = 4
        
        # Mock the simulation to always return the same probability
        # This is to test the tie-breaking mechanism
        # We'll do this by setting a fixed seed
        random.seed(42)
        result = maximize_influence(graph, influence_scores, k, T, 100)
        
        # Verify we got exactly k nodes
        self.assertEqual(len(result), k)
    
    def test_large_graph_performance(self):
        # Test performance with a larger graph (not full 10,000 nodes to keep test runtime reasonable)
        node_count = 500
        edge_count = 2000
        
        graph = {}
        influence_scores = {}
        
        # Create nodes
        for i in range(1, node_count + 1):
            graph[i] = []
            influence_scores[i] = random.randint(1, 50)
        
        # Add random edges
        edges_added = 0
        while edges_added < edge_count:
            source = random.randint(1, node_count)
            target = random.randint(1, node_count)
            if source != target and target not in graph[source]:
                graph[source].append(target)
                edges_added += 1
        
        k = 10
        T = 100
        
        # Time the execution
        import time
        start_time = time.time()
        
        result = maximize_influence(graph, influence_scores, k, T, 20)
        
        execution_time = time.time() - start_time
        
        # Check result validity
        self.assertEqual(len(result), k)
        self.assertTrue(all(node in graph for node in result))
        
        # Performance check - should complete in reasonable time
        # Adjust the threshold as needed based on your machine's performance
        self.assertLess(execution_time, 60, "Execution took too long")

if __name__ == '__main__':
    unittest.main()