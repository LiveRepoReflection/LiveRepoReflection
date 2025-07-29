import unittest
from supply_chain_flow import find_optimal_flow

class SupplyChainFlowTest(unittest.TestCase):
    def _node_information_request_factory(self, capacities, rates, edges):
        # Build a mapping from node id to its list of outgoing edges (v, weight)
        node_outgoing = {i: [] for i in range(len(capacities))}
        for (u, v, weight) in edges:
            node_outgoing[u].append((v, weight))
        
        def node_information_request(node_id):
            return {
                "capacity": capacities[node_id],
                "rate": rates[node_id],
                "outgoing_edges": node_outgoing.get(node_id, [])
            }
        return node_information_request

    def _check_flow_validity(self, n, rates, flow):
        # Check that for each node, the net flow (inflow - outflow) plus rate is zero,
        # and that every flow is non-negative.
        net_flow = [0] * n
        for (u, v, weight), amount in flow.items():
            self.assertGreaterEqual(amount, 0, f"Flow on edge {(u, v, weight)} is negative.")
            net_flow[u] -= amount
            net_flow[v] += amount
        for i in range(n):
            self.assertAlmostEqual(net_flow[i] + rates[i], 0, delta=1e-6,
                msg=f"Flow conservation violated at node {i}: Net flow {net_flow[i]} with rate {rates[i]}.")

    def test_simple_network(self):
        # Simple network with three nodes.
        n = 3
        capacities = [100, 100, 100]
        rates = [50, -25, -25]
        edges = [(0, 1, 1), (0, 2, 2), (1, 2, 1)]

        node_info = self._node_information_request_factory(capacities, rates, edges)
        flow = find_optimal_flow(n, capacities, rates, edges, node_info)
        self.assertIsInstance(flow, dict, "Expected output as a dictionary.")
        self.assertTrue(len(flow) > 0, "Expected a non-empty flow dictionary for a feasible network.")
        self._check_flow_validity(n, rates, flow)

    def test_multiple_edges(self):
        # Network with multiple edges between nodes and varied transportation costs.
        n = 4
        capacities = [200, 200, 200, 200]
        rates = [100, 0, -60, -40]
        edges = [
            (0, 1, 1),
            (0, 2, 4),
            (0, 1, 2),  # Second edge from 0 to 1 with a different cost.
            (1, 2, 1),
            (1, 3, 3),
            (2, 3, 1)
        ]
        node_info = self._node_information_request_factory(capacities, rates, edges)
        flow = find_optimal_flow(n, capacities, rates, edges, node_info)
        self.assertIsInstance(flow, dict, "Expected output as a dictionary.")
        self.assertTrue(len(flow) > 0, "Expected a non-empty flow dictionary for a feasible network.")
        self._check_flow_validity(n, rates, flow)

    def test_infeasible_network(self):
        # Infeasible network where production cannot be delivered (no edges available).
        n = 2
        capacities = [50, 50]
        rates = [100, -100]
        edges = []  # No transportation routes.
        node_info = self._node_information_request_factory(capacities, rates, edges)
        flow = find_optimal_flow(n, capacities, rates, edges, node_info)
        self.assertEqual(flow, {}, "Expected an empty dictionary for an infeasible network.")

    def test_zero_flow_network(self):
        # Network where all nodes have a zero production/consumption rate.
        n = 3
        capacities = [100, 100, 100]
        rates = [0, 0, 0]
        edges = [(0, 1, 5), (1, 2, 10)]
        node_info = self._node_information_request_factory(capacities, rates, edges)
        flow = find_optimal_flow(n, capacities, rates, edges, node_info)
        self.assertIsInstance(flow, dict, "Expected output as a dictionary.")
        # In a zero-flow network, every edge should carry zero flow.
        for flow_value in flow.values():
            self.assertAlmostEqual(flow_value, 0, delta=1e-6)
        self._check_flow_validity(n, rates, flow)

if __name__ == '__main__':
    unittest.main()