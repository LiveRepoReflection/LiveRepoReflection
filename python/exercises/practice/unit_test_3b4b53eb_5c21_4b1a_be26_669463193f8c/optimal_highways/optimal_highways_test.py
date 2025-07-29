import unittest
from optimal_highways.optimal_highways import find_optimal_highway_network

class TestOptimalHighways(unittest.TestCase):
    def test_sample_valid_network(self):
        # Test case based on sample input 1
        N = 5
        B = 20
        D = 2
        city_costs = [
            (1, 2, 5),
            (1, 3, 7),
            (2, 3, 2),
            (2, 4, 4),
            (3, 5, 3),
            (4, 5, 6),
            (1, 5, 8)
        ]
        strategic_hubs = [1, 4, 5]
        # Expected output is 2 if a configuration exists that meets all constraints.
        self.assertEqual(find_optimal_highway_network(N, B, D, city_costs, strategic_hubs), 2)

    def test_sample_no_solution(self):
        # Test case based on sample input 2 where constraints cannot be met
        N = 4
        B = 5
        D = 1
        city_costs = [
            (1, 2, 5),
            (1, 3, 7),
            (2, 3, 2),
            (2, 4, 4),
            (3, 4, 6)
        ]
        strategic_hubs = [1, 4]
        self.assertEqual(find_optimal_highway_network(N, B, D, city_costs, strategic_hubs), -1)

    def test_trivial_two_cities(self):
        # Minimal case with just 2 cities connected by one highway.
        N = 2
        B = 10
        D = 1
        city_costs = [
            (1, 2, 1)
        ]
        strategic_hubs = [1, 2]
        # Only one edge and hence maximum degree is 1.
        self.assertEqual(find_optimal_highway_network(N, B, D, city_costs, strategic_hubs), 1)

    def test_complex_network(self):
        # A more complex graph with multiple edges between cities.
        N = 6
        B = 50
        D = 3
        city_costs = [
            (1, 2, 5),
            (1, 2, 3),  # duplicate edge with lower cost
            (2, 3, 4),
            (2, 4, 8),
            (3, 4, 2),
            (3, 5, 7),
            (4, 5, 3),
            (4, 6, 6),
            (5, 6, 1)
        ]
        strategic_hubs = [1, 5, 6]
        # One possible valid network: select edges (1,2) cost 3, (2,3) cost 4, (3,4) cost 2,
        # (4,5) cost 3, (4,6) cost 6. Total cost = 18 and strategic hubs 1,5,6 have distances:
        # 1->5: 1-2-3-4-5 (4 segments) is too long.
        # A better selection ensuring hubs distance <= 3 may be:
        # (1,2)=3, (2,4)=8, (4,5)=3, (4,6)=6, (2,3)=4 ensuring connectivity.
        # Here, the maximum degree is 3 (city 2 or 4) and all strategic hubs are within 3 segments.
        # Expected output is 3.
        self.assertEqual(find_optimal_highway_network(N, B, D, city_costs, strategic_hubs), 3)

    def test_budget_too_low(self):
        # Test when the available budget is too low to construct a connected network.
        N = 3
        B = 1
        D = 2
        city_costs = [
            (1, 2, 2),
            (2, 3, 2),
            (1, 3, 5)
        ]
        strategic_hubs = [1, 3]
        self.assertEqual(find_optimal_highway_network(N, B, D, city_costs, strategic_hubs), -1)

if __name__ == '__main__':
    unittest.main()