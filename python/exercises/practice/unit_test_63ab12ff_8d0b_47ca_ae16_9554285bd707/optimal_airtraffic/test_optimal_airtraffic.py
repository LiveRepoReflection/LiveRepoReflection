import unittest
from optimal_airtraffic import OptimalAirTraffic

class TestOptimalAirTraffic(unittest.TestCase):
    def setUp(self):
        self.airports = [1, 2, 3, 4, 5]
        self.routes = [
            (1, 2, 10),
            (2, 3, 15),
            (3, 4, 10),
            (4, 5, 5),
            (1, 3, 30),
            (1, 5, 50)
        ]
        self.system = OptimalAirTraffic(self.airports, self.routes)

    def test_initial_graph_construction(self):
        self.assertEqual(self.system.get_route_cost(1, 2), 10)
        self.assertEqual(self.system.get_route_cost(3, 4), 10)
        self.assertIsNone(self.system.get_route_cost(5, 1))

    def test_basic_path_finding(self):
        path = self.system.find_optimal_path(1, 5)
        self.assertEqual(path, [1, 2, 3, 4, 5])
        self.assertEqual(self.system.calculate_path_cost(path), 40)

    def test_weather_updates(self):
        self.system.apply_weather_update((2, 3, 5))  # Cheaper route
        path = self.system.find_optimal_path(1, 5)
        self.assertEqual(path, [1, 2, 3, 4, 5])
        self.assertEqual(self.system.calculate_path_cost(path), 30)

    def test_restrictions(self):
        self.system.apply_restriction((3, 4, 0, 100))  # Permanent restriction
        path = self.system.find_optimal_path(1, 5)
        self.assertEqual(path, [1, 5])
        self.assertEqual(self.system.calculate_path_cost(path), 50)

    def test_no_path_scenario(self):
        self.system.apply_restriction((1, 2, 0, 100))
        self.system.apply_restriction((1, 3, 0, 100))
        self.system.apply_restriction((1, 5, 0, 100))
        path = self.system.find_optimal_path(1, 5)
        self.assertEqual(path, "No path found")

    def test_concurrent_operations(self):
        import threading
        
        def update_weather():
            for _ in range(100):
                self.system.apply_weather_update((2, 3, 5))
        
        def find_paths():
            for _ in range(100):
                path = self.system.find_optimal_path(1, 5)
                self.assertTrue(path == [1, 2, 3, 4, 5] or path == [1, 5])
        
        threads = [
            threading.Thread(target=update_weather),
            threading.Thread(target=find_paths)
        ]
        
        for t in threads:
            t.start()
        for t in threads:
            t.join()

if __name__ == '__main__':
    unittest.main()