import unittest
from emergency_routing import optimal_routing

class TestEmergencyRouting(unittest.TestCase):
    def test_basic_case(self):
        graph = {
            1: {2: 10, 3: 15},
            2: {1: 10, 4: 20},
            3: {1: 15, 4: 5},
            4: {2: 20, 3: 5}
        }
        fire_stations = {1: 2, 2: 1}
        emergencies = [3, 4, 3]
        result = optimal_routing(graph, fire_stations, emergencies)
        expected = {3: 1, 4: 2, 3: 1}
        self.assertEqual(result, expected)

    def test_insufficient_trucks(self):
        graph = {
            1: {2: 5},
            2: {1: 5, 3: 10},
            3: {2: 10}
        }
        fire_stations = {1: 1}
        emergencies = [2, 3]
        result = optimal_routing(graph, fire_stations, emergencies)
        self.assertIsNone(result)

    def test_disconnected_graph(self):
        graph = {
            1: {2: 10},
            2: {1: 10},
            3: {4: 15},
            4: {3: 15}
        }
        fire_stations = {1: 1, 3: 1}
        emergencies = [2, 4]
        result = optimal_routing(graph, fire_stations, emergencies)
        expected = {2: 1, 4: 3}
        self.assertEqual(result, expected)

    def test_multiple_emergencies_same_location(self):
        graph = {
            1: {2: 5},
            2: {1: 5, 3: 10},
            3: {2: 10}
        }
        fire_stations = {1: 3}
        emergencies = [2, 2, 2]
        result = optimal_routing(graph, fire_stations, emergencies)
        expected = {2: 1, 2: 1, 2: 1}
        self.assertEqual(result, expected)

    def test_complex_case_with_multiple_stations(self):
        graph = {
            1: {2: 5, 5: 20},
            2: {1: 5, 3: 10, 6: 15},
            3: {2: 10, 4: 5},
            4: {3: 5, 7: 10},
            5: {1: 20, 6: 10},
            6: {2: 15, 5: 10, 7: 5},
            7: {4: 10, 6: 5}
        }
        fire_stations = {1: 2, 4: 1, 5: 1}
        emergencies = [3, 6, 7, 2]
        result = optimal_routing(graph, fire_stations, emergencies)
        self.assertEqual(len(result), 4)
        self.assertEqual(len(set(result.values())), 3)

    def test_large_graph_performance(self):
        graph = {i: {i+1: 1} for i in range(1, 1000)}
        graph[1000] = {}
        fire_stations = {1: 10, 500: 5}
        emergencies = [i for i in range(100, 200, 10)]
        result = optimal_routing(graph, fire_stations, emergencies)
        self.assertEqual(len(result), len(emergencies))

    def test_zero_travel_time(self):
        graph = {
            1: {2: 0},
            2: {1: 0, 3: 10},
            3: {2: 10}
        }
        fire_stations = {1: 2}
        emergencies = [2, 3]
        result = optimal_routing(graph, fire_stations, emergencies)
        expected = {2: 1, 3: 1}
        self.assertEqual(result, expected)

    def test_station_at_emergency_location(self):
        graph = {
            1: {2: 10},
            2: {1: 10, 3: 5},
            3: {2: 5}
        }
        fire_stations = {1: 1, 3: 1}
        emergencies = [3, 2]
        result = optimal_routing(graph, fire_stations, emergencies)
        expected = {3: 3, 2: 1}
        self.assertEqual(result, expected)

if __name__ == '__main__':
    unittest.main()