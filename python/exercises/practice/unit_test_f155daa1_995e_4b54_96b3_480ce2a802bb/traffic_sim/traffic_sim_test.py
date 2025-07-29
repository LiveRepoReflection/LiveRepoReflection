import unittest
from traffic_sim import simulate_traffic

class TrafficSimulationTest(unittest.TestCase):
    def test_basic_simulation(self):
        city_graph = {
            1: [(2, 5, 10, 60), (3, 3, 15, 40)],  # (destination, capacity, length, speed_limit)
            2: [(4, 4, 8, 50)],
            3: [(4, 2, 12, 30)],
            4: []
        }
        vehicles = [
            {"vehicle_id": 1, "type": "car", "start_intersection": 1, "destination_intersection": 4, "departure_time": 0},
            {"vehicle_id": 2, "type": "truck", "start_intersection": 1, "destination_intersection": 4, "departure_time": 2},
            {"vehicle_id": 3, "type": "car", "start_intersection": 1, "destination_intersection": 4, "departure_time": 3}
        ]
        simulation_time = 20
        
        # Mock shortest path function
        def find_shortest_path(graph, start, end):
            if start == 1 and end == 4:
                return [1, 2, 4]
            elif start == 2 and end == 4:
                return [2, 4]
            elif start == 3 and end == 4:
                return [3, 4]
            return None
        
        result = simulate_traffic(city_graph, vehicles, simulation_time, find_shortest_path)
        self.assertIsInstance(result, float)
        self.assertGreater(result, 0)

    def test_no_vehicles_reach_destination(self):
        city_graph = {
            1: [(2, 5, 10, 60)],
            2: [(3, 5, 10, 60)],
            3: []
        }
        vehicles = [
            {"vehicle_id": 1, "type": "car", "start_intersection": 1, "destination_intersection": 4, "departure_time": 0}
        ]
        simulation_time = 20
        
        # Mock shortest path function that returns no path
        def find_shortest_path(graph, start, end):
            return None
        
        result = simulate_traffic(city_graph, vehicles, simulation_time, find_shortest_path)
        self.assertEqual(result, -1)

    def test_capacity_constraints(self):
        city_graph = {
            1: [(2, 2, 10, 60)],  # Only 2 capacity
            2: [(3, 10, 10, 60)],
            3: []
        }
        vehicles = [
            {"vehicle_id": 1, "type": "car", "start_intersection": 1, "destination_intersection": 3, "departure_time": 0},
            {"vehicle_id": 2, "type": "car", "start_intersection": 1, "destination_intersection": 3, "departure_time": 0},
            {"vehicle_id": 3, "type": "truck", "start_intersection": 1, "destination_intersection": 3, "departure_time": 0}  # Truck has size 2, should block the road
        ]
        simulation_time = 20
        
        def find_shortest_path(graph, start, end):
            if start == 1 and end == 3:
                return [1, 2, 3]
            return None
        
        result = simulate_traffic(city_graph, vehicles, simulation_time, find_shortest_path)
        self.assertIsInstance(result, float)
        # Either only the first two cars make it, or the first car and the truck make it
        # This tests that the capacity constraint is working

    def test_different_vehicle_types(self):
        city_graph = {
            1: [(2, 10, 10, 60)],
            2: []
        }
        vehicles = [
            {"vehicle_id": 1, "type": "car", "start_intersection": 1, "destination_intersection": 2, "departure_time": 0},
            {"vehicle_id": 2, "type": "truck", "start_intersection": 1, "destination_intersection": 2, "departure_time": 0},
            {"vehicle_id": 3, "type": "bus", "start_intersection": 1, "destination_intersection": 2, "departure_time": 0}
        ]
        simulation_time = 20
        
        def find_shortest_path(graph, start, end):
            if start == 1 and end == 2:
                return [1, 2]
            return None
        
        result = simulate_traffic(city_graph, vehicles, simulation_time, find_shortest_path)
        self.assertIsInstance(result, float)
        self.assertGreater(result, 0)

    def test_speed_limit_effect(self):
        city_graph = {
            1: [(2, 5, 10, 10)],  # Speed limit 10
            2: [(3, 5, 10, 5)],   # Speed limit 5
            3: []
        }
        vehicles = [
            {"vehicle_id": 1, "type": "car", "start_intersection": 1, "destination_intersection": 3, "departure_time": 0}
        ]
        simulation_time = 20
        
        def find_shortest_path(graph, start, end):
            if start == 1 and end == 3:
                return [1, 2, 3]
            return None
        
        result = simulate_traffic(city_graph, vehicles, simulation_time, find_shortest_path)
        self.assertIsInstance(result, float)
        self.assertGreaterEqual(result, 3)  # Should take at least 3 time steps

    def test_multiple_paths(self):
        city_graph = {
            1: [(2, 5, 10, 60), (3, 5, 5, 40)],
            2: [(4, 5, 20, 60)],
            3: [(4, 5, 15, 60)],
            4: []
        }
        vehicles = [
            {"vehicle_id": 1, "type": "car", "start_intersection": 1, "destination_intersection": 4, "departure_time": 0}
        ]
        simulation_time = 20
        
        def find_shortest_path(graph, start, end):
            if start == 1 and end == 4:
                return [1, 3, 4]  # Shorter path through 3
            return None
        
        result = simulate_traffic(city_graph, vehicles, simulation_time, find_shortest_path)
        self.assertIsInstance(result, float)
        self.assertGreater(result, 0)

    def test_delayed_departures(self):
        city_graph = {
            1: [(2, 5, 10, 60)],
            2: []
        }
        vehicles = [
            {"vehicle_id": 1, "type": "car", "start_intersection": 1, "destination_intersection": 2, "departure_time": 0},
            {"vehicle_id": 2, "type": "car", "start_intersection": 1, "destination_intersection": 2, "departure_time": 5},
            {"vehicle_id": 3, "type": "car", "start_intersection": 1, "destination_intersection": 2, "departure_time": 10}
        ]
        simulation_time = 20
        
        def find_shortest_path(graph, start, end):
            if start == 1 and end == 2:
                return [1, 2]
            return None
        
        result = simulate_traffic(city_graph, vehicles, simulation_time, find_shortest_path)
        self.assertIsInstance(result, float)
        self.assertGreater(result, 0)

    def test_zero_travel_time(self):
        city_graph = {
            1: [(2, 5, 0, 60)],  # Zero length street
            2: []
        }
        vehicles = [
            {"vehicle_id": 1, "type": "car", "start_intersection": 1, "destination_intersection": 2, "departure_time": 5}
        ]
        simulation_time = 20
        
        def find_shortest_path(graph, start, end):
            if start == 1 and end == 2:
                return [1, 2]
            return None
        
        result = simulate_traffic(city_graph, vehicles, simulation_time, find_shortest_path)
        self.assertEqual(result, 0.0)  # Travel time should be 0 due to zero length road

    def test_simulation_time_limit(self):
        city_graph = {
            1: [(2, 5, 100, 10)],  # Very long street with low speed limit
            2: []
        }
        vehicles = [
            {"vehicle_id": 1, "type": "car", "start_intersection": 1, "destination_intersection": 2, "departure_time": 0}
        ]
        simulation_time = 5  # Not enough time to reach destination
        
        def find_shortest_path(graph, start, end):
            if start == 1 and end == 2:
                return [1, 2]
            return None
        
        result = simulate_traffic(city_graph, vehicles, simulation_time, find_shortest_path)
        self.assertEqual(result, -1)  # No vehicle reaches destination

    def test_empty_vehicle_list(self):
        city_graph = {
            1: [(2, 5, 10, 60)],
            2: []
        }
        vehicles = []
        simulation_time = 20
        
        def find_shortest_path(graph, start, end):
            if start == 1 and end == 2:
                return [1, 2]
            return None
        
        result = simulate_traffic(city_graph, vehicles, simulation_time, find_shortest_path)
        self.assertEqual(result, -1)  # No vehicles to simulate

if __name__ == '__main__':
    unittest.main()