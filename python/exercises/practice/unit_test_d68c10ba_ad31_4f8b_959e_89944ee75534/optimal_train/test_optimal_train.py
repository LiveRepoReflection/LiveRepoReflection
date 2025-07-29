import unittest
import math
from optimal_train import find_optimal_train_network

def is_connected(railway_lines, cities):
    # Build graph to check connectivity
    if not cities:
        return True
    graph = {city: set() for city, _, _ in cities}
    for u, v in railway_lines:
        graph[u].add(v)
        graph[v].add(u)
    visited = set()
    stack = [cities[0][0]]
    while stack:
        node = stack.pop()
        if node not in visited:
            visited.add(node)
            stack.extend(graph[node] - visited)
    return visited == set([city for city, _, _ in cities])

def total_cost_of_network(railway_lines, cities, cost_per_km):
    # Calculate total cost using the Haversine formula
    R = 6371.0
    def haversine(lat1, lon1, lat2, lon2):
        dlat = math.radians(lat2 - lat1)
        dlon = math.radians(lon2 - lon1)
        a = math.sin(dlat / 2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        return R * c
    cost = 0.0
    city_dict = {name: (lat, lon) for name, lat, lon in cities}
    for u, v in railway_lines:
        lat1, lon1 = city_dict[u]
        lat2, lon2 = city_dict[v]
        d = haversine(lat1, lon1, lat2, lon2)
        cost += d * cost_per_km
    return cost

class TestOptimalTrainNetwork(unittest.TestCase):
    def test_budget_too_small(self):
        # When the budget is insufficient to build a connection, expect failure indicators.
        cities = [("A", 0.0, 0.0), ("B", 0.0, 1.0)]
        budget = 0.1  # Too small budget
        cost_per_km = 100.0
        train_speed = 1.0
        
        railway_lines, max_travel_time, total_cost = find_optimal_train_network(cities, budget, cost_per_km, train_speed)
        self.assertEqual(railway_lines, [])
        self.assertEqual(max_travel_time, float('inf'))
        self.assertEqual(total_cost, float('inf'))
    
    def test_single_connection(self):
        # Test with two cities that can be connected with the given budget
        cities = [("A", 0.0, 0.0), ("B", 0.0, 1.0)]
        cost_per_km = 100.0
        train_speed = 1.0
        
        # Calculate approximate distance using Haversine formula
        R = 6371.0
        def haversine(lat1, lon1, lat2, lon2):
            dlat = math.radians(lat2 - lat1)
            dlon = math.radians(lon2 - lon1)
            a = math.sin(dlat / 2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2)**2
            c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
            return R * c
        
        distance = haversine(0.0, 0.0, 0.0, 1.0)
        total_possible_cost = distance * cost_per_km
        budget = total_possible_cost + 10.0
        
        railway_lines, max_travel_time, total_cost = find_optimal_train_network(cities, budget, cost_per_km, train_speed)
        
        # Verify connectivity, cost and travel time approximately
        self.assertTrue(is_connected(railway_lines, cities))
        self.assertAlmostEqual(total_cost, total_possible_cost, delta=1.0)
        self.assertAlmostEqual(max_travel_time, distance, delta=0.1)
    
    def test_multiple_cities(self):
        # Test with multiple cities to ensure a spanning network is produced within the budget
        cities = [
            ("A", 34.0522, -118.2437),
            ("B", 37.7749, -122.4194),
            ("C", 40.7128, -74.0060),
            ("D", 41.8781, -87.6298)
        ]
        cost_per_km = 10.0
        train_speed = 1.0
        budget = 100000.0  # Sufficiently high budget
        
        railway_lines, max_travel_time, total_cost = find_optimal_train_network(cities, budget, cost_per_km, train_speed)
        
        # Check that the network is connected
        self.assertTrue(is_connected(railway_lines, cities))
        
        # Verify that the total cost does not exceed the provided budget
        computed_cost = total_cost_of_network(railway_lines, cities, cost_per_km)
        self.assertLessEqual(computed_cost, budget + 1e-6)
        
        # Maximum travel time should be a positive finite number
        self.assertGreater(max_travel_time, 0.0)
        self.assertNotEqual(max_travel_time, float('inf'))
    
    def test_single_city(self):
        # For a single city, expect no railway lines and zero cost and travel time.
        cities = [("A", 34.0522, -118.2437)]
        budget = 1000.0
        cost_per_km = 10.0
        train_speed = 1.0
        
        railway_lines, max_travel_time, total_cost = find_optimal_train_network(cities, budget, cost_per_km, train_speed)
        
        self.assertEqual(railway_lines, [])
        self.assertEqual(max_travel_time, 0.0)
        self.assertEqual(total_cost, 0.0)

if __name__ == '__main__':
    unittest.main()