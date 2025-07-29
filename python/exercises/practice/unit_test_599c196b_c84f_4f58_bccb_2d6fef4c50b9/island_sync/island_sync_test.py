import unittest
from island_sync import minimum_average_travel_time

class IslandSyncTest(unittest.TestCase):
    def test_simple_graph(self):
        graph = {
            "A": [("B", 10), ("C", 15)],
            "B": [("A", 10), ("D", 12), ("C", 5)],
            "C": [("A", 15), ("B", 5), ("E", 10)],
            "D": [("B", 12), ("F", 1)],
            "E": [("C", 10), ("F", 8)],
            "F": [("D", 1), ("E", 8)]
        }
        observatories = ["A", "F"]
        self.assertAlmostEqual(minimum_average_travel_time(graph, observatories), 23.0, places=6)

    def test_linear_graph(self):
        graph = {
            "A": [("B", 5)],
            "B": [("A", 5), ("C", 3)],
            "C": [("B", 3)]
        }
        observatories = ["A", "C"]
        self.assertAlmostEqual(minimum_average_travel_time(graph, observatories), 8.0, places=6)

    def test_multiple_observatories(self):
        graph = {
            "A": [("B", 1), ("C", 4)],
            "B": [("A", 1), ("C", 2), ("D", 5)],
            "C": [("A", 4), ("B", 2), ("D", 1)],
            "D": [("B", 5), ("C", 1)]
        }
        observatories = ["A", "C", "D"]
        # A to C: 3 (via B), A to D: 4 (via B and C), C to D: 1
        # Total: (3 + 4 + 1) / 3 = 8/3 = 2.6666...
        self.assertAlmostEqual(minimum_average_travel_time(graph, observatories), 2.6666667, places=6)

    def test_disconnected_graph(self):
        graph = {
            "A": [("B", 1)],
            "B": [("A", 1)],
            "C": [("D", 2)],
            "D": [("C", 2)]
        }
        observatories = ["A", "C"]
        self.assertEqual(minimum_average_travel_time(graph, observatories), float('inf'))

    def test_partially_disconnected_observatories(self):
        graph = {
            "A": [("B", 1), ("C", 2)],
            "B": [("A", 1)],
            "C": [("A", 2)],
            "D": [] # Isolated node
        }
        observatories = ["A", "B", "D"]
        self.assertEqual(minimum_average_travel_time(graph, observatories), float('inf'))

    def test_same_observatory_twice(self):
        graph = {
            "A": [("B", 5)],
            "B": [("A", 5)]
        }
        observatories = ["A", "A"]
        # Same observatory doesn't need to communicate with itself
        self.assertEqual(minimum_average_travel_time(graph, observatories), 0.0)

    def test_large_complete_graph(self):
        # Create a complete graph with 20 nodes
        graph = {}
        for i in range(20):
            node = f"Node{i}"
            graph[node] = []
            for j in range(20):
                if i != j:
                    graph[node].append((f"Node{j}", 1))
        
        # Select 5 random observatories
        observatories = [f"Node{i}" for i in range(5)]
        self.assertAlmostEqual(minimum_average_travel_time(graph, observatories), 1.0, places=6)

    def test_large_sparse_graph(self):
        # Create a linear graph with 100 nodes
        graph = {}
        for i in range(100):
            node = f"Node{i}"
            graph[node] = []
            if i > 0:
                graph[node].append((f"Node{i-1}", 1))
            if i < 99:
                graph[node].append((f"Node{i+1}", 1))
        
        # Select observatories at the ends and middle
        observatories = ["Node0", "Node49", "Node99"]
        # Distances: 0-49: 49, 0-99: 99, 49-99: 50
        # Average: (49 + 99 + 50) / 3 = 66
        self.assertAlmostEqual(minimum_average_travel_time(graph, observatories), 66.0, places=6)

    def test_empty_observatories(self):
        graph = {
            "A": [("B", 1)],
            "B": [("A", 1)]
        }
        observatories = []
        # No observatories means no travel time
        self.assertEqual(minimum_average_travel_time(graph, observatories), 0.0)

    def test_single_observatory(self):
        graph = {
            "A": [("B", 1)],
            "B": [("A", 1)]
        }
        observatories = ["A"]
        # Single observatory doesn't need to communicate with anyone
        self.assertEqual(minimum_average_travel_time(graph, observatories), 0.0)

    def test_complex_graph_with_varying_weights(self):
        graph = {
            "A": [("B", 3), ("C", 5), ("D", 9)],
            "B": [("A", 3), ("C", 3), ("E", 4)],
            "C": [("A", 5), ("B", 3), ("D", 2), ("E", 6), ("F", 8)],
            "D": [("A", 9), ("C", 2), ("F", 2)],
            "E": [("B", 4), ("C", 6), ("F", 7)],
            "F": [("C", 8), ("D", 2), ("E", 7)]
        }
        observatories = ["A", "D", "E"]
        # A-D: min(9, 5+2) = 7, A-E: min(3+4, 5+6) = 7, D-E: min(2+6, 2+7) = 8
        # Average: (7 + 7 + 8) / 3 = 7.33333
        self.assertAlmostEqual(minimum_average_travel_time(graph, observatories), 7.3333333, places=6)

    def test_all_nodes_are_observatories(self):
        graph = {
            "A": [("B", 1), ("C", 3)],
            "B": [("A", 1), ("C", 1)],
            "C": [("A", 3), ("B", 1)]
        }
        observatories = ["A", "B", "C"]
        # A-B: 1, A-C: min(3, 1+1) = 2, B-C: 1
        # Average: (1 + 2 + 1) / 3 = 1.33333
        self.assertAlmostEqual(minimum_average_travel_time(graph, observatories), 1.3333333, places=6)

    def test_zero_weight_edges(self):
        graph = {
            "A": [("B", 0), ("C", 5)],
            "B": [("A", 0), ("C", 2)],
            "C": [("A", 5), ("B", 2)]
        }
        observatories = ["A", "C"]
        # A-C: min(5, 0+2) = 2
        self.assertAlmostEqual(minimum_average_travel_time(graph, observatories), 2.0, places=6)

if __name__ == "__main__":
    unittest.main()