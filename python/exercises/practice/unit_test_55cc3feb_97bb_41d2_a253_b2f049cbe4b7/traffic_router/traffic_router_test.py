import unittest
from traffic_router import find_k_shortest_paths

class TrafficRouterTest(unittest.TestCase):
    
    def test_simple_graph(self):
        # Simple graph with one shortest path
        graph = {
            0: [(1, 50, 10)],  # Node 0 to Node 1: Capacity 50, Time 10
            1: [(2, 40, 5)],   # Node 1 to Node 2: Capacity 40, Time 5
            2: []              # Node 2: No outgoing edges
        }
        
        requests = [(0, 2, 1)]  # Find 1 shortest path from 0 to 2
        updates = []
        
        expected = [[[0, 1, 2]]]  # One path: 0 -> 1 -> 2
        result = find_k_shortest_paths(graph, requests, updates)
        self.assertEqual(result, expected)
    
    def test_multiple_paths(self):
        # Graph with multiple paths between nodes
        graph = {
            0: [(1, 50, 10), (2, 30, 5)],
            1: [(3, 40, 10)],
            2: [(3, 60, 15)],
            3: []
        }
        
        requests = [(0, 3, 2)]  # Find 2 shortest paths from 0 to 3
        updates = []
        
        # Two shortest paths: 0 -> 1 -> 3 (time 20) and 0 -> 2 -> 3 (time 20)
        # Paths with equal time should be included if within k
        expected_paths = [[0, 1, 3], [0, 2, 3]]
        result = find_k_shortest_paths(graph, requests, updates)
        
        # Since both paths have the same time, we allow any order
        self.assertEqual(len(result), 1)
        self.assertEqual(len(result[0]), 2)
        self.assertTrue(result[0][0] in expected_paths)
        self.assertTrue(result[0][1] in expected_paths)
        self.assertNotEqual(result[0][0], result[0][1])
    
    def test_road_updates(self):
        # Test graph with road updates
        graph = {
            0: [(1, 50, 10), (2, 30, 15)],
            1: [(3, 40, 20)],
            2: [(3, 60, 5)],
            3: []
        }
        
        requests = [(0, 3, 2)]  # Find 2 shortest paths from 0 to 3
        updates = [(0, 1, 60, 5)]  # Update road from 0 to 1: new capacity 60, new time 5
        
        # After update: 0 -> 1 -> 3 (time 25) and 0 -> 2 -> 3 (time 20)
        expected = [[[0, 2, 3], [0, 1, 3]]]
        result = find_k_shortest_paths(graph, requests, updates)
        self.assertEqual(result, expected)
    
    def test_multiple_updates(self):
        graph = {
            0: [(1, 50, 10), (2, 30, 15)],
            1: [(3, 40, 20)],
            2: [(3, 60, 5)],
            3: []
        }
        
        requests = [(0, 3, 3)]  # Find 3 shortest paths from 0 to 3
        # Multiple updates affecting path order
        updates = [
            (0, 1, 60, 5),   # Update makes 0->1->3 faster
            (2, 3, 70, 20),  # Update makes 0->2->3 slower
            (0, 3, 20, 30)   # Add direct path from 0->3
        ]
        
        # After updates: 0 -> 1 -> 3 (time 25), 0 -> 3 (time 30), 0 -> 2 -> 3 (time 35)
        expected = [[[0, 1, 3], [0, 3], [0, 2, 3]]]
        result = find_k_shortest_paths(graph, requests, updates)
        self.assertEqual(result, expected)
    
    def test_path_removal(self):
        graph = {
            0: [(1, 50, 10), (2, 30, 15)],
            1: [(3, 40, 20)],
            2: [(3, 60, 5)],
            3: []
        }
        
        requests = [(0, 3, 2)]
        # Update that effectively removes a path by setting capacity to 0
        updates = [(2, 3, 0, 5)]
        
        # After update: Only 0 -> 1 -> 3 (time 30) is available
        expected = [[[0, 1, 3]]]
        result = find_k_shortest_paths(graph, requests, updates)
        self.assertEqual(result, expected)
    
    def test_no_path_exists(self):
        graph = {
            0: [(1, 50, 10)],
            1: [],
            2: []
        }
        
        requests = [(0, 2, 1)]  # No path from 0 to 2
        updates = []
        
        expected = [[]]  # Empty list when no path exists
        result = find_k_shortest_paths(graph, requests, updates)
        self.assertEqual(result, expected)
    
    def test_multiple_requests(self):
        graph = {
            0: [(1, 50, 10), (2, 30, 5)],
            1: [(3, 40, 15)],
            2: [(3, 60, 20), (4, 70, 10)],
            3: [],
            4: [(3, 50, 5)]
        }
        
        requests = [
            (0, 3, 2),  # Find 2 shortest paths from 0 to 3
            (0, 4, 1),  # Find 1 shortest path from 0 to 4
            (2, 3, 2)   # Find 2 shortest paths from 2 to 3
        ]
        updates = []
        
        # Expected results for each request
        expected = [
            [[0, 1, 3], [0, 2, 4, 3]],  # 0->3: via 1 (time 25), via 2->4 (time 20)
            [[0, 2, 4]],                # 0->4: 0->2->4 (time 15)
            [[2, 4, 3], [2, 3]]         # 2->3: via 4 (time 15), direct (time 20)
        ]
        result = find_k_shortest_paths(graph, requests, updates)
        
        # Check if same paths are present (allowing for different order if times are equal)
        for i, paths in enumerate(result):
            self.assertEqual(len(paths), len(expected[i]))
            for path in paths:
                self.assertTrue(path in expected[i])
    
    def test_zero_travel_time(self):
        graph = {
            0: [(1, 50, 0), (2, 30, 5)],  # Zero travel time from 0 to 1
            1: [(3, 40, 10)],
            2: [(3, 60, 15)],
            3: []
        }
        
        requests = [(0, 3, 2)]
        updates = []
        
        # Expected: 0 -> 1 -> 3 (time 10), 0 -> 2 -> 3 (time 20)
        expected = [[[0, 1, 3], [0, 2, 3]]]
        result = find_k_shortest_paths(graph, requests, updates)
        self.assertEqual(result, expected)
    
    def test_large_graph_performance(self):
        # Create a larger graph to test performance
        graph = {}
        
        # Create a grid-like graph structure
        size = 20  # 20x20 grid = 400 nodes
        for i in range(size * size):
            graph[i] = []
            
            # Connect to right neighbor
            if (i % size) < size - 1:
                graph[i].append((i + 1, 100, 5))
                
            # Connect to bottom neighbor
            if i < size * (size - 1):
                graph[i].append((i + size, 100, 5))
                
            # Some diagonal connections for alternate paths
            if (i % size) < size - 1 and i < size * (size - 1):
                graph[i].append((i + size + 1, 50, 7))
        
        start_node = 0
        end_node = size * size - 1  # Bottom-right corner
        
        requests = [(start_node, end_node, 3)]  # Find 3 shortest paths
        updates = [
            (0, 1, 50, 10),  # A few updates to test handling
            (size, size + 1, 80, 3),
            (2 * size, 2 * size + 1, 120, 2)
        ]
        
        # We don't check specific paths, just verify that something is returned
        # and the function completes in a reasonable time
        result = find_k_shortest_paths(graph, requests, updates)
        self.assertTrue(len(result) > 0)
        self.assertTrue(len(result[0]) > 0)
        
    def test_updates_before_requests(self):
        graph = {
            0: [(1, 50, 10), (2, 30, 15)],
            1: [(3, 40, 20)],
            2: [(3, 60, 5)],
            3: []
        }
        
        # Apply updates before processing requests
        updates = [
            (0, 1, 60, 5),   # Make 0->1 faster
            (1, 3, 50, 10)   # Make 1->3 faster
        ]
        requests = [(0, 3, 2)]  # Find 2 shortest paths from 0 to 3
        
        # After updates: 0 -> 1 -> 3 (time 15), 0 -> 2 -> 3 (time 20)
        expected = [[[0, 1, 3], [0, 2, 3]]]
        result = find_k_shortest_paths(graph, requests, updates)
        self.assertEqual(result, expected)
    
    def test_adding_new_edges(self):
        graph = {
            0: [(1, 50, 10)],
            1: [(2, 40, 5)],
            2: []
        }
        
        requests = [(0, 2, 2)]  # Find 2 shortest paths from 0 to 2
        updates = [
            (0, 2, 30, 20)  # Add direct connection from 0 to 2
        ]
        
        # After updates: 0 -> 1 -> 2 (time 15), 0 -> 2 (time 20)
        expected = [[[0, 1, 2], [0, 2]]]
        result = find_k_shortest_paths(graph, requests, updates)
        self.assertEqual(result, expected)
    
    def test_k_greater_than_available_paths(self):
        graph = {
            0: [(1, 50, 10), (2, 30, 5)],
            1: [(3, 40, 15)],
            2: [(3, 60, 20)],
            3: []
        }
        
        requests = [(0, 3, 5)]  # Request 5 paths, but only 2 exist
        updates = []
        
        # Only two paths available: 0 -> 1 -> 3, 0 -> 2 -> 3
        expected = [[[0, 1, 3], [0, 2, 3]]]
        result = find_k_shortest_paths(graph, requests, updates)
        self.assertEqual(len(result[0]), 2)
        self.assertTrue(all(path in expected[0] for path in result[0]))

if __name__ == "__main__":
    unittest.main()