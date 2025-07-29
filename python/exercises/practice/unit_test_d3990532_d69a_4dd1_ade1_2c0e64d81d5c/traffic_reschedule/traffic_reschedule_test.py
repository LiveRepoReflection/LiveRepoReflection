import unittest
from traffic_reschedule import optimize_traffic_flow

class TestTrafficReschedule(unittest.TestCase):
    def setUp(self):
        # Set up a sample graph for testing
        self.graph = {
            1: {2: {"length": 500, "speed_limit": 50}, 3: {"length": 800, "speed_limit": 60}},
            2: {4: {"length": 1200, "speed_limit": 40}},
            3: {4: {"length": 600, "speed_limit": 30}},
            4: {}
        }
        self.light_cycles = {
            1: [30, 30],
            2: [40, 20],
            3: [50, 10],
            4: [25, 35]
        }

    def validate_output_cycles(self, original_cycles, new_cycles):
        # Ensure returned cycles maintain same total cycle length and each phase is at least 5 seconds
        self.assertEqual(set(original_cycles.keys()), set(new_cycles.keys()))
        for key in original_cycles:
            orig_total = sum(original_cycles[key])
            new_total = sum(new_cycles[key])
            self.assertEqual(orig_total, new_total, f"Cycle sum mismatch at intersection {key}")
            # Check each phase is not below the minimum requirement of 5 seconds
            for interval in new_cycles[key]:
                self.assertGreaterEqual(interval, 5, f"Interval at intersection {key} is less than 5 seconds")

    def test_travel_time_optimization(self):
        # Test optimize_traffic_flow with optimization_target 'travel_time'
        demand = {
            (1, 4): 300,
            (2, 4): 200,
            (3, 4): 100
        }
        new_cycles = optimize_traffic_flow(self.graph, demand, self.light_cycles, "travel_time")
        self.validate_output_cycles(self.light_cycles, new_cycles)

    def test_throughput_optimization(self):
        # Test optimize_traffic_flow with optimization_target 'throughput'
        demand = {
            (1, 4): 500,
            (2, 4): 300
        }
        new_cycles = optimize_traffic_flow(self.graph, demand, self.light_cycles, "throughput")
        self.validate_output_cycles(self.light_cycles, new_cycles)

    def test_no_demand(self):
        # Test handling when no demand is provided; function should return valid cycles
        demand = {}
        new_cycles = optimize_traffic_flow(self.graph, demand, self.light_cycles, "travel_time")
        self.validate_output_cycles(self.light_cycles, new_cycles)

    def test_disconnected_graph(self):
        # Test with a graph having a disconnected intersection
        graph = {
            1: {2: {"length": 400, "speed_limit": 40}},
            2: {},
            3: {}  # Disconnected node
        }
        light_cycles = {
            1: [35, 25],
            2: [30, 30],
            3: [50, 20]
        }
        demand = {
            (1, 2): 100,
            (3, 1): 50  # Demand involving a disconnected node
        }
        new_cycles = optimize_traffic_flow(graph, demand, light_cycles, "throughput")
        self.validate_output_cycles(light_cycles, new_cycles)

    def test_invalid_optimization_target(self):
        # Test that an invalid optimization_target raises an error
        demand = {(1, 4): 300}
        with self.assertRaises(ValueError):
            optimize_traffic_flow(self.graph, demand, self.light_cycles, "invalid_target")

if __name__ == '__main__':
    unittest.main()