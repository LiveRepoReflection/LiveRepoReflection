import unittest
from smart_ride.smart_ride import SmartRideOptimizer

class TestSmartRideOptimizer(unittest.TestCase):
    def setUp(self):
        # Sample city graph
        self.graph = {
            1: [(2, 5), (3, 10)],
            2: [(1, 5), (3, 3), (4, 9)],
            3: [(1, 10), (2, 3), (4, 6), (5, 8)],
            4: [(2, 9), (3, 6), (5, 7)],
            5: [(3, 8), (4, 7)]
        }
        self.optimizer = SmartRideOptimizer(self.graph)

    def test_single_route(self):
        request = {
            "start_intersection": 1,
            "end_intersection": 5,
            "departure_time": 10,
            "k": 1
        }
        result = self.optimizer.find_best_routes(request)
        self.assertEqual(len(result), 1)
        self.assertTrue(all(key in result[0] for key in ['route', 'cost']))

    def test_multiple_routes(self):
        request = {
            "start_intersection": 1,
            "end_intersection": 5,
            "departure_time": 15,
            "k": 3
        }
        result = self.optimizer.find_best_routes(request)
        self.assertEqual(len(result), 3)
        self.assertTrue(all(isinstance(route['cost'], int) for route in result))
        self.assertTrue(all(len(route['route']) >= 2 for route in result))

    def test_invalid_start_node(self):
        request = {
            "start_intersection": 99,
            "end_intersection": 5,
            "departure_time": 10,
            "k": 1
        }
        with self.assertRaises(ValueError):
            self.optimizer.find_best_routes(request)

    def test_invalid_end_node(self):
        request = {
            "start_intersection": 1,
            "end_intersection": 99,
            "departure_time": 10,
            "k": 1
        }
        with self.assertRaises(ValueError):
            self.optimizer.find_best_routes(request)

    def test_same_start_end(self):
        request = {
            "start_intersection": 1,
            "end_intersection": 1,
            "departure_time": 10,
            "k": 1
        }
        result = self.optimizer.find_best_routes(request)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['route'], [1])
        self.assertEqual(result[0]['cost'], 0)

    def test_limited_routes_available(self):
        request = {
            "start_intersection": 1,
            "end_intersection": 5,
            "departure_time": 20,
            "k": 10
        }
        result = self.optimizer.find_best_routes(request)
        self.assertTrue(1 <= len(result) <= 10)

    def test_route_ordering(self):
        request = {
            "start_intersection": 1,
            "end_intersection": 5,
            "departure_time": 12,
            "k": 3
        }
        result = self.optimizer.find_best_routes(request)
        costs = [route['cost'] for route in result]
        self.assertEqual(costs, sorted(costs))

    def test_traffic_cost_caching(self):
        request1 = {
            "start_intersection": 1,
            "end_intersection": 5,
            "departure_time": 10,
            "k": 1
        }
        request2 = {
            "start_intersection": 1,
            "end_intersection": 5,
            "departure_time": 10,
            "k": 1
        }
        # Should use cached traffic costs for same timestamp
        self.optimizer.find_best_routes(request1)
        self.optimizer.find_best_routes(request2)

if __name__ == '__main__':
    unittest.main()