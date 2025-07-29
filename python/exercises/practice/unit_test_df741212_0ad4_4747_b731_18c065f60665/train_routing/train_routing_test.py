import unittest
from train_routing import min_train_trips

class TrainRoutingTest(unittest.TestCase):
    def test_basic_example(self):
        num_cities = 5
        edges = [(0, 1, 10), (0, 2, 15), (1, 2, 5), (1, 3, 12), (2, 4, 20), (3, 4, 8)]
        train_capacity = 15
        passenger_requests = [(0, 4, 10), (1, 4, 20), (0, 3, 5)]
        self.assertEqual(min_train_trips(num_cities, edges, train_capacity, passenger_requests), 4)

    def test_single_request(self):
        num_cities = 3
        edges = [(0, 1, 5), (1, 2, 5)]
        train_capacity = 10
        passenger_requests = [(0, 2, 7)]
        self.assertEqual(min_train_trips(num_cities, edges, train_capacity, passenger_requests), 1)

    def test_exact_capacity(self):
        num_cities = 4
        edges = [(0, 1, 10), (1, 2, 10), (2, 3, 10)]
        train_capacity = 20
        passenger_requests = [(0, 3, 20)]
        self.assertEqual(min_train_trips(num_cities, edges, train_capacity, passenger_requests), 1)

    def test_multiple_trips_needed(self):
        num_cities = 3
        edges = [(0, 1, 5), (1, 2, 5)]
        train_capacity = 10
        passenger_requests = [(0, 2, 25)]
        self.assertEqual(min_train_trips(num_cities, edges, train_capacity, passenger_requests), 3)

    def test_disconnected_graph(self):
        num_cities = 5
        edges = [(0, 1, 5), (2, 3, 5), (3, 4, 5)]  # No path from 0 to 4
        train_capacity = 15
        passenger_requests = [(0, 4, 10)]
        self.assertEqual(min_train_trips(num_cities, edges, train_capacity, passenger_requests), -1)

    def test_multiple_routes(self):
        num_cities = 4
        edges = [(0, 1, 10), (0, 2, 5), (1, 3, 10), (2, 3, 5)]  # Two routes from 0 to 3
        train_capacity = 10
        passenger_requests = [(0, 3, 15)]  # Should choose the shortest path: 0->2->3
        self.assertEqual(min_train_trips(num_cities, edges, train_capacity, passenger_requests), 2)

    def test_large_capacity_single_trip(self):
        num_cities = 4
        edges = [(0, 1, 5), (1, 2, 5), (2, 3, 5)]
        train_capacity = 100
        passenger_requests = [(0, 3, 95)]
        self.assertEqual(min_train_trips(num_cities, edges, train_capacity, passenger_requests), 1)

    def test_multiple_requests_same_route(self):
        num_cities = 3
        edges = [(0, 1, 5), (1, 2, 5)]
        train_capacity = 10
        passenger_requests = [(0, 2, 8), (0, 2, 7), (0, 2, 9)]
        self.assertEqual(min_train_trips(num_cities, edges, train_capacity, passenger_requests), 3)

    def test_complex_network(self):
        num_cities = 7
        edges = [(0, 1, 5), (0, 2, 10), (1, 3, 5), (2, 3, 5), 
                (2, 4, 8), (3, 5, 12), (4, 5, 6), (4, 6, 7), (5, 6, 10)]
        train_capacity = 12
        passenger_requests = [(0, 6, 30), (1, 5, 15), (2, 6, 10)]
        self.assertEqual(min_train_trips(num_cities, edges, train_capacity, passenger_requests), 6)

    def test_edge_case_one_city(self):
        num_cities = 1
        edges = []
        train_capacity = 10
        passenger_requests = []
        self.assertEqual(min_train_trips(num_cities, edges, train_capacity, passenger_requests), 0)

    def test_edge_case_same_city(self):
        num_cities = 3
        edges = [(0, 1, 5), (1, 2, 5)]
        train_capacity = 10
        passenger_requests = [(1, 1, 5)]  # Same source and destination
        self.assertEqual(min_train_trips(num_cities, edges, train_capacity, passenger_requests), 1)

    def test_large_network(self):
        # Create a larger network to test efficiency
        num_cities = 20
        edges = [(i, i+1, 5) for i in range(19)]  # Line graph
        edges += [(0, 10, 30), (5, 15, 25)]  # Add some shortcuts
        train_capacity = 15
        passenger_requests = [(0, 19, 50), (5, 18, 30), (10, 19, 20)]
        self.assertEqual(min_train_trips(num_cities, edges, train_capacity, passenger_requests), 8)

    def test_zero_passengers(self):
        num_cities = 3
        edges = [(0, 1, 5), (1, 2, 5)]
        train_capacity = 10
        passenger_requests = [(0, 2, 0)]
        # Even though there are 0 passengers, we still need to send a train
        self.assertEqual(min_train_trips(num_cities, edges, train_capacity, passenger_requests), 0)

if __name__ == "__main__":
    unittest.main()