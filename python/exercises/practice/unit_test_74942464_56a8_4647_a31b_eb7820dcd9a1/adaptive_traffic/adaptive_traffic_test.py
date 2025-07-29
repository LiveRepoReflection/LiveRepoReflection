import unittest
from adaptive_traffic import optimize_traffic_flow

class AdaptiveTrafficTest(unittest.TestCase):
    def setUp(self):
        self.graph = {
            0: {1: 100, 2: 50},
            1: {2: 75},
            2: {}
        }
        self.demands_simple = [
            [
                [0, 60, 20],
                [0, 0, 30],
                [0, 0, 0]
            ],
            [
                [0, 40, 10],
                [0, 0, 20],
                [0, 0, 0]
            ]
        ]
        self.max_green_time = 30
        self.time_limit = 20

    def test_correct_flow_assignment_length(self):
        # Ensure the number of time intervals in the output matches the input demands.
        assignments = optimize_traffic_flow(self.graph, self.demands_simple, self.max_green_time, self.time_limit)
        self.assertEqual(len(assignments), len(self.demands_simple),
                         "The output length should match the number of time intervals in demands.")

    def test_flow_capacity_constraints(self):
        # For every edge, the assigned traffic flow must not exceed the road's capacity.
        assignments = optimize_traffic_flow(self.graph, self.demands_simple, self.max_green_time, self.time_limit)
        for t, flow_assignment in enumerate(assignments):
            for src, targets in self.graph.items():
                for dest, capacity in targets.items():
                    flow = flow_assignment.get((src, dest), 0)
                    self.assertLessEqual(flow, capacity,
                        f"Time interval {t}: Flow on edge ({src}, {dest}) exceeds capacity")

    def test_flow_satisfaction_of_demand(self):
        # When network capacity permits, the total outflow should equal the total demand from that intersection.
        assignments = optimize_traffic_flow(self.graph, self.demands_simple, self.max_green_time, self.time_limit)
        for t, flow_assignment in enumerate(assignments):
            for i in range(len(self.demands_simple[t])):
                total_demand = sum(self.demands_simple[t][i])
                total_flow = sum(flow for (src, _), flow in flow_assignment.items() if src == i)
                # Total flow should not exceed total demand.
                self.assertLessEqual(total_flow, total_demand,
                    f"Time interval {t}: Total flow from intersection {i} exceeds its total demand")

    def test_edge_case_empty_demand(self):
        # Test the scenario when all demands are zero.
        zero_demands = [
            [
                [0, 0, 0],
                [0, 0, 0],
                [0, 0, 0]
            ]
        ]
        assignments = optimize_traffic_flow(self.graph, zero_demands, self.max_green_time, self.time_limit)
        for t, flow_assignment in enumerate(assignments):
            for key, flow in flow_assignment.items():
                self.assertEqual(flow, 0,
                    f"Time interval {t}: Expected zero flow on edge {key} when demand is zero")

    def test_complex_scenario(self):
        # A more complex graph with multiple time intervals and higher demands.
        graph_complex = {
            0: {1: 150, 2: 100},
            1: {2: 120, 3: 80},
            2: {3: 100},
            3: {}
        }
        demands_complex = [
            [
                [0, 80, 40, 0],
                [0, 0, 60, 20],
                [0, 0, 0, 50],
                [0, 0, 0, 0]
            ],
            [
                [0, 90, 30, 0],
                [0, 0, 70, 10],
                [0, 0, 0, 60],
                [0, 0, 0, 0]
            ],
            [
                [0, 100, 50, 10],
                [0, 0, 80, 30],
                [0, 0, 0, 70],
                [0, 0, 0, 0]
            ]
        ]
        assignments = optimize_traffic_flow(graph_complex, demands_complex, self.max_green_time, self.time_limit)
        self.assertEqual(len(assignments), len(demands_complex),
                         "Output intervals must match the number of demand intervals.")
        for t, flow_assignment in enumerate(assignments):
            for src, targets in graph_complex.items():
                for dest, capacity in targets.items():
                    flow = flow_assignment.get((src, dest), 0)
                    self.assertLessEqual(flow, capacity,
                        f"Time interval {t}: Flow on edge ({src}, {dest}) exceeds capacity")

if __name__ == '__main__':
    unittest.main()