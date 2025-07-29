import unittest
from cdn_placement import cdn_placement

class CDNPlacementTest(unittest.TestCase):
    def test_basic_scenario(self):
        # Example scenario from the prompt description
        cities = 5
        connections = [(0, 1, 10), (0, 2, 15), (1, 2, 5), (1, 3, 12), (2, 4, 20), (3, 4, 8)]
        demand = [20, 30, 25, 15, 10]
        cdn_capacity = 50
        cdn_cost = 100
        latency_tolerance = 20
        candidate_sites = [0, 1, 2, 3, 4]
        # Total demand = 100, so need at least 2 servers.
        expected = 200
        result = cdn_placement(cities, connections, demand, cdn_capacity, cdn_cost, latency_tolerance, candidate_sites)
        self.assertEqual(result, expected)

    def test_unreachable_city(self):
        # City 2 is disconnected from any candidate site (city 0 and city 1)
        cities = 3
        connections = [(0, 1, 5)]
        demand = [10, 10, 10]
        cdn_capacity = 50
        cdn_cost = 100
        latency_tolerance = 5
        candidate_sites = [0, 1]
        expected = -1
        result = cdn_placement(cities, connections, demand, cdn_capacity, cdn_cost, latency_tolerance, candidate_sites)
        self.assertEqual(result, expected)

    def test_alternative_placement(self):
        # A configuration where the optimal placement is non-trivial due to latency constraints.
        cities = 4
        connections = [(0, 1, 5), (1, 2, 6), (2, 3, 5), (0, 3, 20)]
        demand = [5, 5, 5, 5]  # Total demand = 20; cdn_capacity = 10 -> need 2 servers.
        cdn_capacity = 10
        cdn_cost = 50
        latency_tolerance = 10
        candidate_sites = [0, 2, 3]
        expected = 100
        result = cdn_placement(cities, connections, demand, cdn_capacity, cdn_cost, latency_tolerance, candidate_sites)
        self.assertEqual(result, expected)

    def test_single_server_suffices(self):
        # Total capacity of a single server exceeds total demand.
        cities = 3
        connections = [(0, 1, 4), (1, 2, 4), (0, 2, 8)]
        demand = [10, 10, 10]  # Total demand = 30
        cdn_capacity = 40
        cdn_cost = 20
        latency_tolerance = 10
        candidate_sites = [1]
        expected = 20
        result = cdn_placement(cities, connections, demand, cdn_capacity, cdn_cost, latency_tolerance, candidate_sites)
        self.assertEqual(result, expected)

    def test_insufficient_global_capacity(self):
        # Even placing a server at all candidate sites cannot meet the total demand.
        cities = 3
        connections = [(0, 1, 5), (1, 2, 5), (0, 2, 10)]
        demand = [30, 30, 30]  # Total demand = 90
        cdn_capacity = 50
        cdn_cost = 100
        latency_tolerance = 10
        # Only one candidate site means maximum capacity is 50, which is insufficient.
        candidate_sites = [0]
        expected = -1
        result = cdn_placement(cities, connections, demand, cdn_capacity, cdn_cost, latency_tolerance, candidate_sites)
        self.assertEqual(result, expected)

    def test_limited_candidate_sites(self):
        # Testing scenario where only a subset of cities can host servers.
        cities = 4
        connections = [(0, 1, 5), (1, 2, 5), (2, 3, 5), (0, 3, 10)]
        demand = [10, 20, 10, 20]  # Total demand = 60, so need 2 servers given capacity 30
        cdn_capacity = 30
        cdn_cost = 40
        latency_tolerance = 10
        candidate_sites = [1, 2]
        expected = 80
        result = cdn_placement(cities, connections, demand, cdn_capacity, cdn_cost, latency_tolerance, candidate_sites)
        self.assertEqual(result, expected)

if __name__ == '__main__':
    unittest.main()