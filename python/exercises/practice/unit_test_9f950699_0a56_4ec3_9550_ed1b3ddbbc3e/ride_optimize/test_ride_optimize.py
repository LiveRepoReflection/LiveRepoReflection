import unittest
from ride_optimize import optimize_rides

class TestRideOptimization(unittest.TestCase):
    def setUp(self):
        # Simple graph for basic test cases
        self.small_graph = {
            0: {1: 5, 2: 4},
            1: {0: 5, 2: 2},
            2: {0: 4, 1: 2}
        }

        # Larger graph for more complex scenarios
        self.large_graph = {
            node: {(node + i) % 20: i + 1 for i in range(1, 6)}
            for node in range(20)
        }

    def test_basic_assignment(self):
        drivers = [(0, 0, 1)]  # (driver_id, location, capacity)
        passengers = [(0, 1, 2, 10)]  # (passenger_id, pickup, destination, max_wait)
        
        result = optimize_rides(self.small_graph, drivers, passengers)
        self.assertIsInstance(result, list)
        self.assertTrue(all(isinstance(x, tuple) and len(x) == 2 for x in result))

    def test_no_possible_assignment(self):
        drivers = [(0, 0, 1)]
        passengers = [(0, 1, 2, 1)]  # Max wait time too short
        
        result = optimize_rides(self.small_graph, drivers, passengers)
        self.assertEqual(result, [])

    def test_multiple_drivers_and_passengers(self):
        drivers = [
            (0, 0, 2),
            (1, 1, 2),
            (2, 2, 2)
        ]
        passengers = [
            (0, 0, 1, 10),
            (1, 1, 2, 10),
            (2, 2, 0, 10)
        ]
        
        result = optimize_rides(self.small_graph, drivers, passengers)
        self.assertLessEqual(len(result), len(passengers))
        assigned_passengers = set(p for _, p in result)
        self.assertLessEqual(len(assigned_passengers), len(passengers))

    def test_capacity_constraints(self):
        drivers = [(0, 0, 1)]  # Capacity of 1
        passengers = [
            (0, 1, 2, 10),
            (1, 1, 2, 10)
        ]
        
        result = optimize_rides(self.small_graph, drivers, passengers)
        driver_assignments = {}
        for d, p in result:
            driver_assignments[d] = driver_assignments.get(d, 0) + 1
        
        for d, count in driver_assignments.items():
            self.assertLessEqual(count, 1)  # Check capacity constraint

    def test_waiting_time_constraints(self):
        drivers = [(0, 0, 1)]
        passengers = [(0, 2, 1, 3)]  # Max wait time of 3
        
        result = optimize_rides(self.small_graph, drivers, passengers)
        self.assertTrue(len(result) <= 1)

    def test_large_scale_scenario(self):
        # Generate 50 drivers and 100 passengers
        drivers = [(i, i % 20, 4) for i in range(50)]
        passengers = [(i, i % 20, (i + 5) % 20, 15) for i in range(100)]
        
        result = optimize_rides(self.large_graph, drivers, passengers)
        
        # Basic validation
        self.assertIsInstance(result, list)
        self.assertTrue(all(isinstance(x, tuple) and len(x) == 2 for x in result))
        
        # Check for duplicate assignments
        assigned_passengers = set(p for _, p in result)
        self.assertEqual(len(assigned_passengers), len(result))

    def test_invalid_inputs(self):
        # Test with empty graph
        with self.assertRaises((ValueError, TypeError)):
            optimize_rides({}, [], [])

        # Test with negative weights
        invalid_graph = {0: {1: -5}}
        with self.assertRaises(ValueError):
            optimize_rides(invalid_graph, [(0, 0, 1)], [(0, 0, 1, 10)])

        # Test with invalid locations
        with self.assertRaises(ValueError):
            optimize_rides(self.small_graph, [(0, 5, 1)], [(0, 0, 1, 10)])

    def test_performance(self):
        import time
        
        # Generate large test case
        drivers = [(i, i % 20, 4) for i in range(200)]
        passengers = [(i, i % 20, (i + 5) % 20, 15) for i in range(200)]
        
        start_time = time.time()
        result = optimize_rides(self.large_graph, drivers, passengers)
        end_time = time.time()
        
        self.assertLess(end_time - start_time, 1.0)  # Should complete within 1 second

if __name__ == '__main__':
    unittest.main()