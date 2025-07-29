import unittest
from datetime import datetime

# Import the find_optimal_route function from the aev_routing module
from aev_routing import find_optimal_route

def constant_traffic(speed_limit):
    return lambda t: speed_limit

def time_dependent_traffic(speed_limit):
    def traffic(t):
        # If departure is before 8AM, use full speed; otherwise, half the speed limit.
        return speed_limit if t < 8 else speed_limit / 2
    return traffic

def constant_energy_consumption(speed):
    # For testing, assume a constant consumption regardless of speed
    return 0.5  # kWh per kilometer

class TestAEVRouting(unittest.TestCase):
    def test_origin_equals_destination(self):
        # Graph with a single node where origin is destination
        graph = {
            1: {'neighbors': [], 'charging_station': False}
        }
        edges = {}
        aev = {
            'battery_capacity': 100,
            'initial_charge': 50,
            'energy_consumption_rate': constant_energy_consumption,
            'charging_rate': 10,
        }
        origin = 1
        destination = 1
        departure_time = 7.0
        max_travel_time = 1.0

        route = find_optimal_route(graph, edges, aev, origin, destination, departure_time, max_travel_time)
        self.assertEqual(route, [1])

    def test_simple_direct_route(self):
        # Simple direct route with two nodes and one edge
        graph = {
            1: {'neighbors': [2], 'charging_station': False},
            2: {'neighbors': [], 'charging_station': False},
        }
        edges = {
            (1, 2): {
                'length': 10,  # kilometers
                'speed_limit': 100,
                'traffic': constant_traffic(100),
            }
        }
        aev = {
            'battery_capacity': 30,
            'initial_charge': 30,
            'energy_consumption_rate': constant_energy_consumption,
            'charging_rate': 10,
        }
        origin = 1
        destination = 2
        departure_time = 7.5
        max_travel_time = 1.0

        route = find_optimal_route(graph, edges, aev, origin, destination, departure_time, max_travel_time)
        self.assertEqual(route, [1, 2])

    def test_route_with_charging_required(self):
        # Graph with three nodes where a charging stop is required
        graph = {
            1: {'neighbors': [2, 3], 'charging_station': False},
            2: {'neighbors': [3], 'charging_station': True},
            3: {'neighbors': [], 'charging_station': False},
        }
        edges = {
            (1, 2): {
                'length': 40,  # km, energy needed = 40 * 0.5 = 20 kWh
                'speed_limit': 80,
                'traffic': constant_traffic(80),
            },
            (2, 3): {
                'length': 30,  # km, energy needed = 15 kWh
                'speed_limit': 80,
                'traffic': constant_traffic(80),
            },
            (1, 3): {
                'length': 80,  # km, energy needed = 40 kWh but initial charge (20) insufficient
                'speed_limit': 80,
                'traffic': constant_traffic(80),
            }
        }
        aev = {
            'battery_capacity': 50,
            'initial_charge': 20,
            'energy_consumption_rate': constant_energy_consumption,
            'charging_rate': 10,
        }
        origin = 1
        destination = 3
        departure_time = 6.0
        max_travel_time = 3.0

        route = find_optimal_route(graph, edges, aev, origin, destination, departure_time, max_travel_time)
        self.assertEqual(route, [1, 2, 3])

    def test_no_route_due_to_time_constraint(self):
        # Graph with a valid path that exceeds max_travel_time
        graph = {
            1: {'neighbors': [2], 'charging_station': False},
            2: {'neighbors': [], 'charging_station': False},
        }
        edges = {
            (1, 2): {
                'length': 10,
                'speed_limit': 100,
                'traffic': constant_traffic(100),
            }
        }
        aev = {
            'battery_capacity': 30,
            'initial_charge': 30,
            'energy_consumption_rate': constant_energy_consumption,
            'charging_rate': 10,
        }
        origin = 1
        destination = 2
        departure_time = 7.5
        max_travel_time = 0.05  # too small time window

        route = find_optimal_route(graph, edges, aev, origin, destination, departure_time, max_travel_time)
        self.assertIsNone(route)

    def test_time_dependent_traffic(self):
        # Graph with an edge where travel time depends on departure time
        graph = {
            1: {'neighbors': [2], 'charging_station': False},
            2: {'neighbors': [], 'charging_station': False},
        }
        edges = {
            (1, 2): {
                'length': 10,
                'speed_limit': 100,
                'traffic': time_dependent_traffic(100),
            }
        }
        aev = {
            'battery_capacity': 30,
            'initial_charge': 30,
            'energy_consumption_rate': constant_energy_consumption,
            'charging_rate': 10,
        }
        origin = 1
        destination = 2
        
        # Test departure time after 8AM (traffic slowed)
        departure_time_after = 9.0
        max_travel_time = 1.0
        route_after = find_optimal_route(graph, edges, aev, origin, destination, departure_time_after, max_travel_time)
        self.assertEqual(route_after, [1, 2])
        
        # Test departure time before 8AM (full speed)
        departure_time_before = 7.0
        route_before = find_optimal_route(graph, edges, aev, origin, destination, departure_time_before, max_travel_time)
        self.assertEqual(route_before, [1, 2])

if __name__ == '__main__':
    unittest.main()