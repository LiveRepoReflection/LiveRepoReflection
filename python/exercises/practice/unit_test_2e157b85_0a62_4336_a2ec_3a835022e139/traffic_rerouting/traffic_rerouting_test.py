import unittest
from traffic_rerouting import optimal_evacuation

class TrafficReroutingTest(unittest.TestCase):
    def test_simple_evacuation(self):
        n = 4
        m = 5
        edges = [
            (0, 1, 10, 2),  # Intersection 0 to 1, capacity 10, travel time 2
            (0, 2, 5, 3),   # Intersection 0 to 2, capacity 5, travel time 3
            (1, 3, 15, 1),  # Intersection 1 to 3, capacity 15, travel time 1
            (2, 3, 7, 2),   # Intersection 2 to 3, capacity 7, travel time 2
            (0, 3, 3, 5)    # Intersection 0 to 3, capacity 3, travel time 5
        ]
        population = [100, 50, 75, 0]  # Population at intersections 0, 1, 2, 3
        safe_zone = 3
        increase_cost = 2
        decrease_cost = 1
        
        evacuation_time, adjustment_cost = optimal_evacuation(n, m, edges, population, safe_zone, increase_cost, decrease_cost)
        
        # We can't assert exact values without knowing the optimal solution,
        # but we can check that the values are reasonable
        self.assertTrue(evacuation_time > 0)
        self.assertIsInstance(evacuation_time, (int, float))
        self.assertIsInstance(adjustment_cost, (int, float))
        
    def test_no_routes_to_safe_zone(self):
        n = 3
        m = 1
        edges = [(0, 1, 10, 2)]  # Only a route from 0 to 1, none to safe zone 2
        population = [10, 20, 0]
        safe_zone = 2
        increase_cost = 2
        decrease_cost = 1
        
        evacuation_time, adjustment_cost = optimal_evacuation(n, m, edges, population, safe_zone, increase_cost, decrease_cost)
        
        # Since no one can reach the safe zone, evacuation time should be 0
        self.assertEqual(evacuation_time, 0)
        self.assertEqual(adjustment_cost, 0)
        
    def test_already_at_safe_zone(self):
        n = 3
        m = 2
        edges = [(0, 2, 10, 2), (1, 2, 5, 3)]
        population = [0, 0, 100]  # Everyone is already at the safe zone
        safe_zone = 2
        increase_cost = 2
        decrease_cost = 1
        
        evacuation_time, adjustment_cost = optimal_evacuation(n, m, edges, population, safe_zone, increase_cost, decrease_cost)
        
        # Since everyone is already at the safe zone, evacuation time should be 0
        self.assertEqual(evacuation_time, 0)
        self.assertEqual(adjustment_cost, 0)
        
    def test_multiple_paths_to_safe_zone(self):
        n = 4
        m = 6
        edges = [
            (0, 1, 10, 2),
            (0, 2, 8, 1),
            (1, 3, 5, 3),
            (1, 2, 2, 1),
            (2, 3, 7, 2),
            (0, 3, 3, 5)
        ]
        population = [100, 50, 75, 0]
        safe_zone = 3
        increase_cost = 2
        decrease_cost = 1
        
        evacuation_time, adjustment_cost = optimal_evacuation(n, m, edges, population, safe_zone, increase_cost, decrease_cost)
        
        self.assertTrue(evacuation_time > 0)
        self.assertIsInstance(evacuation_time, (int, float))
        self.assertIsInstance(adjustment_cost, (int, float))
        
    def test_chain_network(self):
        n = 5
        m = 4
        edges = [
            (0, 1, 10, 1),
            (1, 2, 8, 1),
            (2, 3, 6, 1),
            (3, 4, 5, 1)
        ]
        population = [100, 75, 50, 25, 0]
        safe_zone = 4
        increase_cost = 2
        decrease_cost = 1
        
        evacuation_time, adjustment_cost = optimal_evacuation(n, m, edges, population, safe_zone, increase_cost, decrease_cost)
        
        self.assertTrue(evacuation_time > 0)
        self.assertIsInstance(evacuation_time, (int, float))
        self.assertIsInstance(adjustment_cost, (int, float))
        
    def test_larger_network(self):
        n = 8
        m = 12
        edges = [
            (0, 1, 10, 2),
            (0, 2, 8, 3),
            (1, 3, 5, 1),
            (1, 4, 7, 2),
            (2, 4, 6, 3),
            (2, 5, 4, 1),
            (3, 6, 3, 2),
            (3, 7, 9, 4),
            (4, 6, 5, 2),
            (4, 7, 8, 3),
            (5, 7, 6, 1),
            (6, 7, 4, 1)
        ]
        population = [200, 150, 100, 75, 50, 25, 10, 0]
        safe_zone = 7
        increase_cost = 3
        decrease_cost = 2
        
        evacuation_time, adjustment_cost = optimal_evacuation(n, m, edges, population, safe_zone, increase_cost, decrease_cost)
        
        self.assertTrue(evacuation_time > 0)
        self.assertIsInstance(evacuation_time, (int, float))
        self.assertIsInstance(adjustment_cost, (int, float))
        
    def test_cyclic_graph(self):
        n = 4
        m = 4
        edges = [
            (0, 1, 10, 2),
            (1, 2, 8, 1),
            (2, 0, 6, 3),
            (1, 3, 5, 2)
        ]
        population = [100, 75, 50, 0]
        safe_zone = 3
        increase_cost = 2
        decrease_cost = 1
        
        evacuation_time, adjustment_cost = optimal_evacuation(n, m, edges, population, safe_zone, increase_cost, decrease_cost)
        
        self.assertTrue(evacuation_time > 0)
        self.assertIsInstance(evacuation_time, (int, float))
        self.assertIsInstance(adjustment_cost, (int, float))
        
    def test_max_capacity_adjustment_constraints(self):
        # Test that the solution respects the 50% max capacity adjustment constraint
        n = 3
        m = 2
        edges = [
            (0, 2, 10, 5),  # Capacity is 10
            (1, 2, 10, 5)   # Capacity is 10
        ]
        population = [100, 100, 0]
        safe_zone = 2
        increase_cost = 1
        decrease_cost = 1
        
        evacuation_time, adjustment_cost = optimal_evacuation(n, m, edges, population, safe_zone, increase_cost, decrease_cost)
        
        # With 100 vehicles each and max 15 capacity (10 + 50% increase), the evacuation would take at least
        # 100/15 * 5 time units for each node
        min_expected_time = (100 / 15) * 5
        self.assertTrue(evacuation_time >= min_expected_time)
        self.assertIsInstance(evacuation_time, (int, float))
        self.assertIsInstance(adjustment_cost, (int, float))
    
    def test_edge_case_huge_population(self):
        n = 2
        m = 1
        edges = [(0, 1, 10, 1)]
        population = [1000, 0]
        safe_zone = 1
        increase_cost = 2
        decrease_cost = 1
        
        evacuation_time, adjustment_cost = optimal_evacuation(n, m, edges, population, safe_zone, increase_cost, decrease_cost)
        
        # With 1000 vehicles and max capacity of 15 (10 + 50%), it would take at least 1000/15 time units
        min_expected_time = 1000 / 15
        self.assertTrue(evacuation_time >= min_expected_time)
        self.assertIsInstance(evacuation_time, (int, float))
        self.assertIsInstance(adjustment_cost, (int, float))

if __name__ == "__main__":
    unittest.main()