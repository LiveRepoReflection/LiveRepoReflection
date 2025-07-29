import unittest
from flow_allocation import allocate_flow

class TestFlowAllocation(unittest.TestCase):

    def validate_allocation(self, num_nodes, edges, commodities, allocation):
        """
        Validates that the allocation satisfies:
        1. Edge capacity constraints.
        2. Flow conservation for each commodity:
            - At the source: net outflow equals demand.
            - At the destination: net inflow equals demand.
            - At intermediate nodes: net flow is zero.
        """
        # Build a mapping for edge capacity lookup: (u,v) -> capacity
        capacity_lookup = {}
        for (u, v, cap, cost) in edges:
            # There might be multiple edges between the same nodes.
            if (u, v) not in capacity_lookup:
                capacity_lookup[(u, v)] = cap
            else:
                capacity_lookup[(u, v)] += cap

        # Check edge capacities
        for edge, flows in allocation.items():
            total_flow = sum(flows.values())
            self.assertIn(edge, capacity_lookup, f"Edge {edge} not in capacity lookup.")
            self.assertLessEqual(total_flow, capacity_lookup[edge],
                                 f"Total flow {total_flow} on edge {edge} exceeds capacity {capacity_lookup[edge]}.")

        # For each commodity, compute net flow (outflow - inflow) per node.
        # allocation: { (u,v): {commodity_index: flow, ...}, ... }
        for idx, (src, dst, demand) in enumerate(commodities):
            net_flow = {node: 0 for node in range(num_nodes)}
            for (u, v), flows in allocation.items():
                flow = flows.get(idx, 0)
                net_flow[u] += flow
                net_flow[v] -= flow

            # At source, net flow should equal demand
            self.assertEqual(net_flow[src], demand,
                             f"Net flow at source node {src} for commodity {idx} should be {demand} but got {net_flow[src]}.")
            # At destination, net flow should equal -demand
            self.assertEqual(net_flow[dst], -demand,
                             f"Net flow at destination node {dst} for commodity {idx} should be {-demand} but got {net_flow[dst]}.")
            # At all other nodes, net flow should be 0
            for node in range(num_nodes):
                if node != src and node != dst:
                    self.assertEqual(net_flow[node], 0,
                                     f"Net flow at node {node} for commodity {idx} should be 0 but got {net_flow[node]}.")

    def test_feasible_allocation(self):
        # Sample test using a feasible network.
        num_nodes = 4
        edges = [
            (0, 1, 10, 1),  # (u, v, capacity, cost)
            (0, 2, 5, 2),
            (1, 2, 15, 1),
            (1, 3, 8, 3),
            (2, 3, 10, 1)
        ]
        commodities = [
            (0, 3, 7),  # Commodity 0: source, destination, demand
            (0, 3, 3)   # Commodity 1: source, destination, demand
        ]
        allocation = allocate_flow(num_nodes, edges, commodities)
        self.assertIsNotNone(allocation, "Allocation should not be None for a feasible network.")
        # Validate structure: Each edge should have a dictionary mapping commodity indices to flow values.
        for key, flows in allocation.items():
            self.assertIsInstance(key, tuple, "Edge keys must be tuples.")
            self.assertIsInstance(flows, dict, "Allocation values must be dictionaries.")
        
        # Validate capacity constraints and flow conservation for each commodity.
        self.validate_allocation(num_nodes, edges, commodities, allocation)

    def test_infeasible_allocation(self):
        # Test a network where demand exceeds available capacity on any path.
        num_nodes = 3
        edges = [
            (0, 1, 5, 1),
            (1, 2, 5, 1)
        ]
        # Demand is too high to be satisfied by the only available path.
        commodities = [
            (0, 2, 10)
        ]
        allocation = allocate_flow(num_nodes, edges, commodities)
        self.assertIsNone(allocation, "Allocation should be None when no feasible solution exists.")

    def test_multiple_paths_allocation(self):
        # A more complex scenario with multiple paths and cycles.
        num_nodes = 5
        edges = [
            (0, 1, 10, 2),
            (0, 2, 10, 2),
            (1, 3, 5, 3),
            (2, 3, 5, 3),
            (1, 2, 5, 1),  # additional edge creating cycle potential
            (3, 4, 10, 1),
            (2, 4, 5, 2)
        ]
        # Two commodities with different routes possible.
        commodities = [
            (0, 4, 8),
            (0, 4, 4)
        ]
        allocation = allocate_flow(num_nodes, edges, commodities)
        self.assertIsNotNone(allocation, "Allocation should not be None for a feasible network with multiple paths.")
        self.validate_allocation(num_nodes, edges, commodities, allocation)

    def test_edge_case_no_edges(self):
        # Test a scenario with nodes but no connecting edges.
        num_nodes = 3
        edges = []
        # Any commodity would be unsolvable if there are no edges.
        commodities = [
            (0, 2, 1)
        ]
        allocation = allocate_flow(num_nodes, edges, commodities)
        self.assertIsNone(allocation, "Allocation should be None when there are no edges connecting the nodes.")

if __name__ == '__main__':
    unittest.main()