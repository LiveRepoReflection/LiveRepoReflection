import unittest
from network_design.network_design import optimal_network_deployment

class TestOptimalNetworkDeployment(unittest.TestCase):
    def test_single_building(self):
        # Only one building, no edges
        n = 1
        edges = []
        building_data = [(10, 100)]  # (processing_requirement, installation_cost)
        max_latency = 50
        total_budget = 1000
        # Only possibility is to install a server in that building.
        expected = 1
        result = optimal_network_deployment(n, edges, building_data, max_latency, total_budget)
        self.assertEqual(result, expected)

    def test_two_buildings_single_server(self):
        # Two buildings connected by an edge; one server suffices if latency and bandwidth are met.
        n = 2
        edges = [(0, 1, 20, 20)]
        building_data = [(10, 150), (8, 130)]
        max_latency = 30
        total_budget = 500
        # A server in either building will cover the other since latency=20 and bandwidth requirement (10 or 8) <= 20.
        expected = 1
        result = optimal_network_deployment(n, edges, building_data, max_latency, total_budget)
        self.assertEqual(result, expected)

    def test_three_buildings_chain_low_latency(self):
        # Three buildings in a line, but max_latency is so strict that each building must have its own server.
        n = 3
        edges = [(0, 1, 30, 50), (1, 2, 30, 50)]
        building_data = [(5, 100), (6, 100), (7, 100)]
        max_latency = 20  # 30 > max_latency, so no building can rely on a neighbor's server.
        total_budget = 500
        expected = 3
        result = optimal_network_deployment(n, edges, building_data, max_latency, total_budget)
        self.assertEqual(result, expected)

    def test_bandwidth_constraint_requires_two_servers(self):
        # Two buildings connected by an edge.
        # The bandwidth limit is set too low to allow one server to cover both.
        n = 2
        edges = [(0, 1, 10, 29)]
        building_data = [(30, 100), (30, 100)]
        max_latency = 20
        total_budget = 500
        # Single server would force the non-server side to send 30 units through the edge,
        # which exceeds the bandwidth limit of 29. Therefore both buildings need a server.
        expected = 2
        result = optimal_network_deployment(n, edges, building_data, max_latency, total_budget)
        self.assertEqual(result, expected)

    def test_budget_constraint_impossible(self):
        # Two buildings where every server installation is too expensive relative to the budget.
        n = 2
        edges = [(0, 1, 10, 50)]
        building_data = [(10, 500), (10, 500)]
        max_latency = 50
        total_budget = 400  # Not enough to install even one server.
        expected = -1
        result = optimal_network_deployment(n, edges, building_data, max_latency, total_budget)
        self.assertEqual(result, expected)

    def test_square_network_one_server_possible(self):
        # Four buildings in a square configuration with extra cross links.
        n = 4
        edges = [
            (0, 1, 10, 50),
            (1, 2, 10, 50),
            (2, 3, 10, 50),
            (0, 3, 20, 50),
            (0, 2, 15, 50),
            (1, 3, 15, 50)
        ]
        building_data = [(10, 150), (10, 150), (10, 150), (10, 150)]
        max_latency = 25
        total_budget = 350
        # A single server placement (for instance at building 1) offers latencies
        # within max_latency for all buildings and the link bandwidth suffices.
        expected = 1
        result = optimal_network_deployment(n, edges, building_data, max_latency, total_budget)
        self.assertEqual(result, expected)

if __name__ == '__main__':
    unittest.main()