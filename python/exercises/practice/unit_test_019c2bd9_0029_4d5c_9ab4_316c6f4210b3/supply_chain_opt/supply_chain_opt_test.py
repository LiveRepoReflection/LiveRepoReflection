import unittest
from supply_chain_opt import optimize_supply_chain

class TestSupplyChainOpt(unittest.TestCase):

    def check_solution(self, nodes, edges, flows):
        if flows is None:
            return

        # Create a dictionary for edge lookup
        edge_dict = {(edge['source'], edge['destination']): edge for edge in edges}
        for (src, dst), flow in flows.items():
            # Non-negativity and capacity constraints for each edge
            self.assertGreaterEqual(flow, 0, f"Flow on edge ({src}, {dst}) must be non-negative")
            self.assertLessEqual(flow, edge_dict[(src, dst)]['capacity'],
                                 f"Flow on edge ({src}, {dst}) exceeds its capacity")
        
        # Compute inflows and outflows for each node
        inflows = {node['id']: 0 for node in nodes}
        outflows = {node['id']: 0 for node in nodes}
        for (src, dst), flow in flows.items():
            outflows[src] += flow
            inflows[dst] += flow

        # Validate node constraints
        for node in nodes:
            node_id = node['id']
            if node['type'] == 'factory':
                production_capacity = node['production_capacity']
                self.assertLessEqual(outflows[node_id], production_capacity,
                                     f"Factory {node_id} production exceeded")
            elif node['type'] == 'warehouse':
                storage_capacity = node['storage_capacity']
                # Flow conservation: inflow == outflow
                self.assertAlmostEqual(inflows[node_id], outflows[node_id],
                                       msg=f"Warehouse {node_id} does not satisfy flow conservation")
                # Storage capacity constraint
                self.assertLessEqual(inflows[node_id], storage_capacity,
                                     f"Warehouse {node_id} storage exceeded")
            elif node['type'] == 'distribution_center':
                demand = node['demand']
                self.assertAlmostEqual(inflows[node_id], demand,
                                       msg=f"Distribution center {node_id} demand not met")

    def test_simple_feasible(self):
        nodes = [
            {'id': 'F1', 'type': 'factory', 'production_capacity': 100},
            {'id': 'D1', 'type': 'distribution_center', 'demand': 80}
        ]
        edges = [
            {'source': 'F1', 'destination': 'D1', 'capacity': 100, 'cost_per_unit': 1}
        ]
        flows = optimize_supply_chain(nodes, edges)
        self.assertIsNotNone(flows, "Expected a feasible solution for a simple supply chain")
        self.check_solution(nodes, edges, flows)

    def test_infeasible_demand(self):
        nodes = [
            {'id': 'F1', 'type': 'factory', 'production_capacity': 50},
            {'id': 'D1', 'type': 'distribution_center', 'demand': 80}
        ]
        edges = [
            {'source': 'F1', 'destination': 'D1', 'capacity': 100, 'cost_per_unit': 1}
        ]
        flows = optimize_supply_chain(nodes, edges)
        self.assertIsNone(flows, "Expected no solution when the factory cannot meet the demand")

    def test_warehouse_flow_conservation(self):
        nodes = [
            {'id': 'F1', 'type': 'factory', 'production_capacity': 100},
            {'id': 'W1', 'type': 'warehouse', 'storage_capacity': 70},
            {'id': 'D1', 'type': 'distribution_center', 'demand': 70}
        ]
        edges = [
            {'source': 'F1', 'destination': 'W1', 'capacity': 90, 'cost_per_unit': 2},
            {'source': 'F1', 'destination': 'D1', 'capacity': 30, 'cost_per_unit': 5},
            {'source': 'W1', 'destination': 'D1', 'capacity': 70, 'cost_per_unit': 1}
        ]
        flows = optimize_supply_chain(nodes, edges)
        self.assertIsNotNone(flows, "Expected a feasible solution with a warehouse in the network")
        self.check_solution(nodes, edges, flows)

    def test_complex_network(self):
        nodes = [
            {'id': 'F1', 'type': 'factory', 'production_capacity': 100},
            {'id': 'F2', 'type': 'factory', 'production_capacity': 80},
            {'id': 'W1', 'type': 'warehouse', 'storage_capacity': 90},
            {'id': 'W2', 'type': 'warehouse', 'storage_capacity': 70},
            {'id': 'D1', 'type': 'distribution_center', 'demand': 80},
            {'id': 'D2', 'type': 'distribution_center', 'demand': 70},
        ]
        edges = [
            {'source': 'F1', 'destination': 'W1', 'capacity': 60, 'cost_per_unit': 3},
            {'source': 'F1', 'destination': 'D1', 'capacity': 50, 'cost_per_unit': 6},
            {'source': 'F2', 'destination': 'W1', 'capacity': 50, 'cost_per_unit': 4},
            {'source': 'F2', 'destination': 'W2', 'capacity': 40, 'cost_per_unit': 2},
            {'source': 'W1', 'destination': 'D1', 'capacity': 60, 'cost_per_unit': 1},
            {'source': 'W1', 'destination': 'D2', 'capacity': 40, 'cost_per_unit': 2},
            {'source': 'W2', 'destination': 'D2', 'capacity': 70, 'cost_per_unit': 3},
        ]
        flows = optimize_supply_chain(nodes, edges)
        self.assertIsNotNone(flows, "Expected a feasible solution for a complex network")
        self.check_solution(nodes, edges, flows)

    def test_disconnected_graph(self):
        nodes = [
            {'id': 'F1', 'type': 'factory', 'production_capacity': 100},
            {'id': 'D1', 'type': 'distribution_center', 'demand': 80},
            {'id': 'W1', 'type': 'warehouse', 'storage_capacity': 50},
        ]
        edges = [
            {'source': 'F1', 'destination': 'W1', 'capacity': 60, 'cost_per_unit': 2},
            # No edge from W1 to D1, thus disconnecting the factory from meeting demand
        ]
        flows = optimize_supply_chain(nodes, edges)
        self.assertIsNone(flows, "Expected no solution for a disconnected supply chain network")

if __name__ == '__main__':
    unittest.main()