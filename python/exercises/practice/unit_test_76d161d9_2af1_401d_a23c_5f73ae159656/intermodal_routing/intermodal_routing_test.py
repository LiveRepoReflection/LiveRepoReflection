import unittest
from intermodal_routing import find_routes

class TestIntermodalRouting(unittest.TestCase):
    def setUp(self):
        # Common transfer costs used in all tests
        self.transfer_costs = {
            "truck": {"truck": 0, "train": 20, "ship": 30},
            "train": {"truck": 20, "train": 0, "ship": 25},
            "ship": {"truck": 30, "train": 25, "ship": 0}
        }

    def test_single_edge_route(self):
        # Test 1: Single mode (truck) with no transfer required.
        locations = [
            {"name": "A", "truck": True, "train": False, "ship": False},
            {"name": "B", "truck": True, "train": False, "ship": False}
        ]
        edges = [
            {"source": "A", "destination": "B", "mode": "truck", "cost": 100, "time": 10, "capacity": 10}
        ]
        od_pairs = [
            {"origin": "A", "destination": "B", "quantity": 5, "time_window": [0, 20]}
        ]
        routes = find_routes(locations, edges, self.transfer_costs, od_pairs)
        self.assertEqual(len(routes), 1)
        route = routes[0]
        # Expected: direct route with no transfer cost, within capacity so no extra cost/time
        self.assertEqual(route["nodes"], ["A", "B"])
        self.assertEqual(len(route["edges"]), 1)
        self.assertEqual(route["total_cost"], 100)
        self.assertEqual(route["total_time"], 10)
        self.assertTrue(route["time_window_met"])

    def test_transfer_route(self):
        # Test 2: Route that requires a transfer from truck to train.
        locations = [
            {"name": "A", "truck": True, "train": False, "ship": False},
            {"name": "B", "truck": True, "train": True, "ship": False},
            {"name": "C", "truck": False, "train": True, "ship": False}
        ]
        edges = [
            {"source": "A", "destination": "B", "mode": "truck", "cost": 50, "time": 5, "capacity": 10},
            {"source": "B", "destination": "C", "mode": "train", "cost": 70, "time": 7, "capacity": 10}
        ]
        od_pairs = [
            {"origin": "A", "destination": "C", "quantity": 5, "time_window": [0, 20]}
        ]
        routes = find_routes(locations, edges, self.transfer_costs, od_pairs)
        self.assertEqual(len(routes), 1)
        route = routes[0]
        # Expected: cost = 50 (A->B) + 20 (transfer truck->train) + 70 (B->C) = 140, time = 5+7 = 12.
        self.assertEqual(route["nodes"], ["A", "B", "C"])
        self.assertEqual(len(route["edges"]), 2)
        self.assertEqual(route["total_cost"], 140)
        self.assertEqual(route["total_time"], 12)
        self.assertTrue(route["time_window_met"])

    def test_capacity_constraint(self):
        # Test 3: Route where the quantity exceeds the capacity leading to linear increase in cost and time.
        locations = [
            {"name": "A", "truck": True, "train": False, "ship": False},
            {"name": "B", "truck": True, "train": False, "ship": False}
        ]
        edges = [
            {"source": "A", "destination": "B", "mode": "truck", "cost": 100, "time": 10, "capacity": 5}
        ]
        od_pairs = [
            {"origin": "A", "destination": "B", "quantity": 8, "time_window": [0, 30]}
        ]
        routes = find_routes(locations, edges, self.transfer_costs, od_pairs)
        self.assertEqual(len(routes), 1)
        route = routes[0]
        # Excess quantity = 3. Assume cost and time each increase by 1 unit per unit above capacity.
        # Expected: cost = 100 + 3 = 103, time = 10 + 3 = 13.
        self.assertEqual(route["nodes"], ["A", "B"])
        self.assertEqual(route["total_cost"], 103)
        self.assertEqual(route["total_time"], 13)
        self.assertTrue(route["time_window_met"])

    def test_time_window_violation(self):
        # Test 4: Route that does not meet the time window constraint.
        locations = [
            {"name": "A", "truck": True, "train": False, "ship": False},
            {"name": "B", "truck": True, "train": False, "ship": False}
        ]
        edges = [
            {"source": "A", "destination": "B", "mode": "truck", "cost": 100, "time": 25, "capacity": 10}
        ]
        od_pairs = [
            {"origin": "A", "destination": "B", "quantity": 5, "time_window": [0, 20]}
        ]
        routes = find_routes(locations, edges, self.transfer_costs, od_pairs)
        self.assertEqual(len(routes), 1)
        route = routes[0]
        # Although a route exists, its total time exceeds the time window.
        self.assertEqual(route["nodes"], ["A", "B"])
        self.assertEqual(route["total_cost"], 100)
        self.assertEqual(route["total_time"], 25)
        self.assertFalse(route["time_window_met"])

    def test_no_route_found(self):
        # Test 5: Scenario where no valid route exists between origin and destination.
        locations = [
            {"name": "A", "truck": True, "train": False, "ship": False},
            {"name": "B", "truck": True, "train": False, "ship": False},
            {"name": "C", "truck": True, "train": False, "ship": False}
        ]
        edges = [
            {"source": "A", "destination": "B", "mode": "truck", "cost": 50, "time": 5, "capacity": 10}
        ]
        od_pairs = [
            {"origin": "A", "destination": "C", "quantity": 5, "time_window": [0, 20]}
        ]
        routes = find_routes(locations, edges, self.transfer_costs, od_pairs)
        self.assertEqual(len(routes), 1)
        route = routes[0]
        # Expected: When no route is found, the function should indicate this clearly.
        # Here, we assume that a route with "nodes" set to None indicates no valid route.
        self.assertIsNone(route["nodes"])
        self.assertIsNone(route.get("edges"))
        self.assertIsNone(route.get("total_cost"))
        self.assertIsNone(route.get("total_time"))
        # We can also check for a specific flag if implemented, for instance "found" == False.
        self.assertFalse(route.get("time_window_met", True))

if __name__ == '__main__':
    unittest.main()