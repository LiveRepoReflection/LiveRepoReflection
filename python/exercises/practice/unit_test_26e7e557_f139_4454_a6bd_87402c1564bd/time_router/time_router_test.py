import unittest
from time_router import find_optimal_route

class TimeRouterTest(unittest.TestCase):
    def test_basic_route_no_congestion(self):
        # Simple graph with no congestion
        graph = {
            1: [(2, 10, [])],
            2: [(3, 20, [])],
            3: []
        }
        self.assertEqual(find_optimal_route(graph, 1, 3, 0), 30)

    def test_multiple_paths(self):
        # Graph with multiple possible paths
        graph = {
            1: [(2, 10, []), (3, 15, [])],
            2: [(4, 20, [])],
            3: [(4, 10, [])],
            4: []
        }
        self.assertEqual(find_optimal_route(graph, 1, 4, 0), 25)  # Path 1->3->4 is shorter

    def test_single_congestion_window(self):
        # Graph with one congestion window
        graph = {
            1: [(2, 10, [(0, 100, 2.0)])],  # Double travel time from 0-100 minutes
            2: [(3, 20, [])],
            3: []
        }
        self.assertEqual(find_optimal_route(graph, 1, 3, 50), 40)  # 10*2 + 20 = 40
        self.assertEqual(find_optimal_route(graph, 1, 3, 150), 30)  # 10 + 20 = 30 (outside congestion)

    def test_multiple_congestion_windows(self):
        # Multiple congestion windows on a single road
        graph = {
            1: [(2, 10, [(0, 100, 2.0), (200, 300, 3.0)])],
            2: []
        }
        self.assertEqual(find_optimal_route(graph, 1, 2, 50), 20)   # Inside first window
        self.assertEqual(find_optimal_route(graph, 1, 2, 150), 10)   # Outside any window
        self.assertEqual(find_optimal_route(graph, 1, 2, 250), 30)   # Inside second window

    def test_overlapping_congestion_windows(self):
        # Overlapping congestion windows (should use the highest factor)
        graph = {
            1: [(2, 10, [(0, 100, 2.0), (50, 150, 3.0)])],
            2: []
        }
        self.assertEqual(find_optimal_route(graph, 1, 2, 75), 30)   # Overlapping windows, 10*3 = 30

    def test_time_wrapping(self):
        # Test time wrapping around at the end of the day
        graph = {
            1: [(2, 10, [(1430, 1450, 2.0)])],  # Congestion near midnight
            2: []
        }
        self.assertEqual(find_optimal_route(graph, 1, 2, 1435), 20)  # Inside congestion window
        self.assertEqual(find_optimal_route(graph, 1, 2, 10), 10)    # Outside congestion window

    def test_complex_graph(self):
        # More complex graph with multiple paths and congestion
        graph = {
            1: [(2, 10, [(0, 100, 2.0)]), (3, 15, [(0, 50, 1.5)])],
            2: [(4, 20, [(0, 200, 1.5)])],
            3: [(4, 10, [(150, 250, 3.0)])],
            4: []
        }
        # At time 0:
        # Path 1->2->4: 10*2 + 20*1.5 = 50
        # Path 1->3->4: 15*1.5 + 10 = 32.5
        self.assertEqual(find_optimal_route(graph, 1, 4, 0), 32.5)
        
        # At time 175:
        # Path 1->2->4: 10 + 20*1.5 = 40
        # Path 1->3->4: 15 + 10*3 = 45
        self.assertEqual(find_optimal_route(graph, 1, 4, 175), 40)

    def test_no_path(self):
        # Graph with no path from start to end
        graph = {
            1: [(2, 10, [])],
            2: [],
            3: [(4, 10, [])],
            4: []
        }
        self.assertEqual(find_optimal_route(graph, 1, 4, 0), -1)

    def test_invalid_nodes(self):
        # Invalid start or end nodes
        graph = {
            1: [(2, 10, [])],
            2: []
        }
        self.assertEqual(find_optimal_route(graph, 5, 2, 0), -1)  # Invalid start
        self.assertEqual(find_optimal_route(graph, 1, 5, 0), -1)  # Invalid end

    def test_large_graph(self):
        # Test with a larger graph (not actually 10,000 nodes, but enough to test algorithm efficiency)
        graph = {}
        # Create a simple grid graph
        for i in range(1, 101):  # 100 nodes
            neighbors = []
            # Connect to right neighbor
            if i % 10 != 0:
                neighbors.append((i + 1, 10, []))
            # Connect to bottom neighbor
            if i <= 90:
                neighbors.append((i + 10, 10, []))
            graph[i] = neighbors

        # Add some congestion
        if graph.get(1) and len(graph[1]) > 0:
            graph[1][0] = (graph[1][0][0], graph[1][0][1], [(0, 100, 2.0)])

        # Find route from top-left to bottom-right
        self.assertNotEqual(find_optimal_route(graph, 1, 100, 0), -1)

    def test_start_equals_end(self):
        # Test when start and end are the same
        graph = {
            1: [(2, 10, [])],
            2: []
        }
        self.assertEqual(find_optimal_route(graph, 1, 1, 0), 0)

if __name__ == '__main__':
    unittest.main()