import unittest
from art_gallery_dag import propagate_feedback
import time

class TestPropagateRatings(unittest.TestCase):
    
    def test_basic_propagation(self):
        """Test a simple propagation in a small DAG."""
        nodes = [
            {"id": "A", "value": 5.0, "min_value": 0.0, "max_value": 10.0},
            {"id": "B", "value": 10.0, "min_value": 0.0, "max_value": 20.0},
            {"id": "C", "value": 15.0, "min_value": 0.0, "max_value": 30.0}
        ]
        edges = [
            {"source": "A", "destination": "B", "weight": 0.5},
            {"source": "B", "destination": "C", "weight": 0.8}
        ]
        ratings = {"B": 20}
        dampening_factor = 0.5
        
        expected = {
            "A": 5.0 + (20 - 10.0) * 0.5 * 0.5,  # Original + (Rating - Original) * Weight * Dampening
            "B": 20.0,  # Direct rating
            "C": 15.0 + (20 - 10.0) * 0.8 * 0.5  # Original + (Rating - Original) * Weight * Dampening
        }
        
        result = propagate_feedback(nodes, edges, ratings, dampening_factor)
        
        for node_id, expected_value in expected.items():
            self.assertAlmostEqual(result[node_id], expected_value, places=6)
    
    def test_node_value_bounds(self):
        """Test that node parameters are properly bounded."""
        nodes = [
            {"id": "A", "value": 5.0, "min_value": 0.0, "max_value": 10.0},
            {"id": "B", "value": 10.0, "min_value": 0.0, "max_value": 15.0}
        ]
        edges = [
            {"source": "A", "destination": "B", "weight": 1.0}
        ]
        
        # This would push B beyond its max_value if not bounded
        ratings = {"A": 20}
        dampening_factor = 1.0
        
        result = propagate_feedback(nodes, edges, ratings, dampening_factor)
        
        self.assertEqual(result["A"], 10.0)  # Clipped to max_value
        self.assertLessEqual(result["B"], 15.0)  # Should not exceed max_value
        
        # Now test min_value
        nodes = [
            {"id": "A", "value": 5.0, "min_value": 0.0, "max_value": 10.0},
            {"id": "B", "value": 3.0, "min_value": 2.0, "max_value": 15.0}
        ]
        
        ratings = {"A": -10}  # This would push A and potentially B below their min_values
        
        result = propagate_feedback(nodes, edges, ratings, dampening_factor)
        
        self.assertEqual(result["A"], 0.0)  # Clipped to min_value
        self.assertGreaterEqual(result["B"], 2.0)  # Should not go below min_value
    
    def test_multiple_ratings(self):
        """Test propagation with multiple ratings."""
        nodes = [
            {"id": "A", "value": 5.0, "min_value": 0.0, "max_value": 10.0},
            {"id": "B", "value": 10.0, "min_value": 0.0, "max_value": 20.0},
            {"id": "C", "value": 15.0, "min_value": 0.0, "max_value": 30.0}
        ]
        edges = [
            {"source": "A", "destination": "B", "weight": 0.5},
            {"source": "B", "destination": "C", "weight": 0.8}
        ]
        
        # Both A and C get rated
        ratings = {"A": 8, "C": 25}
        dampening_factor = 0.5
        
        # A gets direct rating + influence from B (which gets influence from C)
        # B gets influence from both A and C
        # C gets direct rating + influence from B (which gets influence from A)
        result = propagate_feedback(nodes, edges, ratings, dampening_factor)
        
        # Hand-calculating this is complex, so we'll just check that the values are different
        # from the original and that direct ratings are applied correctly
        self.assertEqual(result["A"], 8.0)  # Direct rating
        self.assertNotEqual(result["B"], 10.0)  # Should be updated
        self.assertEqual(result["C"], 25.0)  # Direct rating
    
    def test_cycle_handling(self):
        """Test that the algorithm handles cycles gracefully."""
        nodes = [
            {"id": "A", "value": 5.0, "min_value": 0.0, "max_value": 10.0},
            {"id": "B", "value": 10.0, "min_value": 0.0, "max_value": 20.0},
            {"id": "C", "value": 15.0, "min_value": 0.0, "max_value": 30.0}
        ]
        edges = [
            {"source": "A", "destination": "B", "weight": 0.5},
            {"source": "B", "destination": "C", "weight": 0.8},
            {"source": "C", "destination": "A", "weight": 0.3}  # This creates a cycle
        ]
        
        ratings = {"B": 20}
        dampening_factor = 0.5
        
        # The function should not get stuck in an infinite loop
        result = propagate_feedback(nodes, edges, ratings, dampening_factor)
        
        # We expect all nodes to be affected due to the cycle
        self.assertNotEqual(result["A"], 5.0)
        self.assertEqual(result["B"], 20.0)  # Direct rating
        self.assertNotEqual(result["C"], 15.0)
    
    def test_large_graph_performance(self):
        """Test that the algorithm performs well on larger graphs."""
        # Generate a larger DAG
        num_nodes = 1000
        nodes = [{"id": str(i), "value": float(i), "min_value": 0.0, "max_value": float(2*i)} for i in range(num_nodes)]
        
        # Create a chain of nodes with some random connections
        import random
        random.seed(42)  # For reproducibility
        
        edges = []
        for i in range(num_nodes - 1):
            edges.append({"source": str(i), "destination": str(i+1), "weight": random.uniform(0.1, 1.0)})
            
            # Add some random edges (but ensure it's still a DAG by only connecting to higher nodes)
            for _ in range(3):  # Add up to 3 random edges per node
                dest = random.randint(i+2, num_nodes-1) if i+2 < num_nodes else i+1
                edges.append({"source": str(i), "destination": str(dest), "weight": random.uniform(0.1, 1.0)})
        
        # Create some ratings
        ratings = {str(i): float(i+10) for i in range(0, num_nodes, 100)}  # Rate every 100th node
        
        dampening_factor = 0.5
        
        start_time = time.time()
        result = propagate_feedback(nodes, edges, ratings, dampening_factor)
        end_time = time.time()
        
        # Check that we got results for all nodes
        self.assertEqual(len(result), num_nodes)
        
        # Check that the algorithm completed in a reasonable time
        # Adjust this threshold based on the expected performance of your algorithm
        self.assertLess(end_time - start_time, 5.0, "Algorithm took too long to complete")
    
    def test_memory_efficiency(self):
        """Test the memory efficiency of the algorithm (hard to test directly)."""
        # This is more of a conceptual test since we can't easily measure memory usage in a unit test
        # In a real-world scenario, you would use tools like memory_profiler or tracemalloc
        
        # We'll create a large number of nodes and edges
        num_nodes = 10000
        nodes = [{"id": str(i), "value": float(i), "min_value": 0.0, "max_value": float(2*i)} for i in range(num_nodes)]
        
        # Create a sparse graph (linear chain with some additional edges)
        edges = []
        for i in range(num_nodes - 1):
            edges.append({"source": str(i), "destination": str(i+1), "weight": 0.5})
            
            # Add some long-distance edges
            if i % 100 == 0 and i + 500 < num_nodes:
                edges.append({"source": str(i), "destination": str(i+500), "weight": 0.3})
        
        # Create some ratings
        ratings = {str(i): float(i+10) for i in range(0, num_nodes, 1000)}  # Rate every 1000th node
        
        dampening_factor = 0.5
        
        try:
            result = propagate_feedback(nodes, edges, ratings, dampening_factor)
            # If we get here without a memory error, that's a good sign
            self.assertEqual(len(result), num_nodes)
        except MemoryError:
            self.fail("Algorithm ran out of memory")
        
    def test_empty_inputs(self):
        """Test that the algorithm handles empty inputs gracefully."""
        nodes = []
        edges = []
        ratings = {}
        dampening_factor = 0.5
        
        result = propagate_feedback(nodes, edges, ratings, dampening_factor)
        self.assertEqual(result, {})
        
        # Test with nodes but no edges or ratings
        nodes = [{"id": "A", "value": 5.0, "min_value": 0.0, "max_value": 10.0}]
        
        result = propagate_feedback(nodes, edges, ratings, dampening_factor)
        self.assertEqual(result, {"A": 5.0})
        
        # Test with nodes and edges but no ratings
        edges = [{"source": "A", "destination": "B", "weight": 0.5}]
        nodes.append({"id": "B", "value": 10.0, "min_value": 0.0, "max_value": 20.0})
        
        result = propagate_feedback(nodes, edges, ratings, dampening_factor)
        self.assertEqual(result, {"A": 5.0, "B": 10.0})
    
    def test_rating_propagation_with_multiple_paths(self):
        """Test that ratings propagate correctly with multiple paths between nodes."""
        nodes = [
            {"id": "A", "value": 5.0, "min_value": 0.0, "max_value": 10.0},
            {"id": "B", "value": 10.0, "min_value": 0.0, "max_value": 20.0},
            {"id": "C", "value": 15.0, "min_value": 0.0, "max_value": 30.0},
            {"id": "D", "value": 20.0, "min_value": 0.0, "max_value": 40.0}
        ]
        edges = [
            {"source": "A", "destination": "B", "weight": 0.5},
            {"source": "B", "destination": "D", "weight": 0.8},
            {"source": "A", "destination": "C", "weight": 0.6},
            {"source": "C", "destination": "D", "weight": 0.7}
        ]
        
        ratings = {"A": 8}
        dampening_factor = 0.5
        
        result = propagate_feedback(nodes, edges, ratings, dampening_factor)
        
        # D should be influenced by both paths A->B->D and A->C->D
        self.assertEqual(result["A"], 8.0)  # Direct rating
        self.assertNotEqual(result["B"], 10.0)  # Should be updated
        self.assertNotEqual(result["C"], 15.0)  # Should be updated
        self.assertNotEqual(result["D"], 20.0)  # Should be updated by both paths

if __name__ == '__main__':
    unittest.main()