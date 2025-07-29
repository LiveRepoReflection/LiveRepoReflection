import unittest
from optimal_delivery import optimize_routes

def calculate_cost(city_map, route):
    cost = 0
    for i in range(len(route) - 1):
        u, v = route[i], route[i+1]
        # Find the edge from u to v. Assume city_map is undirected.
        edge_found = False
        for neighbor, weight in city_map.get(u, []):
            if neighbor == v:
                cost += weight
                edge_found = True
                break
        if not edge_found:
            # If edge not found in u's list, check v's list (should not happen if graph is consistent)
            for neighbor, weight in city_map.get(v, []):
                if neighbor == u:
                    cost += weight
                    edge_found = True
                    break
        if not edge_found:
            # Inconsistent graph: no connection between u and v
            raise ValueError(f"Edge between {u} and {v} not found in city_map")
    return cost

class TestOptimalDelivery(unittest.TestCase):
    def test_trivial_delivery(self):
        # Graph: single edge between 0 and 1
        city_map = {
            0: [(1, 5)],
            1: [(0, 5)]
        }
        packages = [
            (0, 1, "medium")
        ]
        time_windows = {}  # no time window constraint
        result = optimize_routes(city_map, packages, time_windows)
        self.assertIn(0, result)
        route = result[0]
        self.assertEqual(route[0], 0)
        self.assertEqual(route[-1], 1)
        cost = calculate_cost(city_map, route)
        self.assertEqual(cost, 5)

    def test_same_source_destination(self):
        city_map = {
            0: [],
            1: []
        }
        packages = [
            (0, 0, "low"),
            (1, 1, "high")
        ]
        time_windows = {}
        result = optimize_routes(city_map, packages, time_windows)
        # For same source and destination, route should contain only one node and cost 0
        for idx in [0, 1]:
            self.assertIn(idx, result)
            route = result[idx]
            self.assertEqual(len(route), 1)
            self.assertEqual(route[0], packages[idx][0])
            self.assertEqual(calculate_cost(city_map, route), 0)

    def test_time_window_success(self):
        # Construct a simple graph where a valid route meets time window
        city_map = {
            0: [(1, 3)],
            1: [(0, 3), (2, 4)],
            2: [(1, 4)]
        }
        packages = [
            (0, 2, "high")
        ]
        # Set time window that the cost should satisfy
        # The only route is 0 -> 1 -> 2 with cost 3+4 = 7, so set window [7, 10]
        time_windows = {
            (0, 2): (7, 10)
        }
        result = optimize_routes(city_map, packages, time_windows)
        self.assertIn(0, result)
        route = result[0]
        self.assertEqual(route[0], 0)
        self.assertEqual(route[-1], 2)
        cost = calculate_cost(city_map, route)
        self.assertGreaterEqual(cost, 7)
        self.assertLessEqual(cost, 10)

    def test_time_window_failure(self):
        # Graph similar as before
        city_map = {
            0: [(1, 3)],
            1: [(0, 3), (2, 4)],
            2: [(1, 4)]
        }
        packages = [
            (0, 2, "high")
        ]
        # Set time window impossible to achieve: the only route costs 7, but time window is [0, 5]
        time_windows = {
            (0, 2): (0, 5)
        }
        result = optimize_routes(city_map, packages, time_windows)
        # Package 0 should be undeliverable so not included in result
        self.assertNotIn(0, result)

    def test_no_route(self):
        # Graph with disconnected components
        city_map = {
            0: [(1, 2)],
            1: [(0, 2)],
            2: [],  # Node 2 is isolated from nodes 0 and 1
            3: [(4, 1)],
            4: [(3, 1)]
        }
        packages = [
            (0, 2, "medium"),  # No route exists from 0 to 2
            (3, 4, "low")      # Route exists between 3 and 4
        ]
        time_windows = {}
        result = optimize_routes(city_map, packages, time_windows)
        self.assertNotIn(0, result)
        self.assertIn(1, result)
        route = result[1]
        self.assertEqual(route[0], 3)
        self.assertEqual(route[-1], 4)
        cost = calculate_cost(city_map, route)
        self.assertEqual(cost, 1)

    def test_priority_ordering(self):
        # Construct a graph where multiple packages exist between same nodes
        city_map = {
            0: [(1, 2)],
            1: [(0, 2), (2, 3)],
            2: [(1, 3)]
        }
        # Two packages from 0 to 2, with different priorities.
        packages = [
            (0, 2, "high"),
            (0, 2, "low")
        ]
        # No time window constraints
        time_windows = {}
        result = optimize_routes(city_map, packages, time_windows)
        # Both packages should be delivered.
        self.assertIn(0, result)
        self.assertIn(1, result)
        route_high = result[0]
        route_low = result[1]
        cost_high = calculate_cost(city_map, route_high)
        cost_low = calculate_cost(city_map, route_low)
        # High priority package's route cost must be less than or equal to low priority's route cost.
        self.assertLessEqual(cost_high, cost_low)

    def test_complex_scenario(self):
        # A more complex grid-like graph
        city_map = {
            0: [(1, 1), (2, 4)],
            1: [(0, 1), (2, 2), (3, 5)],
            2: [(0, 4), (1, 2), (3, 1)],
            3: [(1, 5), (2, 1), (4, 3)],
            4: [(3, 3)]
        }
        packages = [
            (0, 4, "high"),   # Expected optimal path: 0->1->2->3->4 or 0->1->3->4 depending on weights
            (0, 4, "medium"), # Same source/dest with lower priority
            (2, 4, "low"),    # Different source
            (4, 0, "high")    # Reverse path from 4 to 0
        ]
        
        # Set time windows such that only routes with cost <= 10 are valid if applicable.
        time_windows = {
            (0, 4): (0, 10),
            (2, 4): (0, 10),
            (4, 0): (0, 15)
        }
        result = optimize_routes(city_map, packages, time_windows)
        # Ensure deliverable packages are returned and each route starts and ends correctly
        for idx, pkg in enumerate(packages):
            src, dst, _ = pkg
            if (src, dst) in time_windows:
                if idx in result:
                    route = result[idx]
                    self.assertEqual(route[0], src)
                    self.assertEqual(route[-1], dst)
                    cost = calculate_cost(city_map, route)
                    start, end = time_windows[(src, dst)]
                    self.assertGreaterEqual(cost, start)
                    self.assertLessEqual(cost, end)
                else:
                    # In case package is not deliverable, assert it's not included.
                    self.assertNotIn(idx, result)
            else:
                if idx in result:
                    route = result[idx]
                    self.assertEqual(route[0], src)
                    self.assertEqual(route[-1], dst)

        # Check prioritization condition: high priority package(s) should not have a higher cost
        # than any lower priority package delivered.
        delivered = []
        for idx in result:
            pkg = packages[idx]
            src, dst, priority = pkg
            cost = calculate_cost(city_map, result[idx])
            delivered.append((priority, cost))
        # Group packages by priority level
        priority_order = {"high": 0, "medium": 1, "low": 2}
        delivered_sorted = sorted(delivered, key=lambda x: priority_order[x[0]])
        for i in range(len(delivered_sorted)-1):
            self.assertLessEqual(delivered_sorted[i][1], delivered_sorted[i+1][1])

if __name__ == '__main__':
    unittest.main()