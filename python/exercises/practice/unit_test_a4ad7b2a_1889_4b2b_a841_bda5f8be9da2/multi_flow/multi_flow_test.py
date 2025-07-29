import unittest
from multi_flow import multi_flow

def verify_solution(solution, num_nodes, edges, commodities):
    # Create a dictionary for capacities: key: (u, v) -> capacity
    capacity_dict = {}
    for u, v, capacity, cost in edges:
        if (u, v) in capacity_dict:
            capacity_dict[(u, v)] += capacity
        else:
            capacity_dict[(u, v)] = capacity

    # Check capacity constraints for each edge.
    for (u, v), flow_dict in solution.items():
        total_flow = sum(flow_dict.get(i, 0) for i in range(len(commodities)))
        if total_flow > capacity_dict.get((u, v), 0):
            return False

    # For each commodity, check flow conservation constraints.
    # For commodity i: at source, outflow - inflow should equal demand;
    # at target, outflow - inflow should equal -demand; elsewhere, it should be 0.
    for idx, (source, sink, demand) in enumerate(commodities):
        flow_balance = [0] * num_nodes
        for (u, v), flow_dict in solution.items():
            flow = flow_dict.get(idx, 0)
            flow_balance[u] += flow
            flow_balance[v] -= flow
        for node in range(num_nodes):
            if node == source and flow_balance[node] != demand:
                return False
            elif node == sink and flow_balance[node] != -demand:
                return False
            elif node != source and node != sink and flow_balance[node] != 0:
                return False
    return True

class TestMultiFlow(unittest.TestCase):
    def test_single_commodity_feasible(self):
        num_nodes = 4
        edges = [
            (0, 1, 10, 1),
            (0, 2, 5, 2),
            (1, 2, 15, 1),
            (1, 3, 7, 3),
            (2, 3, 12, 1)
        ]
        commodities = [
            (0, 3, 8)
        ]
        result = multi_flow(num_nodes, edges, commodities)
        self.assertIsNotNone(result, "Expected a feasible solution for single commodity.")
        self.assertTrue(verify_solution(result, num_nodes, edges, commodities),
                        "Solution does not satisfy capacity or flow conservation constraints.")

    def test_multiple_commodities_feasible(self):
        num_nodes = 3
        edges = [
            (0, 1, 5, 2),
            (1, 2, 5, 2),
            (0, 2, 3, 3)
        ]
        # Two commodities: commodity 0 and commodity 1, both from 0 to 2.
        commodities = [
            (0, 2, 5),
            (0, 2, 2)
        ]
        result = multi_flow(num_nodes, edges, commodities)
        self.assertIsNotNone(result, "Expected a feasible solution for multiple commodities.")
        self.assertTrue(verify_solution(result, num_nodes, edges, commodities),
                        "Solution does not satisfy capacity or flow conservation constraints.")

    def test_infeasible_due_to_capacity(self):
        num_nodes = 2
        edges = [
            (0, 1, 3, 1)
        ]
        # Infeasible commodity: demand exceeds edge capacity.
        commodities = [
            (0, 1, 5)
        ]
        result = multi_flow(num_nodes, edges, commodities)
        self.assertIsNone(result, "Expected no feasible solution when demand exceeds capacity.")

    def test_cycle_graph(self):
        # Graph with cycle.
        num_nodes = 4
        edges = [
            (0, 1, 10, 2),
            (1, 2, 10, 2),
            (2, 0, 10, 2),
            (1, 3, 5, 3),
            (2, 3, 5, 1)
        ]
        commodities = [
            (0, 3, 4)
        ]
        result = multi_flow(num_nodes, edges, commodities)
        self.assertIsNotNone(result, "Expected a feasible solution in a cyclic graph.")
        self.assertTrue(verify_solution(result, num_nodes, edges, commodities),
                        "Solution in cyclic graph does not satisfy capacity or flow conservation.")

    def test_multiple_paths(self):
        # Graph with multiple available paths for commodities.
        num_nodes = 5
        edges = [
            (0, 1, 5, 1),
            (1, 4, 5, 1),
            (0, 2, 5, 2),
            (2, 4, 5, 2),
            (0, 3, 5, 3),
            (3, 4, 5, 3)
        ]
        # Two commodities going from 0 to 4 with moderate demand.
        commodities = [
            (0, 4, 4),
            (0, 4, 4)
        ]
        result = multi_flow(num_nodes, edges, commodities)
        self.assertIsNotNone(result, "Expected a feasible solution for multiple paths scenario.")
        self.assertTrue(verify_solution(result, num_nodes, edges, commodities),
                        "Solution does not satisfy capacity or flow conservation in multiple paths case.")

if __name__ == '__main__':
    unittest.main()