import unittest
from flow_allocator import allocate_flow

class FlowAllocatorTest(unittest.TestCase):

    def verify_allocation(self, nodes, commodities, edges, T, capacity_func, allocation):
        # For each commodity, verify that the flow allocation meets the demand and flow conservation constraints.
        for idx, (source, destination, demand) in enumerate(commodities):
            commodity_alloc = allocation.get(idx, {})
            # Sum of flows leaving the source should equal the demand.
            source_outflow = sum(flow for (u, v, time), flow in commodity_alloc.items() if u == source)
            self.assertAlmostEqual(source_outflow, demand, msg=f"Commodity {idx}: Total outflow from source {source} does not equal demand.")

            # Sum of flows arriving at the destination should equal the demand.
            destination_inflow = sum(flow for (u, v, time), flow in commodity_alloc.items() if v == destination)
            self.assertAlmostEqual(destination_inflow, demand, msg=f"Commodity {idx}: Total inflow to destination {destination} does not equal demand.")

            # For nodes other than source and destination, ensure flow conservation at each time step.
            for time in range(T):
                for node in nodes:
                    if node == source or node == destination:
                        continue
                    inflow = sum(flow for (u, v, ts), flow in commodity_alloc.items() if v == node and ts == time)
                    outflow = sum(flow for (u, v, ts), flow in commodity_alloc.items() if u == node and ts == time)
                    self.assertAlmostEqual(inflow, outflow, msg=f"Commodity {idx}: Flow conservation violated at node {node} at time {time}.")

        # Check capacity constraints on every edge at every time step.
        for (u, v) in edges:
            for time in range(T):
                total_flow = sum(allocation.get(idx, {}).get((u, v, time), 0) for idx in range(len(commodities)))
                cap = capacity_func(u, v, time)
                self.assertLessEqual(total_flow, cap, msg=f"Capacity exceeded on edge ({u}, {v}) at time {time}.")

    def test_single_commodity_time_one(self):
        # Simple network with one commodity and a single time step.
        nodes = [1, 2, 3, 4]
        commodities = [(1, 4, 10)]
        edges = [(1, 2), (1, 3), (2, 4), (3, 4)]
        T = 1

        def capacity(start_node, end_node, time):
            return 10  # Sufficient capacity on all edges.

        def cost(start_node, end_node, time, flow):
            return flow  # Linear cost per unit flow.

        allocation = allocate_flow(nodes, commodities, edges, T, capacity, cost)
        self.assertIsInstance(allocation, dict)
        self.verify_allocation(nodes, commodities, edges, T, capacity, allocation)

    def test_multiple_commodities_multiple_time_steps(self):
        # Network with multiple commodities and two time steps.
        nodes = [1, 2, 3, 4, 5]
        commodities = [
            (1, 5, 8),
            (2, 4, 5)
        ]
        edges = [(1, 2), (1, 3), (2, 5), (3, 5), (2, 4), (3, 4)]
        T = 2

        def capacity(start_node, end_node, time):
            if (start_node, end_node) in [(1, 2), (1, 3)]:
                return 5 + time  # Increasing capacity at later time.
            elif (start_node, end_node) in [(2, 5), (3, 5)]:
                return 6
            elif (start_node, end_node) in [(2, 4), (3, 4)]:
                return 4
            else:
                return 0

        def cost(start_node, end_node, time, flow):
            return (time + 1) * flow  # Cost increases with time.

        allocation = allocate_flow(nodes, commodities, edges, T, capacity, cost)
        self.assertIsInstance(allocation, dict)
        self.verify_allocation(nodes, commodities, edges, T, capacity, allocation)

    def test_no_feasible_solution(self):
        # Create a network where the available capacity is insufficient to meet the demand.
        nodes = [1, 2, 3]
        commodities = [(1, 3, 10)]
        edges = [(1, 2), (2, 3)]
        T = 1

        def capacity(start_node, end_node, time):
            return 5  # Capacity too low for the demand.

        def cost(start_node, end_node, time, flow):
            return flow

        with self.assertRaises(ValueError) as context:
            allocate_flow(nodes, commodities, edges, T, capacity, cost)
        self.assertEqual(str(context.exception), "No feasible solution found")

    def test_empty_commodities(self):
        # If the commodities list is empty, expect an empty allocation dictionary.
        nodes = [1, 2, 3]
        commodities = []
        edges = [(1, 2), (2, 3)]
        T = 1

        def capacity(start_node, end_node, time):
            return 10

        def cost(start_node, end_node, time, flow):
            return flow

        allocation = allocate_flow(nodes, commodities, edges, T, capacity, cost)
        self.assertEqual(allocation, {})

    def test_empty_nodes_or_edges(self):
        # With empty nodes or edges, and a provided commodity, no feasible solution exists.
        nodes = []
        commodities = [(1, 2, 5)]
        edges = []
        T = 1

        def capacity(start_node, end_node, time):
            return 0

        def cost(start_node, end_node, time, flow):
            return flow

        with self.assertRaises(ValueError) as context:
            allocate_flow(nodes, commodities, edges, T, capacity, cost)
        self.assertEqual(str(context.exception), "No feasible solution found")

if __name__ == '__main__':
    unittest.main()