import unittest
from traffic_congestion import routing_function

class TrafficCongestionTest(unittest.TestCase):
    def simulate(self, n, edges, initial_vehicles, time_steps):
        allowed_edges = {(u, v) for (u, v, capacity) in edges}
        current_vehicles = initial_vehicles.copy()
        max_congestion_over_time = 0
        # Simulate each time step
        for t in range(time_steps):
            decision = routing_function(n, edges, current_vehicles, t)
            # Check that decisions contain only allowed edges and non-negative integers.
            node_outflow = [0] * n
            for (u, v), vehicles in decision.items():
                self.assertIn((u, v), allowed_edges, f"Edge {(u, v)} is not allowed.")
                self.assertIsInstance(vehicles, int, "Number of vehicles must be an integer.")
                self.assertGreaterEqual(vehicles, 0, "Number of vehicles must be non-negative.")
                node_outflow[u] += vehicles
            # Ensure outflow does not exceed available vehicles at each intersection
            for i in range(n):
                self.assertLessEqual(node_outflow[i], current_vehicles[i],
                                     f"Vehicles routed from node {i} exceed available vehicles.")
            # Update the vehicles: subtract outgoing and add incoming vehicles.
            new_vehicles = [0] * n
            for i in range(n):
                new_vehicles[i] = current_vehicles[i] - node_outflow[i]
            for (u, v), vehicles in decision.items():
                new_vehicles[v] += vehicles
            current_vehicles = new_vehicles

            # Calculate congestion for the current time step.
            for (u, v), vehicles in decision.items():
                cap = None
                for (start, end, capacity) in edges:
                    if (start, end) == (u, v):
                        cap = capacity
                        break
                self.assertIsNotNone(cap, "Capacity for edge not found.")
                congestion = max(0, vehicles - cap)
                max_congestion_over_time = max(max_congestion_over_time, congestion)
        return current_vehicles, max_congestion_over_time

    def test_single_time_step(self):
        n = 3
        edges = [(0, 1, 10), (0, 2, 5), (1, 2, 7)]
        initial_vehicles = [20, 5, 0]
        time_steps = 1
        final_vehicles, max_congestion = self.simulate(n, edges, initial_vehicles, time_steps)
        # Verify conservation of vehicles
        self.assertEqual(sum(initial_vehicles), sum(final_vehicles))
        self.assertGreaterEqual(max_congestion, 0)

    def test_multiple_time_steps(self):
        n = 5
        edges = [(0, 1, 8), (1, 2, 6), (2, 3, 10), (3, 4, 5), (0, 2, 7), (1, 3, 4), (2, 4, 9)]
        initial_vehicles = [15, 10, 5, 0, 0]
        time_steps = 5
        final_vehicles, max_congestion = self.simulate(n, edges, initial_vehicles, time_steps)
        # Check vehicle conservation over simulation
        self.assertEqual(sum(initial_vehicles), sum(final_vehicles))
        self.assertGreaterEqual(max_congestion, 0)

    def test_no_vehicles(self):
        n = 4
        edges = [(0, 1, 5), (1, 2, 5), (2, 3, 5)]
        initial_vehicles = [0, 0, 0, 0]
        time_steps = 3
        final_vehicles, max_congestion = self.simulate(n, edges, initial_vehicles, time_steps)
        self.assertEqual(final_vehicles, [0, 0, 0, 0])
        self.assertEqual(max_congestion, 0)

    def test_routing_limits(self):
        n = 3
        edges = [(0, 1, 3), (0, 2, 2)]
        initial_vehicles = [4, 0, 0]
        time_steps = 1
        allowed_edges = {(0, 1), (0, 2)}
        decision = routing_function(n, edges, initial_vehicles, 0)
        total_vehicles_routed = 0
        for (u, v), vehicles in decision.items():
            self.assertIn((u, v), allowed_edges, f"Edge {(u, v)} is not allowed.")
            self.assertIsInstance(vehicles, int, "Number of vehicles must be an integer.")
            self.assertGreaterEqual(vehicles, 0, "Number of vehicles must be non-negative.")
            total_vehicles_routed += vehicles
        self.assertLessEqual(total_vehicles_routed, initial_vehicles[0],
                             "Total vehicles routed exceed available vehicles.")

if __name__ == '__main__':
    unittest.main()