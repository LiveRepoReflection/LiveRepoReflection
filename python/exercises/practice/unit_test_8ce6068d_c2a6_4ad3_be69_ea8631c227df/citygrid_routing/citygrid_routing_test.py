import unittest
from citygrid_routing import find_k_shortest_paths

class TestCityGridRouting(unittest.TestCase):
    def test_basic_path_finding(self):
        # Simple graph with 4 nodes
        graph = {
            0: [(1, 1, 2), (2, 2, 2)],
            1: [(3, 1, 2)],
            2: [(3, 1, 2)],
            3: []
        }
        priority_nodes = [2]
        prev_routes = []
        updates = []
        
        result = find_k_shortest_paths(
            graph=graph,
            start=0,
            end=3,
            k=2,
            priority_nodes=priority_nodes,
            coordination_window=5,
            capacity_penalty=2.0,
            prev_routes=prev_routes,
            updates=updates
        )
        
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0], [0, 1, 3])  # Shortest path
        self.assertEqual(result[1], [0, 2, 3])  # Second shortest path

    def test_no_path_exists(self):
        graph = {
            0: [(1, 1, 2)],
            1: [],
            2: []
        }
        result = find_k_shortest_paths(
            graph=graph,
            start=0,
            end=2,
            k=1,
            priority_nodes=[],
            coordination_window=5,
            capacity_penalty=2.0,
            prev_routes=[],
            updates=[]
        )
        
        self.assertEqual(result, [])

    def test_capacity_constraints(self):
        graph = {
            0: [(1, 1, 1)],
            1: [(2, 1, 1)],
            2: []
        }
        prev_routes = [
            ([0, 1, 2], 0)  # Route recently used
        ]
        
        result = find_k_shortest_paths(
            graph=graph,
            start=0,
            end=2,
            k=1,
            priority_nodes=[],
            coordination_window=2,
            capacity_penalty=2.0,
            prev_routes=prev_routes,
            updates=[]
        )
        
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0], [0, 1, 2])

    def test_priority_nodes(self):
        graph = {
            0: [(1, 2, 2), (2, 2, 2)],
            1: [(3, 2, 2)],
            2: [(3, 2, 2)],
            3: []
        }
        priority_nodes = [2]
        
        result = find_k_shortest_paths(
            graph=graph,
            start=0,
            end=3,
            k=2,
            priority_nodes=priority_nodes,
            coordination_window=5,
            capacity_penalty=2.0,
            prev_routes=[],
            updates=[]
        )
        
        # Path through priority node should be preferred
        self.assertEqual(result[0], [0, 2, 3])

    def test_real_time_updates(self):
        graph = {
            0: [(1, 1, 2)],
            1: [(2, 1, 2)],
            2: []
        }
        updates = [(0, 1, 5, 1)]  # Update cost of edge 0->1
        
        result = find_k_shortest_paths(
            graph=graph,
            start=0,
            end=2,
            k=1,
            priority_nodes=[],
            coordination_window=5,
            capacity_penalty=2.0,
            prev_routes=[],
            updates=updates
        )
        
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0], [0, 1, 2])

    def test_large_graph(self):
        # Create a larger graph with 1000 nodes
        large_graph = {i: [] for i in range(1000)}
        for i in range(999):
            large_graph[i].append((i + 1, 1, 2))
        
        result = find_k_shortest_paths(
            graph=large_graph,
            start=0,
            end=999,
            k=1,
            priority_nodes=[100, 200, 300],
            coordination_window=5,
            capacity_penalty=2.0,
            prev_routes=[],
            updates=[]
        )
        
        self.assertEqual(len(result), 1)
        self.assertEqual(len(result[0]), 1000)

    def test_multiple_simultaneous_routes(self):
        graph = {
            0: [(1, 1, 2), (2, 1, 2)],
            1: [(3, 1, 2)],
            2: [(3, 1, 2)],
            3: []
        }
        prev_routes = [
            ([0, 1, 3], 0),
            ([0, 2, 3], 1)
        ]
        
        result = find_k_shortest_paths(
            graph=graph,
            start=0,
            end=3,
            k=1,
            priority_nodes=[],
            coordination_window=5,
            capacity_penalty=2.0,
            prev_routes=prev_routes,
            updates=[]
        )
        
        self.assertEqual(len(result), 1)

    def test_invalid_inputs(self):
        graph = {0: [(1, 1, 2)], 1: []}
        
        with self.assertRaises(ValueError):
            find_k_shortest_paths(
                graph=graph,
                start=0,
                end=2,  # Non-existent node
                k=0,    # Invalid k
                priority_nodes=[],
                coordination_window=5,
                capacity_penalty=2.0,
                prev_routes=[],
                updates=[]
            )
        
        with self.assertRaises(ValueError):
            find_k_shortest_paths(
                graph=graph,
                start=0,
                end=1,
                k=1,
                priority_nodes=[],
                coordination_window=-1,  # Invalid window
                capacity_penalty=2.0,
                prev_routes=[],
                updates=[]
            )

if __name__ == '__main__':
    unittest.main()