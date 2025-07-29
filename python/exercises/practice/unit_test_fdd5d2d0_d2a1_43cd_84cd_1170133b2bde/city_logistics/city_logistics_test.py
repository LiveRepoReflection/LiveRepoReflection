import unittest
from city_logistics import LogisticsNetwork

class TestCityLogistics(unittest.TestCase):
    def setUp(self):
        # Create a new network instance for each test
        self.network = LogisticsNetwork()
        
        # Initialize a basic network graph used in multiple tests
        # For simplicity, we use integers for city IDs
        # Graph structure used in tests:
        # 1 -> 2, 1 -> 3, 2 -> 4, 3 -> 4, 1 -> 4
        # We simulate edges using:
        # self.network.add_edge(source, destination, time, cost)
        self.network.add_edge(1, 2, time=1, cost=3)
        self.network.add_edge(2, 4, time=3, cost=3)
        self.network.add_edge(1, 3, time=2, cost=2)
        self.network.add_edge(3, 4, time=2, cost=2)
        self.network.add_edge(1, 4, time=6, cost=0)

    def test_optimal_route_found(self):
        # Create a simple network with two possible routes from A to C.
        # Setup a network with cities: A=10, B=20, C=30.
        network = LogisticsNetwork()
        network.add_edge(10, 20, time=2, cost=5)  # Route: 10 -> 20
        network.add_edge(20, 30, time=2, cost=5)  # Route: 20 -> 30
        network.add_edge(10, 30, time=5, cost=8)  # Direct route: 10 -> 30
        
        # Delivery request: source=10, destination=30, package_size=10, deadline=6
        # Calculation for 10 -> 20->30:
        #   Edge 10->20: total_cost = 5 + (10*2) = 25
        #   Edge 20->30: total_cost = 5 + (10*2) = 25
        #   Total = 50, and total time = 2+2=4 < deadline 6
        # Direct route 10->30: cost = 8 + (10*5) = 58, time = 5 < deadline 6
        path, total_cost = network.process_request(10, 30, package_size=10, deadline=6)
        self.assertEqual(path, [10, 20, 30])
        self.assertEqual(total_cost, 50)

    def test_deadline_exceeded(self):
        # Use the same network from test_optimal_route_found.
        network = LogisticsNetwork()
        network.add_edge(10, 20, time=2, cost=5)
        network.add_edge(20, 30, time=2, cost=5)
        network.add_edge(10, 30, time=5, cost=8)
        # Set a deadline that cannot be met.
        result = network.process_request(10, 30, package_size=10, deadline=3)
        self.assertIsNone(result)

    def test_real_time_update(self):
        # Setup initial network with two routes.
        network = LogisticsNetwork()
        network.add_edge(10, 20, time=2, cost=5)
        network.add_edge(20, 30, time=2, cost=5)
        network.add_edge(10, 30, time=5, cost=8)
        
        # Initially, the optimal route should be 10->20->30 (total time 4, cost 50)
        path, total_cost = network.process_request(10, 30, package_size=10, deadline=6)
        self.assertEqual(path, [10, 20, 30])
        self.assertEqual(total_cost, 50)
        
        # Now, update the direct edge 10->30 to simulate a real-time improvement.
        # New edge 10->30: time=3, cost=7.
        network.update_edge(10, 30, time=3, cost=7)
        # Now, recalculate:
        # Direct route: cost = 7 + (10*3) = 37, time = 3, deadline 6 met.
        path, total_cost = network.process_request(10, 30, package_size=10, deadline=6)
        self.assertEqual(path, [10, 30])
        self.assertEqual(total_cost, 37)

    def test_multiple_routes_selection(self):
        # Using the default graph from setUp:
        # Routes:
        # 1->2->4: time = 1+3 = 4, cost = (3+5*1) + (3+5*3) = (8) + (18) = 26, when package_size=5.
        # 1->3->4: time = 2+2 = 4, cost = (2+5*2) + (2+5*2) = (12) + (12) = 24.
        # Direct: 1->4: time = 6, cost = 0+5*6 = 30.
        path, total_cost = self.network.process_request(1, 4, package_size=5, deadline=6)
        self.assertEqual(path, [1, 3, 4])
        self.assertEqual(total_cost, 24)

    def test_multiple_concurrent_requests(self):
        # Simulate multiple sequential requests on the same network instance.
        # Using the default self.network graph from setUp.
        requests = [
            (1, 4, 5, 6),  # Expected optimal: [1, 3, 4], cost 24.
            (1, 4, 2, 6),  # Recalculate costs with package_size=2.
            (1, 4, 10, 7)  # Larger package size.
        ]
        expected_results = []
        # Calculations for each request:
        # For package_size=5 (calculated above): cost = 24, route [1,3,4]
        expected_results.append(([1, 3, 4], 24))
        # For package_size=2:
        # 1->2->4: (3+2*1) + (3+2*3) = (5) + (9) = 14, time =4
        # 1->3->4: (2+2*2)+(2+2*2)= (6)+(6)=12, time =4
        # Direct: 1->4: (0+2*6)=12, time=6 -> tie, choose the one with lower cost? In tie multiple valid,
        # assuming the algorithm picks [1,3,4] consistently.
        expected_results.append(([1, 3, 4], 12))
        # For package_size=10:
        # 1->2->4: (3+10*1) + (3+10*3) = (13)+(33)=46, time=4
        # 1->3->4: (2+10*2)+(2+10*2)= (22)+(22)=44, time=4
        # Direct: 1->4: (0+10*6)=60, time=6
        expected_results.append(([1, 3, 4], 44))
        
        for (src, dst, pkg_size, deadline), expected in zip(requests, expected_results):
            result = self.network.process_request(src, dst, package_size=pkg_size, deadline=deadline)
            self.assertIsNotNone(result)
            path, total_cost = result
            self.assertEqual(path, expected[0])
            self.assertEqual(total_cost, expected[1])

if __name__ == '__main__':
    unittest.main()