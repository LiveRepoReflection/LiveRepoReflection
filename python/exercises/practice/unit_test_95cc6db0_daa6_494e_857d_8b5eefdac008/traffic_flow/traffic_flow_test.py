import unittest
from traffic_flow import optimal_traffic_flow

class TestTrafficFlow(unittest.TestCase):
    def validate_flow(self, flow, N, edges, sources, destinations):
        # Create dictionaries for source demands and destination capacities
        source_dict = {node: demand for (node, demand) in sources}
        dest_dict = {node: cap for (node, cap) in destinations}

        # Initialize node balance (net inflow = incoming flow - outgoing flow)
        balance = {node: 0 for node in range(N)}

        # Check that each edge's flow does not exceed capacity and accumulate flows
        for (u, v, capacity, _) in edges:
            edge_key = (u, v)
            self.assertIn(edge_key, flow, msg=f"Missing flow for edge ({u}, {v})")
            f = flow[edge_key]
            self.assertIsInstance(f, int, msg=f"Flow on edge ({u}, {v}) must be integer")
            self.assertGreaterEqual(f, 0, msg=f"Flow on edge ({u}, {v}) is negative")
            self.assertLessEqual(f, capacity, msg=f"Flow on edge ({u}, {v}) exceeds its capacity")
            balance[u] -= f
            balance[v] += f

        # Verify flow conservation for all nodes based on their roles.
        for node in range(N):
            if node in source_dict:
                # For source, net inflow should be -demand
                self.assertEqual(balance[node], -source_dict[node],
                                 msg=f"Source node {node} balance {balance[node]} != -{source_dict[node]}")
            elif node in dest_dict:
                # For destination, net inflow should equal its capacity
                self.assertEqual(balance[node], dest_dict[node],
                                 msg=f"Destination node {node} balance {balance[node]} != {dest_dict[node]}")
            else:
                # Intermediate nodes should have zero net flow.
                self.assertEqual(balance[node], 0,
                                 msg=f"Intermediate node {node} balance {balance[node]} is not 0")

        # Total flow sent out by sources should equal sum of demands
        total_out = sum(-balance[node] for node in source_dict)
        total_demand = sum(source_dict.values())
        self.assertEqual(total_out, total_demand,
                         msg="Total outgoing flow from sources does not equal total demand")

    def test_single_source_single_destination(self):
        # Graph example from the problem description
        N = 4
        edges = [
            (0, 1, 10, 2),
            (0, 2, 5, 1),
            (1, 2, 15, 3),
            (1, 3, 7, 1),
            (2, 3, 8, 2)
        ]
        sources = [(0, 10)]
        destinations = [(3, 10)]
        flow = optimal_traffic_flow(N, edges, sources, destinations)
        self.validate_flow(flow, N, edges, sources, destinations)

    def test_multiple_sources_destinations(self):
        # Graph with two sources and two destinations
        N = 6
        edges = [
            (0, 2, 5, 2),
            (0, 3, 5, 1),
            (1, 2, 7, 4),
            (1, 3, 3, 2),
            (2, 4, 6, 1),
            (2, 5, 4, 2),
            (3, 4, 5, 3),
            (3, 5, 8, 1),
            (4, 5, 5, 2)
        ]
        sources = [(0, 5), (1, 7)]
        destinations = [(4, 6), (5, 6)]
        flow = optimal_traffic_flow(N, edges, sources, destinations)
        self.validate_flow(flow, N, edges, sources, destinations)

    def test_complex_case_with_cycle(self):
        # Graph with a cycle and alternative paths
        N = 5
        edges = [
            (0, 1, 4, 2),
            (0, 2, 6, 1),
            (1, 3, 4, 3),
            (2, 3, 4, 2),
            (3, 4, 8, 1),
            (1, 2, 2, 2)
        ]
        sources = [(0, 8)]
        destinations = [(4, 8)]
        flow = optimal_traffic_flow(N, edges, sources, destinations)
        self.validate_flow(flow, N, edges, sources, destinations)

    def test_exact_capacity_usage(self):
        # Test where each edge is used exactly at its capacity to route the demand.
        N = 4
        edges = [
            (0, 1, 3, 1),
            (0, 2, 2, 2),
            (1, 3, 3, 1),
            (2, 3, 2, 3)
        ]
        sources = [(0, 5)]
        destinations = [(3, 5)]
        flow = optimal_traffic_flow(N, edges, sources, destinations)
        self.validate_flow(flow, N, edges, sources, destinations)

if __name__ == "__main__":
    unittest.main()