import unittest
from emergency_routes import find_optimal_routes


class EmergencyRoutesTest(unittest.TestCase):
    def test_basic_case(self):
        city_graph = {
            0: {1: [(0, 3600, 10), (3601, 7200, 20)], 2: [(0, 86400, 15)]},
            1: {3: [(0, 86400, 5)]},
            2: {3: [(0, 86400, 10)]},
            3: {}
        }

        emergency_events = [(3, 3000)]
        service_providers = {"hospital": [0, 1], "fire_station": [2]}

        expected = {
            3: {
                "route": [1, 3],
                "arrival_time": 3005,
                "service_provider_type": "hospital",
                "service_provider_location": 1
            }
        }

        self.assertEqual(find_optimal_routes(
            city_graph, emergency_events, service_providers), expected)

    def test_time_dependent_routing(self):
        city_graph = {
            0: {1: [(0, 3600, 10), (3601, 86400, 20)]},
            1: {}
        }
        
        # Test before time change
        emergency_events = [(1, 3000)]
        service_providers = {"hospital": [0]}
        
        expected = {
            1: {
                "route": [0, 1],
                "arrival_time": 3010,
                "service_provider_type": "hospital",
                "service_provider_location": 0
            }
        }
        
        self.assertEqual(find_optimal_routes(
            city_graph, emergency_events, service_providers), expected)
        
        # Test after time change
        emergency_events = [(1, 4000)]
        expected = {
            1: {
                "route": [0, 1],
                "arrival_time": 4020,
                "service_provider_type": "hospital",
                "service_provider_location": 0
            }
        }
        
        self.assertEqual(find_optimal_routes(
            city_graph, emergency_events, service_providers), expected)

    def test_multiple_events(self):
        city_graph = {
            0: {1: [(0, 86400, 10)]},
            1: {2: [(0, 86400, 5)]},
            2: {3: [(0, 86400, 5)]},
            3: {}
        }
        
        emergency_events = [(1, 1000), (2, 1500), (3, 2000)]
        service_providers = {"hospital": [0]}
        
        expected = {
            1: {
                "route": [0, 1],
                "arrival_time": 1010,
                "service_provider_type": "hospital",
                "service_provider_location": 0
            },
            2: {
                "route": [0, 1, 2],
                "arrival_time": 1515,
                "service_provider_type": "hospital",
                "service_provider_location": 0
            },
            3: {
                "route": [0, 1, 2, 3],
                "arrival_time": 2020,
                "service_provider_type": "hospital",
                "service_provider_location": 0
            }
        }
        
        self.assertEqual(find_optimal_routes(
            city_graph, emergency_events, service_providers), expected)

    def test_multiple_service_providers(self):
        city_graph = {
            0: {3: [(0, 86400, 20)]},
            1: {3: [(0, 86400, 10)]},
            2: {3: [(0, 86400, 15)]},
            3: {}
        }
        
        emergency_events = [(3, 2000)]
        service_providers = {
            "hospital": [0],
            "fire_station": [1], 
            "police_station": [2]
        }
        
        expected = {
            3: {
                "route": [1, 3],
                "arrival_time": 2010,
                "service_provider_type": "fire_station",
                "service_provider_location": 1
            }
        }
        
        self.assertEqual(find_optimal_routes(
            city_graph, emergency_events, service_providers), expected)

    def test_same_distance_different_providers(self):
        city_graph = {
            0: {3: [(0, 86400, 10)]},
            1: {3: [(0, 86400, 10)]},
            2: {3: [(0, 86400, 10)]},
            3: {}
        }
        
        emergency_events = [(3, 2000)]
        service_providers = {
            "hospital": [0],
            "fire_station": [1],
            "police_station": [2]
        }
        
        expected = {
            3: {
                "route": [0, 3],
                "arrival_time": 2010,
                "service_provider_type": "hospital",
                "service_provider_location": 0
            }
        }
        
        self.assertEqual(find_optimal_routes(
            city_graph, emergency_events, service_providers), expected)

    def test_same_type_different_providers(self):
        city_graph = {
            0: {3: [(0, 86400, 15)]},
            1: {3: [(0, 86400, 15)]},
            2: {3: [(0, 86400, 10)]},
            3: {}
        }
        
        emergency_events = [(3, 2000)]
        service_providers = {"hospital": [0, 1, 2]}
        
        expected = {
            3: {
                "route": [2, 3],
                "arrival_time": 2010,
                "service_provider_type": "hospital",
                "service_provider_location": 2
            }
        }
        
        self.assertEqual(find_optimal_routes(
            city_graph, emergency_events, service_providers), expected)

    def test_unreachable_event(self):
        city_graph = {
            0: {1: [(0, 86400, 10)]},
            1: {},
            2: {}
        }
        
        emergency_events = [(2, 2000)]
        service_providers = {"hospital": [0]}
        
        expected = {2: None}
        
        self.assertEqual(find_optimal_routes(
            city_graph, emergency_events, service_providers), expected)

    def test_large_graph(self):
        # Create a larger graph for performance testing
        city_graph = {}
        
        # Create a line graph with 1000 nodes
        for i in range(999):
            city_graph[i] = {i+1: [(0, 86400, 1)]}
        
        city_graph[999] = {}
        
        emergency_events = [(999, 1000)]
        service_providers = {"hospital": [0]}
        
        expected = {
            999: {
                "route": list(range(1000)),  # 0 to 999
                "arrival_time": 1999,
                "service_provider_type": "hospital",
                "service_provider_location": 0
            }
        }
        
        self.assertEqual(find_optimal_routes(
            city_graph, emergency_events, service_providers), expected)

    def test_complex_time_dependent_case(self):
        city_graph = {
            0: {
                1: [(0, 3600, 10), (3601, 7200, 20), (7201, 86400, 5)],
                2: [(0, 3600, 15), (3601, 86400, 10)]
            },
            1: {3: [(0, 86400, 5)]},
            2: {3: [(0, 3600, 20), (3601, 86400, 5)]},
            3: {}
        }
        
        # First event during first time period
        emergency_events = [(3, 2000)]
        service_providers = {"hospital": [0]}
        
        expected = {
            3: {
                "route": [0, 1, 3],
                "arrival_time": 2015,
                "service_provider_type": "hospital",
                "service_provider_location": 0
            }
        }
        
        self.assertEqual(find_optimal_routes(
            city_graph, emergency_events, service_providers), expected)
        
        # Second event during second time period
        emergency_events = [(3, 4000)]
        
        expected = {
            3: {
                "route": [0, 2, 3],
                "arrival_time": 4015,
                "service_provider_type": "hospital",
                "service_provider_location": 0
            }
        }
        
        self.assertEqual(find_optimal_routes(
            city_graph, emergency_events, service_providers), expected)
        
        # Third event during third time period
        emergency_events = [(3, 8000)]
        
        expected = {
            3: {
                "route": [0, 1, 3],
                "arrival_time": 8010,
                "service_provider_type": "hospital",
                "service_provider_location": 0
            }
        }
        
        self.assertEqual(find_optimal_routes(
            city_graph, emergency_events, service_providers), expected)

    def test_tie_breaks_by_location_id(self):
        city_graph = {
            0: {3: [(0, 86400, 10)]},
            1: {3: [(0, 86400, 10)]},
            2: {3: [(0, 86400, 10)]},
            3: {}
        }
        
        emergency_events = [(3, 2000)]
        service_providers = {"hospital": [1, 2, 0]}  # Intentionally not sorted
        
        expected = {
            3: {
                "route": [0, 3],
                "arrival_time": 2010,
                "service_provider_type": "hospital",
                "service_provider_location": 0
            }
        }
        
        self.assertEqual(find_optimal_routes(
            city_graph, emergency_events, service_providers), expected)

    def test_same_distance_different_service_types(self):
        city_graph = {
            0: {3: [(0, 86400, 10)]},  # hospital
            1: {3: [(0, 86400, 10)]},  # fire station
            2: {3: [(0, 86400, 10)]},  # police station
            3: {}
        }
        
        emergency_events = [(3, 2000)]
        service_providers = {
            "fire_station": [1],
            "police_station": [2],
            "hospital": [0]
        }
        
        expected = {
            3: {
                "route": [0, 3],
                "arrival_time": 2010,
                "service_provider_type": "hospital",
                "service_provider_location": 0
            }
        }
        
        self.assertEqual(find_optimal_routes(
            city_graph, emergency_events, service_providers), expected)

        # Change the priority by removing hospital
        service_providers = {
            "fire_station": [1],
            "police_station": [2]
        }
        
        expected = {
            3: {
                "route": [1, 3],
                "arrival_time": 2010,
                "service_provider_type": "fire_station",
                "service_provider_location": 1
            }
        }
        
        self.assertEqual(find_optimal_routes(
            city_graph, emergency_events, service_providers), expected)


if __name__ == "__main__":
    unittest.main()