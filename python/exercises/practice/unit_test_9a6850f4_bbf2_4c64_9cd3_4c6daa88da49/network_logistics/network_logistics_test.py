import unittest
from collections import defaultdict, deque

# Assuming the existence of a function design_network in network_logistics.py
from network_logistics import design_network

def build_route_dict(potential_routes):
    # Build a dictionary to lookup (u, v) -> (cost, capacity) in either order.
    route_dict = {}
    for u, v, cost, capacity in potential_routes:
        route_dict[frozenset((u, v))] = (cost, capacity)
    return route_dict

def total_network_cost(selected_routes, route_dict):
    total = 0
    for route in selected_routes:
        key = frozenset(route)
        cost, _ = route_dict.get(key, (0, 0))
        total += cost
    return total

def check_latency(selected_routes, route_dict, max_latency):
    # Check that each selected edge adheres to the latency constraint (1/capacity <= max_latency).
    for route in selected_routes:
        key = frozenset(route)
        _, capacity = route_dict.get(key, (None, None))
        if capacity is None or (1 / capacity) > max_latency:
            return False
    return True

def check_connectivity(selected_routes, required_nodes):
    # Build graph from selected_routes and check that all required_nodes are in one connected component.
    graph = defaultdict(set)
    for u, v in selected_routes:
        graph[u].add(v)
        graph[v].add(u)
    if not required_nodes:
        return True
    visited = set()
    start = next(iter(required_nodes))
    queue = deque([start])
    while queue:
        node = queue.popleft()
        if node in visited:
            continue
        visited.add(node)
        for neighbor in graph[node]:
            if neighbor not in visited:
                queue.append(neighbor)
    return required_nodes.issubset(visited)

class NetworkLogisticsTest(unittest.TestCase):
    def test_negative_cost_error(self):
        # Test that negative cost in a potential route raises an error.
        locations = [
            {"id": 1, "demand": 5},
            {"id": 2, "demand": -5}
        ]
        # Introducing a negative cost here.
        potential_routes = [
            (1, 2, -10, 10)
        ]
        budget = 50
        max_latency = 0.2
        with self.assertRaises(ValueError):
            design_network(locations, potential_routes, budget, max_latency)

    def test_basic_valid_network(self):
        # Test with a simple scenario with a unique valid solution.
        locations = [
            {"id": 1, "demand": 5},
            {"id": 2, "demand": -3},
            {"id": 3, "demand": -2}
        ]
        potential_routes = [
            (1, 2, 10, 10),
            (1, 3, 15, 10),
            (2, 3, 5, 10)
        ]
        budget = 30
        max_latency = 0.2
        selected_routes = design_network(locations, potential_routes, budget, max_latency)
        # Build a lookup dictionary for cost and capacity.
        route_dict = build_route_dict(potential_routes)
        # Check that each required location is connected.
        required_nodes = {loc["id"] for loc in locations if loc["demand"] != 0}
        self.assertTrue(check_connectivity(selected_routes, required_nodes), "Network is not fully connected.")
        # Check budget constraint.
        cost = total_network_cost(selected_routes, route_dict)
        self.assertLessEqual(cost, budget, "Total cost exceeds budget.")
        # Check latency constraint.
        self.assertTrue(check_latency(selected_routes, route_dict, max_latency), "Latency constraint violated.")

    def test_unconnected_network_error(self):
        # Test scenario where it's impossible to connect all required nodes.
        locations = [
            {"id": 1, "demand": 4},
            {"id": 2, "demand": -4},
            {"id": 3, "demand": 0}  # isolated node with no demand and no connecting routes needed
        ]
        potential_routes = [
            (1, 3, 5, 10)
            # Node 2 is not connected to any route.
        ]
        budget = 20
        max_latency = 0.2
        with self.assertRaises(ValueError):
            design_network(locations, potential_routes, budget, max_latency)

    def test_optimal_cost_network(self):
        # Test that the solution finds the network with the minimal total cost.
        # In this scenario, multiple valid solutions exist, but one is optimal.
        locations = [
            {"id": 1, "demand": 4},
            {"id": 2, "demand": -3},
            {"id": 3, "demand": -1}
        ]
        potential_routes = [
            (1, 2, 5, 10),   # Edge A
            (1, 3, 8, 10),   # Edge B
            (2, 3, 1, 10)    # Edge C
        ]
        budget = 20
        max_latency = 0.2
        selected_routes = design_network(locations, potential_routes, budget, max_latency)
        route_dict = build_route_dict(potential_routes)
        total_cost = total_network_cost(selected_routes, route_dict)
        # The optimal solution should choose routes (1,2) and (2,3) with total cost 6.
        self.assertEqual(total_cost, 6, "Optimal cost network not found.")
        # Verify connectivity.
        required_nodes = {loc["id"] for loc in locations if loc["demand"] != 0}
        self.assertTrue(check_connectivity(selected_routes, required_nodes), "Network connectivity failed.")
        # Verify latency.
        self.assertTrue(check_latency(selected_routes, route_dict, max_latency), "Latency constraint violated.")

    def test_zero_demand_bridge(self):
        # Test scenario where a node with zero demand is used as a bridging node.
        locations = [
            {"id": 1, "demand": 3},
            {"id": 2, "demand": -3},
            {"id": 3, "demand": 0}
        ]
        potential_routes = [
            (1, 3, 2, 10),
            (3, 2, 2, 10),
            (1, 2, 10, 10)
        ]
        budget = 20
        max_latency = 0.2
        selected_routes = design_network(locations, potential_routes, budget, max_latency)
        route_dict = build_route_dict(potential_routes)
        total_cost = total_network_cost(selected_routes, route_dict)
        # The optimal solution should choose (1,3) and (3,2) with total cost 4.
        self.assertEqual(total_cost, 4, "Bridge node not used optimally.")
        # Verify that nodes with non-zero demand are connected.
        required_nodes = {loc["id"] for loc in locations if loc["demand"] != 0}
        self.assertTrue(check_connectivity(selected_routes, required_nodes), "Network connectivity failed.")
        self.assertTrue(check_latency(selected_routes, route_dict, max_latency), "Latency constraint violated.")

if __name__ == '__main__':
    unittest.main()