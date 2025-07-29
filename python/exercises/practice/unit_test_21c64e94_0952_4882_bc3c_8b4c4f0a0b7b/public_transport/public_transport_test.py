import unittest
from public_transport import find_minimum_costs

class PublicTransportTest(unittest.TestCase):
    def test_sample_case(self):
        N = 5
        M = 6
        routes = [
            (0, 1, 10, 5, 500),
            (0, 2, 15, 8, 300),
            (1, 2, 5, 3, 400),
            (1, 3, 20, 10, 600),
            (2, 4, 25, 12, 200),
            (3, 4, 10, 7, 700)
        ]
        K = 2
        station_pairs = [
            (0, 4, 150),
            (1, 3, 700)
        ]
        max_travel_time = 60
        max_transfers = 2
        expected = [20, -1]
        result = find_minimum_costs(N, M, routes, K, station_pairs, max_travel_time, max_transfers)
        self.assertEqual(result, expected)

    def test_time_constraint(self):
        N = 4
        M = 3
        routes = [
            (0, 1, 50, 5, 1000),
            (1, 2, 50, 5, 1000),
            (2, 3, 50, 5, 1000)
        ]
        K = 1
        station_pairs = [(0, 3, 50)]
        max_travel_time = 100
        max_transfers = 2
        expected = [-1]
        result = find_minimum_costs(N, M, routes, K, station_pairs, max_travel_time, max_transfers)
        self.assertEqual(result, expected)

    def test_capacity_constraint(self):
        N = 4
        M = 3
        routes = [
            (0, 1, 10, 5, 100),
            (1, 2, 10, 5, 100),
            (2, 3, 10, 5, 100)
        ]
        K = 1
        station_pairs = [(0, 3, 150)]
        max_travel_time = 40
        max_transfers = 3
        expected = [-1]
        result = find_minimum_costs(N, M, routes, K, station_pairs, max_travel_time, max_transfers)
        self.assertEqual(result, expected)

    def test_transfer_constraint(self):
        N = 5
        M = 4
        routes = [
            (0, 1, 10, 3, 500),
            (1, 2, 10, 3, 500),
            (2, 3, 10, 3, 500),
            (3, 4, 10, 3, 500)
        ]
        K = 1
        station_pairs = [(0, 4, 100)]
        max_travel_time = 50
        max_transfers = 2
        expected = [-1]
        result = find_minimum_costs(N, M, routes, K, station_pairs, max_travel_time, max_transfers)
        self.assertEqual(result, expected)

    def test_multiple_paths(self):
        N = 6
        M = 7
        routes = [
            (0, 1, 10, 5, 500),
            (1, 2, 10, 5, 500),
            (0, 3, 15, 7, 500),
            (3, 2, 15, 6, 500),
            (2, 4, 10, 4, 500),
            (1, 4, 50, 2, 500),
            (4, 5, 5, 3, 500)
        ]
        K = 1
        station_pairs = [(0, 5, 100)]
        max_travel_time = 60
        max_transfers = 3
        expected = [17]
        result = find_minimum_costs(N, M, routes, K, station_pairs, max_travel_time, max_transfers)
        self.assertEqual(result, expected)

    def test_edge_case_same_station(self):
        N = 3
        M = 2
        routes = [
            (0, 1, 10, 5, 500),
            (1, 2, 10, 5, 500)
        ]
        K = 1
        station_pairs = [(1, 1, 100)]
        max_travel_time = 30
        max_transfers = 1
        expected = [0]
        result = find_minimum_costs(N, M, routes, K, station_pairs, max_travel_time, max_transfers)
        self.assertEqual(result, expected)

if __name__ == '__main__':
    unittest.main()