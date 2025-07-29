import unittest
from atms_routing import find_fastest_route

class TestATMSRouting(unittest.TestCase):
    def setUp(self):
        # Simple graph with 3 intersections
        self.simple_graph = {
            1: {
                'neighbors': {
                    2: {
                        'length': 1000,
                        'speed_limit': 60,
                        'capacity': 100,
                        'current_traffic': 10,
                        'delay_function': lambda x: -0.1 * x
                    }
                }
            },
            2: {
                'neighbors': {
                    3: {
                        'length': 2000,
                        'speed_limit': 40,
                        'capacity': 50,
                        'current_traffic': 5,
                        'delay_function': lambda x: 0.5 * x
                    }
                }
            },
            3: {'neighbors': {}}
        }

        # Graph with multiple paths
        self.complex_graph = {
            1: {
                'neighbors': {
                    2: {
                        'length': 1000,
                        'speed_limit': 60,
                        'capacity': 100,
                        'current_traffic': 20,
                        'delay_function': lambda x: 0.2 * x
                    },
                    3: {
                        'length': 1500,
                        'speed_limit': 80,
                        'capacity': 120,
                        'current_traffic': 15,
                        'delay_function': lambda x: 0.1 * x
                    }
                }
            },
            2: {
                'neighbors': {
                    4: {
                        'length': 2000,
                        'speed_limit': 40,
                        'capacity': 80,
                        'current_traffic': 30,
                        'delay_function': lambda x: 0.3 * x
                    }
                }
            },
            3: {
                'neighbors': {
                    4: {
                        'length': 1000,
                        'speed_limit': 60,
                        'capacity': 100,
                        'current_traffic': 10,
                        'delay_function': lambda x: 0.1 * x
                    }
                }
            },
            4: {'neighbors': {}}
        }

        # Disconnected graph
        self.disconnected_graph = {
            1: {
                'neighbors': {
                    2: {
                        'length': 1000,
                        'speed_limit': 60,
                        'capacity': 100,
                        'current_traffic': 10,
                        'delay_function': lambda x: 0.1 * x
                    }
                }
            },
            2: {'neighbors': {}},
            3: {'neighbors': {}}
        }

    def test_simple_route(self):
        result = find_fastest_route(self.simple_graph, 1, 3, 0)
        self.assertEqual(result, [1, 2, 3])

    def test_multiple_paths(self):
        result = find_fastest_route(self.complex_graph, 1, 4, 0)
        self.assertEqual(result, [1, 3, 4])

    def test_no_route_exists(self):
        result = find_fastest_route(self.disconnected_graph, 1, 3, 0)
        self.assertEqual(result, [])

    def test_same_start_and_end(self):
        result = find_fastest_route(self.simple_graph, 1, 1, 0)
        self.assertEqual(result, [1])

    def test_negative_delay(self):
        # Test that negative delays are handled correctly
        graph = {
            1: {
                'neighbors': {
                    2: {
                        'length': 1000,
                        'speed_limit': 60,
                        'capacity': 100,
                        'current_traffic': 10,
                        'delay_function': lambda x: -1 * x
                    }
                }
            },
            2: {'neighbors': {}}
        }
        result = find_fastest_route(graph, 1, 2, 0)
        self.assertEqual(result, [1, 2])

    def test_large_traffic_impact(self):
        # Test when traffic significantly impacts travel time
        graph = {
            1: {
                'neighbors': {
                    2: {
                        'length': 1000,
                        'speed_limit': 60,
                        'capacity': 100,
                        'current_traffic': 90,
                        'delay_function': lambda x: 1 * x
                    }
                }
            },
            2: {'neighbors': {}}
        }
        result = find_fastest_route(graph, 1, 2, 0)
        self.assertEqual(result, [1, 2])

    def test_empty_graph(self):
        result = find_fastest_route({}, 1, 2, 0)
        self.assertEqual(result, [])

    def test_nonexistent_nodes(self):
        result = find_fastest_route(self.simple_graph, 99, 100, 0)
        self.assertEqual(result, [])

if __name__ == '__main__':
    unittest.main()