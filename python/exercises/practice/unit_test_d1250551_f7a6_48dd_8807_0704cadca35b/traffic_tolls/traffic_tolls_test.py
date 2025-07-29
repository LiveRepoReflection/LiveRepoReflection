import unittest
from traffic_tolls import optimize_tolls

class TestTrafficTolls(unittest.TestCase):
    def test_single_path(self):
        # Graph with only one available path: optimal tolls should be 0 for each edge.
        graph = {
            'A': {'B': 10},
            'B': {'C': 15},
            'C': {'D': 20}
        }
        source = 'A'
        destination = 'D'
        start_time = 480  # 8:00 AM
        end_time = 540    # 9:00 AM
        num_commuters = 100
        
        # Simple predict_traffic function: always returns 1.0 multiplier.
        def predict_traffic(start, end, current_time):
            return 1.0

        tolls = optimize_tolls(graph, source, destination, start_time, end_time, num_commuters, predict_traffic)
        
        # For a single-path network the optimal toll likely is 0 on each segment.
        expected_edges = [('A', 'B'), ('B', 'C'), ('C', 'D')]
        for edge in expected_edges:
            toll = tolls.get(edge, 0)
            self.assertIsInstance(toll, int, f"Toll for edge {edge} is not an integer")
            self.assertGreaterEqual(toll, 0, f"Toll for edge {edge} is negative")
            self.assertEqual(toll, 0, f"For a single path, expected toll of 0 for edge {edge}")

    def test_parallel_paths(self):
        # Graph with two alternative paths from A to D.
        graph = {
            'A': {'B': 5, 'C': 8},
            'B': {'D': 5},
            'C': {'D': 4}
        }
        source = 'A'
        destination = 'D'
        start_time = 540  # 9:00 AM
        end_time = 600    # 10:00 AM
        num_commuters = 200

        # predict_traffic returns constant multiplier 1.0 for all edges.
        def predict_traffic(start, end, current_time):
            return 1.0
        
        tolls = optimize_tolls(graph, source, destination, start_time, end_time, num_commuters, predict_traffic)
        valid_edges = {('A', 'B'), ('A', 'C'), ('B', 'D'), ('C', 'D')}
        
        # Check that the keys in tolls are valid and all toll values are non-negative integers.
        for key, value in tolls.items():
            self.assertIn(key, valid_edges, f"Unexpected edge key {key} in tolls")
            self.assertIsInstance(value, int, f"Toll value for edge {key} is not an integer")
            self.assertGreaterEqual(value, 0, f"Toll value for edge {key} is negative")
        
        # Additionally, check for each road segment in the graph that returned toll (or 0 if absent) is an integer and non-negative.
        for start in graph:
            for end in graph[start]:
                toll = tolls.get((start, end), 0)
                self.assertIsInstance(toll, int, f"Toll for edge ({start}, {end}) is not an integer")
                self.assertGreaterEqual(toll, 0, f"Toll for edge ({start}, {end}) is negative")

    def test_variable_congestion(self):
        # Graph where predict_traffic returns different multipliers.
        graph = {
            'A': {'B': 7, 'C': 10},
            'B': {'D': 6},
            'C': {'D': 4},
            'D': {'E': 5}
        }
        source = 'A'
        destination = 'E'
        start_time = 600   # 10:00 AM
        end_time = 660     # 11:00 AM
        num_commuters = 150

        # predict_traffic function returns different values based on the edge.
        def predict_traffic(start, end, current_time):
            if (start, end) == ('A', 'B'):
                return 1.3
            elif (start, end) == ('A', 'C'):
                return 1.5
            elif (start, end) == ('B', 'D'):
                return 1.0
            elif (start, end) == ('C', 'D'):
                return 1.2
            elif (start, end) == ('D', 'E'):
                return 1.0
            return 1.0
        
        tolls = optimize_tolls(graph, source, destination, start_time, end_time, num_commuters, predict_traffic)
        valid_edges = {('A', 'B'), ('A', 'C'), ('B', 'D'), ('C', 'D'), ('D', 'E')}
        
        # Check that each toll provided is a non-negative integer and belongs to the valid set of edges.
        for key, value in tolls.items():
            self.assertIn(key, valid_edges, f"Edge {key} is not a valid edge in the graph")
            self.assertIsInstance(value, int, f"Toll for edge {key} is not an integer")
            self.assertGreaterEqual(value, 0, f"Toll for edge {key} is negative")
        
        # Check for all edges in the graph that the toll value returned (or assumed 0) satisfies the invariant.
        for start in graph:
            for end in graph[start]:
                toll = tolls.get((start, end), 0)
                self.assertIsInstance(toll, int, f"Toll for edge ({start}, {end}) is not an integer")
                self.assertGreaterEqual(toll, 0, f"Toll for edge ({start}, {end}) is negative")


if __name__ == '__main__':
    unittest.main()