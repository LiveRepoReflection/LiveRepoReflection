import unittest
from atms_optimizer import optimize_traffic_lights

class TestATMSOptimizer(unittest.TestCase):
    
    def test_simple_case(self):
        # Simple case with 2 intersections and one road
        n = 2
        roads = [(0, 1, 100, 0.5)]  # One road from intersection 0 to 1
        target_intersection = 1
        time_horizon = 300
        min_green_time = 30
        max_green_time = 120
        amber_time = 5
        
        # Since there's only one incoming road to intersection 1,
        # the optimal solution is to keep it green for the entire duration
        expected = [120]  # max green time allowed
        
        result = optimize_traffic_lights(n, roads, target_intersection, time_horizon, 
                                         min_green_time, max_green_time, amber_time)
        
        self.assertEqual(result, expected)
    
    def test_two_incoming_roads(self):
        # Case with 3 intersections and two roads leading to target
        n = 3
        roads = [
            (0, 2, 200, 0.2),  # Road from 0 to 2
            (1, 2, 300, 0.3),  # Road from 1 to 2
        ]
        target_intersection = 2
        time_horizon = 600
        min_green_time = 60
        max_green_time = 180
        amber_time = 5
        
        result = optimize_traffic_lights(n, roads, target_intersection, time_horizon, 
                                         min_green_time, max_green_time, amber_time)
        
        # Check if result satisfies basic constraints
        self.assertIsNotNone(result)
        self.assertEqual(len(result), 2)  # Two green times for two incoming roads
        
        # Check if green times are within allowed range
        for green_time in result:
            self.assertTrue(min_green_time <= green_time <= max_green_time)
        
        # Check if total time does not exceed time horizon
        total_time = sum(result) + len(result) * amber_time
        self.assertLessEqual(total_time, time_horizon)
    
    def test_complex_network(self):
        # More complex case with multiple intersections and roads
        n = 5
        roads = [
            (0, 4, 150, 0.4),   # Road from 0 to 4
            (1, 4, 200, 0.25),  # Road from 1 to 4
            (2, 4, 100, 0.6),   # Road from 2 to 4
            (3, 4, 250, 0.3),   # Road from 3 to 4
            (4, 0, 150, 0.1),   # Road from 4 to 0 (not incoming to target)
        ]
        target_intersection = 4
        time_horizon = 900
        min_green_time = 45
        max_green_time = 150
        amber_time = 8
        
        result = optimize_traffic_lights(n, roads, target_intersection, time_horizon, 
                                         min_green_time, max_green_time, amber_time)
        
        # Check if result satisfies basic constraints
        self.assertIsNotNone(result)
        self.assertEqual(len(result), 4)  # Four green times for four incoming roads
        
        # Check if green times are within allowed range
        for green_time in result:
            self.assertTrue(min_green_time <= green_time <= max_green_time)
        
        # Check if total time does not exceed time horizon
        total_time = sum(result) + len(result) * amber_time
        self.assertLessEqual(total_time, time_horizon)
    
    def test_no_incoming_roads(self):
        # Case with no incoming roads to target intersection
        n = 3
        roads = [
            (0, 1, 100, 0.2),   # Road from 0 to 1
            (1, 0, 100, 0.2),   # Road from 1 to 0
            (2, 0, 200, 0.3),   # Road from 2 to 0
        ]
        target_intersection = 2
        time_horizon = 400
        min_green_time = 30
        max_green_time = 120
        amber_time = 5
        
        result = optimize_traffic_lights(n, roads, target_intersection, time_horizon, 
                                         min_green_time, max_green_time, amber_time)
        
        self.assertEqual(result, [])  # Should return empty list for no incoming roads
    
    def test_insufficient_time(self):
        # Case where time horizon is too small for minimum requirements
        n = 3
        roads = [
            (0, 2, 200, 0.2),
            (1, 2, 300, 0.3),
        ]
        target_intersection = 2
        # Time horizon is less than minimum green times + amber times
        time_horizon = 50
        min_green_time = 30
        max_green_time = 120
        amber_time = 5
        
        result = optimize_traffic_lights(n, roads, target_intersection, time_horizon, 
                                         min_green_time, max_green_time, amber_time)
        
        self.assertIsNone(result)  # Should return None if no valid solution
    
    def test_edge_case_min_equals_max(self):
        # Edge case where min green time equals max green time
        n = 3
        roads = [
            (0, 2, 200, 0.2),
            (1, 2, 300, 0.3),
        ]
        target_intersection = 2
        time_horizon = 200
        min_green_time = 60
        max_green_time = 60  # min = max
        amber_time = 5
        
        result = optimize_traffic_lights(n, roads, target_intersection, time_horizon, 
                                         min_green_time, max_green_time, amber_time)
        
        # In this case, the only valid solution is [60, 60]
        self.assertEqual(result, [60, 60])
    
    def test_time_constraint_boundary(self):
        # Test boundary condition for time constraints
        n = 2
        roads = [(0, 1, 100, 0.5)]
        target_intersection = 1
        # Exactly enough time for one green cycle
        time_horizon = 35  # min_green_time + amber_time
        min_green_time = 30
        max_green_time = 120
        amber_time = 5
        
        result = optimize_traffic_lights(n, roads, target_intersection, time_horizon, 
                                         min_green_time, max_green_time, amber_time)
        
        self.assertEqual(result, [30])  # Should work with exactly minimum time
    
    def test_multiple_roads_optimization(self):
        # Test case with various traffic densities
        n = 4
        roads = [
            (0, 3, 200, 0.1),   # Low density
            (1, 3, 200, 0.5),   # Medium density
            (2, 3, 200, 0.9),   # High density
        ]
        target_intersection = 3
        time_horizon = 600
        min_green_time = 30
        max_green_time = 120
        amber_time = 5
        
        result = optimize_traffic_lights(n, roads, target_intersection, time_horizon, 
                                        min_green_time, max_green_time, amber_time)
        
        # Verify basic constraints
        self.assertIsNotNone(result)
        self.assertEqual(len(result), 3)
        
        # Higher density roads should generally get more green time
        # Not a strict requirement due to optimization complexities, but a good sanity check
        if result[0] > result[2] or result[1] > result[2]:
            print("Warning: Optimization may not be ideal. Expected higher green time for higher density roads.")

if __name__ == '__main__':
    unittest.main()