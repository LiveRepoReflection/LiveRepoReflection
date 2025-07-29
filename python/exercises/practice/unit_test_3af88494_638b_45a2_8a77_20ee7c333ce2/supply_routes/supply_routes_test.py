import unittest
from supply_routes import solve

class SupplyRoutesTest(unittest.TestCase):
    def test_simple_graph(self):
        graph = {
            "WarehouseA": {"Factory1": 10, "DistributionCenterX": 15},
            "Factory1": {"DistributionCenterX": 5, "WarehouseB": 12},
            "DistributionCenterX": {"WarehouseB": 8},
            "WarehouseB": {}
        }
        disrupted_routes = [("WarehouseA", "Factory1")]
        origins = ["WarehouseA", "Factory1"]
        destinations = ["WarehouseB", "DistributionCenterX"]
        
        expected = {
            ("WarehouseA", "WarehouseB"): 23,
            ("WarehouseA", "DistributionCenterX"): 15,
            ("Factory1", "WarehouseB"): 12,
            ("Factory1", "DistributionCenterX"): 5
        }
        
        self.assertEqual(solve(graph, disrupted_routes, origins, destinations), expected)

    def test_no_valid_path(self):
        graph = {
            "A": {"B": 1},
            "B": {"C": 2},
            "C": {"D": 3},
            "D": {}
        }
        disrupted_routes = [("B", "C")]
        origins = ["A"]
        destinations = ["D"]
        
        expected = {("A", "D"): float('inf')}
        self.assertEqual(solve(graph, disrupted_routes, origins, destinations), expected)

    def test_multiple_paths(self):
        graph = {
            "Start": {"A": 1, "B": 2},
            "A": {"End": 3},
            "B": {"End": 1},
            "End": {}
        }
        disrupted_routes = [("Start", "A")]
        origins = ["Start"]
        destinations = ["End"]
        
        expected = {("Start", "End"): 3}  # Through B path
        self.assertEqual(solve(graph, disrupted_routes, origins, destinations), expected)

    def test_complex_graph(self):
        graph = {
            "S1": {"A": 1, "B": 2},
            "S2": {"B": 3, "C": 1},
            "A": {"D": 4, "E": 2},
            "B": {"D": 1, "E": 3},
            "C": {"E": 5},
            "D": {"T1": 2},
            "E": {"T1": 3, "T2": 2},
            "T1": {},
            "T2": {}
        }
        disrupted_routes = [("B", "D"), ("A", "E")]
        origins = ["S1", "S2"]
        destinations = ["T1", "T2"]
        
        result = solve(graph, disrupted_routes, origins, destinations)
        
        # Verify all origin-destination pairs exist
        expected_pairs = [
            ("S1", "T1"), ("S1", "T2"),
            ("S2", "T1"), ("S2", "T2")
        ]
        self.assertEqual(set(result.keys()), set(expected_pairs))

    def test_cyclic_graph(self):
        graph = {
            "A": {"B": 1},
            "B": {"C": 2, "A": 1},
            "C": {"A": 3, "D": 4},
            "D": {}
        }
        disrupted_routes = []
        origins = ["A"]
        destinations = ["D"]
        
        expected = {("A", "D"): 7}  # A->B->C->D
        self.assertEqual(solve(graph, disrupted_routes, origins, destinations), expected)

    def test_all_routes_disrupted(self):
        graph = {
            "A": {"B": 1},
            "B": {"C": 1},
            "C": {}
        }
        disrupted_routes = [("A", "B"), ("B", "C")]
        origins = ["A"]
        destinations = ["C"]
        
        expected = {("A", "C"): float('inf')}
        self.assertEqual(solve(graph, disrupted_routes, origins, destinations), expected)

    def test_large_graph_performance(self):
        # Create a large graph with 1000 nodes
        large_graph = {}
        for i in range(999):
            large_graph[f"Node{i}"] = {f"Node{i+1}": i % 10 + 1}
        large_graph["Node999"] = {}
        
        disrupted_routes = [(f"Node{i}", f"Node{i+1}") for i in range(0, 999, 100)]
        origins = ["Node0"]
        destinations = ["Node999"]
        
        # This should complete within a reasonable time
        result = solve(large_graph, disrupted_routes, origins, destinations)
        self.assertIsInstance(result, dict)
        self.assertIn(("Node0", "Node999"), result)

if __name__ == '__main__':
    unittest.main()