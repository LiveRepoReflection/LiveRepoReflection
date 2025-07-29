import unittest
from highway_exits import find_optimal_exits
import math

class TestHighwayExits(unittest.TestCase):
    def assertListAlmostEqual(self, list1, list2, places=6):
        """Compare two lists of floats with a specified precision."""
        self.assertEqual(len(list1), len(list2))
        for a, b in zip(list1, list2):
            self.assertAlmostEqual(a, b, places=places)

    def test_single_zone_single_exit(self):
        # With only one residential zone and one exit, the exit should be placed at the zone's x position
        L = 10
        N = 1
        residential_zones = [(5, 2, 10)]  # (x, y, population)
        v1 = 1
        v2 = 2
        expected = [5.0]
        result = find_optimal_exits(L, N, residential_zones, v1, v2)
        self.assertListAlmostEqual(result, expected)

    def test_three_zones_two_exits(self):
        # With three zones and two exits, optimization is more complex
        L = 10
        N = 2
        residential_zones = [(2, 5, 10), (5, 2, 15), (8, 3, 20)]
        v1 = 1
        v2 = 2
        # The exact solution depends on the optimization algorithm, but we can provide a reference solution
        # for this simple case. For v1=1, v2=2, the optimal positions should be close to our expected output.
        result = find_optimal_exits(L, N, residential_zones, v1, v2)
        # Check that we get exactly N exits
        self.assertEqual(len(result), N)
        # Check that all exits are within the highway length
        for pos in result:
            self.assertTrue(0 <= pos <= L)
        # Check that the exits are sorted
        self.assertEqual(result, sorted(result))

    def test_multiple_zones_multiple_exits(self):
        L = 20
        N = 3
        residential_zones = [(2, 3, 50), (6, 2, 30), (10, 1, 20), (15, 4, 40), (18, 2, 60)]
        v1 = 2
        v2 = 5
        result = find_optimal_exits(L, N, residential_zones, v1, v2)
        # Check that we get exactly N exits
        self.assertEqual(len(result), N)
        # Check that all exits are within the highway length
        for pos in result:
            self.assertTrue(0 <= pos <= L)
        # Check that the exits are sorted
        self.assertEqual(result, sorted(result))

    def test_clustered_zones(self):
        # Test with zones clustered at three different locations
        L = 100
        N = 3
        residential_zones = [
            (10, 2, 100), (11, 2, 100), (12, 2, 100),  # Cluster 1
            (50, 3, 100), (51, 3, 100), (52, 3, 100),  # Cluster 2
            (90, 1, 100), (91, 1, 100), (92, 1, 100)   # Cluster 3
        ]
        v1 = 1
        v2 = 3
        # With equal populations and similar y-values, the exits should be placed near the center of each cluster
        expected_approximate = [11.0, 51.0, 91.0]  # Approximate expected positions
        result = find_optimal_exits(L, N, residential_zones, v1, v2)
        # Check we have N exits
        self.assertEqual(len(result), N)
        
        # Check exits are sorted and within bounds
        self.assertEqual(result, sorted(result))
        for pos in result:
            self.assertTrue(0 <= pos <= L)
            
        # In this special case, exits should be close to the centers of the clusters
        # We use a larger tolerance for this check as the exact positions depend on the optimization algorithm
        for expected, actual in zip(expected_approximate, result):
            self.assertTrue(abs(expected - actual) < 5)

    def test_edge_case_no_solution(self):
        # Test with no residential zones - any placement should be valid
        L = 10
        N = 2
        residential_zones = []
        v1 = 1
        v2 = 2
        result = find_optimal_exits(L, N, residential_zones, v1, v2)
        # Check that we get exactly N exits
        self.assertEqual(len(result), N)
        # Check that all exits are within the highway length
        for pos in result:
            self.assertTrue(0 <= pos <= L)
        # Check that the exits are sorted
        self.assertEqual(result, sorted(result))

    def test_edge_case_all_zones_same_location(self):
        # Test with all zones at the same x-position
        L = 10
        N = 2
        residential_zones = [(5, 1, 10), (5, 2, 20), (5, 3, 30)]
        v1 = 1
        v2 = 2
        # One exit should be at x=5, and the other could be anywhere since it's redundant
        result = find_optimal_exits(L, N, residential_zones, v1, v2)
        # Check that we get exactly N exits
        self.assertEqual(len(result), N)
        # The first exit should be at position 5
        self.assertAlmostEqual(result[0], 5.0)

    def test_many_zones_many_exits(self):
        # Test with more zones and exits to ensure algorithm efficiency
        L = 100
        N = 10
        # Create 100 random residential zones
        import random
        random.seed(42)  # For reproducibility
        residential_zones = [(random.randint(0, L), random.randint(1, 10), random.randint(10, 100)) 
                             for _ in range(100)]
        v1 = 2
        v2 = 5
        result = find_optimal_exits(L, N, residential_zones, v1, v2)
        # Check that we get exactly N exits
        self.assertEqual(len(result), N)
        # Check that all exits are within the highway length
        for pos in result:
            self.assertTrue(0 <= pos <= L)
        # Check that the exits are sorted
        self.assertEqual(result, sorted(result))

    def test_calculate_total_travel_time(self):
        # Helper function to calculate total travel time for a given exit position
        def calculate_travel_time(zone, exit_pos, v1, v2):
            x, y, pop = zone
            # Time to reach the highway
            highway_time = y / v1
            # Time along the highway to the exit
            exit_time = abs(x - exit_pos) / v2
            return pop * (highway_time + exit_time)
        
        # Helper function to calculate total travel time for all zones
        def calculate_total_time(zones, exits, v1, v2):
            total = 0
            for zone in zones:
                # Find the minimum travel time for each zone to any exit
                min_time = float('inf')
                for exit_pos in exits:
                    time = calculate_travel_time(zone, exit_pos, v1, v2)
                    min_time = min(min_time, time)
                total += min_time
            return total
        
        # Simple test case
        L = 10
        N = 2
        residential_zones = [(2, 5, 10), (8, 3, 20)]
        v1 = 1
        v2 = 2
        
        # Try obvious solution of placing exits at positions 2 and 8
        simple_solution = [2.0, 8.0]
        simple_total_time = calculate_total_time(residential_zones, simple_solution, v1, v2)
        
        # Get our algorithm's solution
        algorithm_solution = find_optimal_exits(L, N, residential_zones, v1, v2)
        algorithm_total_time = calculate_total_time(residential_zones, algorithm_solution, v1, v2)
        
        # The algorithm's solution should provide a total time less than or equal to our simple solution
        self.assertLessEqual(algorithm_total_time, simple_total_time)
        
    def test_constraints(self):
        # Test with the maximum allowed constraints
        L = 1000
        N = 100
        M = 100  # Using a smaller M than the max for test performance
        import random
        random.seed(42)  # For reproducibility
        residential_zones = [(random.randint(0, L), random.randint(1, 100), random.randint(1, 1000)) 
                             for _ in range(M)]
        v1 = 1
        v2 = 100
        
        result = find_optimal_exits(L, N, residential_zones, v1, v2)
        # Check that we get exactly N exits
        self.assertEqual(len(result), N)
        # Check that all exits are within the highway length
        for pos in result:
            self.assertTrue(0 <= pos <= L)
        # Check that the exits are sorted
        self.assertEqual(result, sorted(result))

    def test_equal_travel_speed(self):
        # Test case where v1 = v2 to catch potential division by zero issues
        L = 10
        N = 2
        residential_zones = [(2, 5, 10), (8, 3, 20)]
        v1 = 5
        v2 = 5
        
        result = find_optimal_exits(L, N, residential_zones, v1, v2)
        # Just check that the function returns N exits without errors
        self.assertEqual(len(result), N)

if __name__ == '__main__':
    unittest.main()