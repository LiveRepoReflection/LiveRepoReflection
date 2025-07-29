import unittest
from traffic_pilot import simulate_traffic

class TrafficPilotTest(unittest.TestCase):
    def test_no_vehicles(self):
        city_graph = {
            0: {1: {'capacity': 10, 'travel_time': 5}},
            1: {2: {'capacity': 10, 'travel_time': 10}},
            2: {}
        }
        vehicles = []
        simulation_time = 100
        result = simulate_traffic(city_graph, vehicles, simulation_time)
        self.assertEqual(result.get("average_travel_time", None), 0.0)

    def test_same_origin_destination(self):
        city_graph = {
            0: {1: {'capacity': 10, 'travel_time': 5}},
            1: {0: {'capacity': 10, 'travel_time': 5}},
        }
        vehicles = [
            {'start_time': 0, 'origin': 0, 'destination': 0, 'size': 5}
        ]
        simulation_time = 50
        result = simulate_traffic(city_graph, vehicles, simulation_time)
        # Vehicle is already at destination so travel time should be 0.
        self.assertEqual(result.get("average_travel_time", None), 0.0)

    def test_single_route_success(self):
        # A simple route from 0 -> 1 -> 2.
        city_graph = {
            0: {1: {'capacity': 10, 'travel_time': 5}},
            1: {2: {'capacity': 10, 'travel_time': 10}},
            2: {}
        }
        vehicles = [
            {'start_time': 0, 'origin': 0, 'destination': 2, 'size': 3}
        ]
        simulation_time = 50
        result = simulate_traffic(city_graph, vehicles, simulation_time)
        # Expected travel time is 5 + 10 = 15.
        self.assertAlmostEqual(result.get("average_travel_time", None), 15.0)

    def test_multiple_vehicles_congestion(self):
        # Test routing when multiple vehicles may cause congestion,
        # requiring re-routing or delayed entries due to capacity limits.
        city_graph = {
            0: {
                1: {'capacity': 5, 'travel_time': 5},
                2: {'capacity': 5, 'travel_time': 8}
            },
            1: {
                3: {'capacity': 5, 'travel_time': 5}
            },
            2: {
                3: {'capacity': 5, 'travel_time': 3}
            },
            3: {}
        }
        vehicles = [
            {'start_time': 0, 'origin': 0, 'destination': 3, 'size': 3},
            {'start_time': 1, 'origin': 0, 'destination': 3, 'size': 3},
            {'start_time': 2, 'origin': 0, 'destination': 3, 'size': 3},
            {'start_time': 3, 'origin': 0, 'destination': 3, 'size': 3},
            {'start_time': 4, 'origin': 0, 'destination': 3, 'size': 3}
        ]
        simulation_time = 100
        result = simulate_traffic(city_graph, vehicles, simulation_time)
        # Ensure that some vehicles have reached the destination and average travel time > 0.
        self.assertGreater(result.get("average_travel_time", 0), 0)

    def test_disconnected_graph(self):
        # The destination is unreachable so no vehicle should complete the route.
        city_graph = {
            0: {1: {'capacity': 10, 'travel_time': 5}},
            1: {},
            2: {}
        }
        vehicles = [
            {'start_time': 0, 'origin': 0, 'destination': 2, 'size': 2}
        ]
        simulation_time = 50
        result = simulate_traffic(city_graph, vehicles, simulation_time)
        # With unreachable destination, average travel time is 0.0.
        self.assertEqual(result.get("average_travel_time", None), 0.0)

if __name__ == "__main__":
    unittest.main()