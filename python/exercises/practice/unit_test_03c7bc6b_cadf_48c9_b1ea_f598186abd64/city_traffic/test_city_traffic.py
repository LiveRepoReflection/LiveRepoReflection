import unittest
from city_traffic import simulate_traffic

class TestCityTrafficSim(unittest.TestCase):
    def test_simple_case(self):
        num_intersections = 3
        roads = [(0, 1, 10, 2), (1, 2, 5, 1), (2, 0, 3, 3)]
        demands = [5, -3, 0]
        simulation_steps = 5
        
        result = simulate_traffic(num_intersections, roads, demands, simulation_steps)
        
        # Check that the result has the expected length
        self.assertEqual(len(result), num_intersections)
        # Check that all values are non-negative integers
        for cars in result:
            self.assertIsInstance(cars, int)
            self.assertGreaterEqual(cars, 0)
    
    def test_single_intersection(self):
        num_intersections = 1
        roads = []  # No roads
        demands = [5]  # Positive demand, cars will accumulate
        simulation_steps = 10
        
        result = simulate_traffic(num_intersections, roads, demands, simulation_steps)
        
        # Since there are no roads, cars will accumulate based on demand
        self.assertEqual(result[0], 5 * simulation_steps)
    
    def test_single_intersection_with_negative_demand(self):
        num_intersections = 1
        roads = []
        demands = [-5]  # Negative demand, cars will leave
        simulation_steps = 10
        
        result = simulate_traffic(num_intersections, roads, demands, simulation_steps)
        
        # Since there are no cars initially and negative demand, result should be 0
        self.assertEqual(result[0], 0)
    
    def test_balanced_flow(self):
        num_intersections = 2
        roads = [(0, 1, 10, 1), (1, 0, 10, 1)]
        demands = [5, -5]  # Cars enter at 0, leave at 1
        simulation_steps = 10
        
        result = simulate_traffic(num_intersections, roads, demands, simulation_steps)
        
        # After enough steps, we should reach an equilibrium
        # The exact values depend on the simulation implementation details
        self.assertIsNotNone(result)
    
    def test_capacity_limit(self):
        num_intersections = 2
        roads = [(0, 1, 3, 1)]  # Road with capacity 3
        demands = [10, 0]  # Demand exceeds capacity
        simulation_steps = 5
        
        result = simulate_traffic(num_intersections, roads, demands, simulation_steps)
        
        # Check that the result is calculated
        self.assertEqual(len(result), num_intersections)
        # After 5 steps, int. 0 should have cars queued due to limited capacity
        self.assertGreater(result[0] + result[1], 0)
    
    def test_travel_time(self):
        num_intersections = 2
        roads = [(0, 1, 100, 5)]  # Road with long travel time
        demands = [10, 0]
        simulation_steps = 10
        
        result = simulate_traffic(num_intersections, roads, demands, simulation_steps)
        
        # After 10 steps, some cars should have reached intersection 1
        # The exact values depend on the simulation implementation details
        self.assertIsNotNone(result)
    
    def test_self_loop(self):
        num_intersections = 1
        roads = [(0, 0, 5, 2)]  # Road from intersection 0 to itself
        demands = [3, ]
        simulation_steps = 10
        
        result = simulate_traffic(num_intersections, roads, demands, simulation_steps)
        
        # Should have cars at the intersection and possibly on the self-loop road
        self.assertGreaterEqual(result[0], 0)
    
    def test_complex_network(self):
        num_intersections = 5
        roads = [
            (0, 1, 10, 2), (1, 2, 8, 1), (2, 3, 5, 3), (3, 4, 7, 2),
            (4, 0, 6, 4), (1, 3, 4, 1), (2, 0, 3, 2), (4, 2, 2, 3)
        ]
        demands = [5, 2, -3, 0, -4]
        simulation_steps = 20
        
        result = simulate_traffic(num_intersections, roads, demands, simulation_steps)
        
        # Check basic properties of the result
        self.assertEqual(len(result), num_intersections)
        for cars in result:
            self.assertIsInstance(cars, int)
            self.assertGreaterEqual(cars, 0)
    
    def test_large_network(self):
        num_intersections = 50
        roads = []
        # Create a ring topology with some cross connections
        for i in range(num_intersections):
            next_i = (i + 1) % num_intersections
            roads.append((i, next_i, 10, 1))
            # Add some cross connections for every 5th node
            if i % 5 == 0:
                cross_i = (i + 10) % num_intersections
                roads.append((i, cross_i, 5, 2))
        
        # Alternate between positive and negative demand
        demands = [5 if i % 2 == 0 else -5 for i in range(num_intersections)]
        simulation_steps = 50
        
        result = simulate_traffic(num_intersections, roads, demands, simulation_steps)
        
        # Check basic properties of the result
        self.assertEqual(len(result), num_intersections)
        for cars in result:
            self.assertIsInstance(cars, int)
            self.assertGreaterEqual(cars, 0)
    
    def test_edge_case_max_values(self):
        num_intersections = 100
        roads = []
        # Create a fully connected graph with maximum capacity and travel time
        for i in range(num_intersections):
            for j in range(num_intersections):
                if i != j:
                    roads.append((i, j, 50, 10))
        
        # Maximum allowed demands
        demands = [50 if i % 2 == 0 else -50 for i in range(num_intersections)]
        simulation_steps = 100
        
        # This is mostly to test if the solution can handle the maximum input sizes
        # without crashing or timing out
        result = simulate_traffic(num_intersections, roads, demands, simulation_steps)
        
        # Check basic properties of the result
        self.assertEqual(len(result), num_intersections)
        for cars in result:
            self.assertIsInstance(cars, int)
            self.assertGreaterEqual(cars, 0)
    
    def test_no_roads(self):
        num_intersections = 5
        roads = []
        demands = [10, -5, 3, -8, 0]
        simulation_steps = 10
        
        result = simulate_traffic(num_intersections, roads, demands, simulation_steps)
        
        # With no roads, intersections with positive demand should accumulate cars
        # and intersections with negative demand should stay at 0
        for i, demand in enumerate(demands):
            if demand > 0:
                self.assertEqual(result[i], demand * simulation_steps)
            else:
                self.assertEqual(result[i], 0)

if __name__ == '__main__':
    unittest.main()