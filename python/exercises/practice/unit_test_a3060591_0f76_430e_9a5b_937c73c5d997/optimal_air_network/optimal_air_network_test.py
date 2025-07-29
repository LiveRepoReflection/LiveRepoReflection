import unittest
from math import radians, sin, cos, sqrt, atan2
import optimal_air_network

def haversine(lat1, lon1, lat2, lon2):
    R = 6371  # Earth's radius in km
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat / 2) ** 2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    return R * c

def is_connected(num_nodes, edges):
    if num_nodes == 0:
        return True
    graph = {i: [] for i in range(num_nodes)}
    for u, v in edges:
        graph[u].append(v)
        graph[v].append(u)
    visited = set()
    def dfs(node):
        visited.add(node)
        for neighbor in graph[node]:
            if neighbor not in visited:
                dfs(neighbor)
    dfs(0)
    return len(visited) == num_nodes

class OptimalAirNetworkTest(unittest.TestCase):

    def test_single_city(self):
        cities = [(40.0, -70.0)]
        airports = [(40.0, -70.0, 100, 1)]
        route_difficulty_factor = 2
        result = optimal_air_network.design_network(cities, airports, route_difficulty_factor)
        total_cost, max_travel_time, airport_locations, flight_routes = result

        # For a single city, expect only one airport to be built and no flight routes.
        self.assertEqual(airport_locations, [0])
        self.assertEqual(flight_routes, [])
        self.assertEqual(total_cost, 100)
        self.assertEqual(max_travel_time, 0)

    def test_two_cities(self):
        cities = [(40.0, -70.0), (42.0, -71.0)]
        airports = [
            (40.0, -70.0, 150, 2),
            (42.0, -71.0, 200, 2)
        ]
        route_difficulty_factor = 1
        result = optimal_air_network.design_network(cities, airports, route_difficulty_factor)
        total_cost, max_travel_time, airport_locations, flight_routes = result

        # Both potential airports must be selected
        self.assertEqual(set(airport_locations), {0, 1})
        num_nodes = len(airport_locations)
        self.assertTrue(is_connected(num_nodes, flight_routes))

        # Verify that flight route degree does not exceed each airport's capacity.
        degree_counts = [0] * num_nodes
        for u, v in flight_routes:
            degree_counts[u] += 1
            degree_counts[v] += 1
        for i in range(num_nodes):
            airport_index = airport_locations[i]
            self.assertLessEqual(degree_counts[i], airports[airport_index][3])

        # Check maximum travel time for the direct connection between the two airports.
        lat1, lon1, _, _ = airports[airport_locations[0]]
        lat2, lon2, _, _ = airports[airport_locations[1]]
        distance = haversine(lat1, lon1, lat2, lon2)
        expected_time = distance / 800  # average_speed constant
        self.assertAlmostEqual(max_travel_time, expected_time, places=3)

    def test_three_cities(self):
        cities = [(40.0, -70.0), (41.0, -71.0), (42.0, -72.0)]
        airports = [
            (40.0, -70.0, 100, 2),
            (41.0, -71.0, 120, 2),
            (42.0, -72.0, 150, 2)
        ]
        route_difficulty_factor = 2
        result = optimal_air_network.design_network(cities, airports, route_difficulty_factor)
        total_cost, max_travel_time, airport_locations, flight_routes = result

        # All potential airports should be built for comprehensive connectivity.
        self.assertEqual(set(airport_locations), {0, 1, 2})
        num_nodes = len(airport_locations)
        self.assertTrue(is_connected(num_nodes, flight_routes))

        # Validate that the number of routes from each airport does not exceed its capacity.
        degree_counts = [0] * num_nodes
        for u, v in flight_routes:
            degree_counts[u] += 1
            degree_counts[v] += 1
        for i in range(num_nodes):
            airport_index = airport_locations[i]
            self.assertLessEqual(degree_counts[i], airports[airport_index][3])

        # Confirm that total_cost is not less than the sum of all individual airport construction costs.
        expected_min_cost = sum([airports[i][2] for i in airport_locations])
        self.assertGreaterEqual(total_cost, expected_min_cost)

    def test_no_airports(self):
        cities = [(40.0, -70.0), (41.0, -71.0)]
        airports = []
        route_difficulty_factor = 1
        result = optimal_air_network.design_network(cities, airports, route_difficulty_factor)
        total_cost, max_travel_time, airport_locations, flight_routes = result

        # With no available airport locations, connectivity cannot be achieved.
        self.assertEqual(max_travel_time, float('inf'))
        self.assertEqual(airport_locations, [])
        self.assertEqual(flight_routes, [])

if __name__ == '__main__':
    unittest.main()