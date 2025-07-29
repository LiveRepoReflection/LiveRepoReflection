import unittest
from flow_optimizer import optimize_multi_commodity_flow


class TestFlowOptimizer(unittest.TestCase):

    def test_simple_example(self):
        # Simple example from the problem description
        nodes = ['A', 'B']
        edges = {
            'A': [('B', [(0, 1), (20, 2)])],
            'B': []
        }
        commodities = [('A', 'B', 10)]
        
        result = optimize_multi_commodity_flow(nodes, edges, commodities)
        
        # Check if the result is a dictionary
        self.assertIsInstance(result, dict)
        
        # Check if the keys are commodity indices
        self.assertTrue(all(isinstance(k, int) for k in result))
        
        # Check if each commodity has a flow assignment
        for k in range(len(commodities)):
            self.assertIn(k, result)
            self.assertIsInstance(result[k], dict)
        
        # Check the specific flow for the example
        self.assertIn(('A', 'B'), result[0])
        self.assertEqual(result[0][('A', 'B')], 10)
        
        # Check that the flow satisfies the demand
        total_flow = sum(flow for edge, flow in result[0].items() if edge[0] == 'A')
        self.assertEqual(total_flow, 10)
        
        # The expected cost should be 15
        # Cost function is 1 + (10-0)*(2-1)/(20-0) = 1.5 per unit
        # Total cost = 10 * 1.5 = 15
        total_cost = 0
        for k, flows in result.items():
            for edge, flow in flows.items():
                if flow > 0:
                    from_node, to_node = edge
                    cost_function = next((cf for n, cf in edges[from_node] if n == to_node), None)
                    
                    # Calculate the cost for this edge
                    total_edge_flow = sum(result[i].get(edge, 0) for i in range(len(commodities)))
                    cost_per_unit = self._calculate_cost(total_edge_flow, cost_function)
                    total_cost += flow * cost_per_unit
        
        self.assertAlmostEqual(total_cost, 15, places=2)

    def test_multi_commodity_network(self):
        # More complex example with multiple commodities
        nodes = ['A', 'B', 'C', 'D']
        edges = {
            'A': [('B', [(0, 1), (10, 2), (20, 4)]), ('C', [(0, 2), (15, 3)])],
            'B': [('C', [(0, 1), (10, 2)]), ('D', [(0, 3), (10, 5)])],
            'C': [('D', [(0, 1), (10, 2), (20, 3)])],
            'D': []
        }
        commodities = [
            ('A', 'D', 5),  # Commodity 0
            ('B', 'D', 8)   # Commodity 1
        ]
        
        result = optimize_multi_commodity_flow(nodes, edges, commodities)
        
        # Check if the result is a dictionary
        self.assertIsInstance(result, dict)
        
        # Check if the keys are commodity indices
        self.assertTrue(all(isinstance(k, int) for k in result))
        
        # Check if each commodity has a flow assignment
        for k in range(len(commodities)):
            self.assertIn(k, result)
            self.assertIsInstance(result[k], dict)
        
        # Verify flow conservation for each commodity at each node
        for k, commodity_flow in result.items():
            source, dest, demand = commodities[k]
            
            # Check source outflow
            source_outflow = sum(flow for (src, dst), flow in commodity_flow.items() if src == source)
            self.assertEqual(source_outflow, demand)
            
            # Check destination inflow
            dest_inflow = sum(flow for (src, dst), flow in commodity_flow.items() if dst == dest)
            self.assertEqual(dest_inflow, demand)
            
            # Check flow conservation at intermediate nodes
            for node in nodes:
                if node != source and node != dest:
                    inflow = sum(flow for (src, dst), flow in commodity_flow.items() if dst == node)
                    outflow = sum(flow for (src, dst), flow in commodity_flow.items() if src == node)
                    self.assertEqual(inflow, outflow)
        
        # Calculate total cost and verify it's reasonable
        total_cost = 0
        for k, flows in result.items():
            for edge, flow in flows.items():
                if flow > 0:
                    from_node, to_node = edge
                    cost_function = next((cf for n, cf in edges[from_node] if n == to_node), None)
                    
                    # Calculate the cost for this edge
                    total_edge_flow = sum(result[i].get(edge, 0) for i in range(len(commodities)))
                    cost_per_unit = self._calculate_cost(total_edge_flow, cost_function)
                    total_cost += flow * cost_per_unit
        
        # Just check that cost is positive since we don't know the optimal cost for this example
        self.assertGreater(total_cost, 0)
    
    def test_congested_network(self):
        # Test with a network where edges become expensive as flow increases
        nodes = ['A', 'B', 'C', 'D']
        edges = {
            'A': [('B', [(0, 1), (5, 3), (10, 10)]), ('C', [(0, 2), (10, 3)])],
            'B': [('D', [(0, 1), (5, 5), (10, 15)])],
            'C': [('D', [(0, 2), (10, 4)])],
            'D': []
        }
        commodities = [('A', 'D', 10)]
        
        result = optimize_multi_commodity_flow(nodes, edges, commodities)
        
        # Check if we get a valid solution
        self.assertIsInstance(result, dict)
        self.assertIn(0, result)
        
        # Calculate the total flow on each edge
        edge_flows = {}
        for k, flows in result.items():
            for edge, flow in flows.items():
                if edge not in edge_flows:
                    edge_flows[edge] = 0
                edge_flows[edge] += flow
        
        # Check if the flow is properly distributed to avoid congestion
        # The optimal solution should split the flow between A->B->D and A->C->D
        # to minimize cost due to the congestion effects
        for edge, flow in edge_flows.items():
            # No edge should have more than 10 units of flow (the total demand)
            self.assertLessEqual(flow, 10)
        
        # Verify the total demand is satisfied
        total_outflow_from_A = sum(flow for (src, dst), flow in edge_flows.items() if src == 'A')
        total_inflow_to_D = sum(flow for (src, dst), flow in edge_flows.items() if dst == 'D')
        self.assertEqual(total_outflow_from_A, 10)
        self.assertEqual(total_inflow_to_D, 10)
    
    def test_multi_source_destination(self):
        # Test with multiple sources and destinations
        nodes = ['A', 'B', 'C', 'D', 'E']
        edges = {
            'A': [('B', [(0, 1), (10, 2)]), ('C', [(0, 1), (10, 3)])],
            'B': [('D', [(0, 1), (10, 2)]), ('E', [(0, 2), (10, 3)])],
            'C': [('D', [(0, 2), (10, 3)]), ('E', [(0, 1), (10, 2)])],
            'D': [],
            'E': []
        }
        commodities = [
            ('A', 'D', 5),  # Commodity 0
            ('A', 'E', 5),  # Commodity 1
            ('B', 'E', 3)   # Commodity 2
        ]
        
        result = optimize_multi_commodity_flow(nodes, edges, commodities)
        
        # Check if we get a valid solution
        self.assertIsInstance(result, dict)
        self.assertEqual(len(result), 3)
        
        # Verify all demands are satisfied
        for k, (source, dest, demand) in enumerate(commodities):
            outflow = sum(flow for (src, dst), flow in result[k].items() if src == source)
            inflow = sum(flow for (src, dst), flow in result[k].items() if dst == dest)
            self.assertEqual(outflow, demand)
            self.assertEqual(inflow, demand)
        
        # Verify flow conservation at all nodes
        for k, flows in result.items():
            source, dest, _ = commodities[k]
            for node in nodes:
                if node != source and node != dest:
                    inflow = sum(flow for (src, dst), flow in flows.items() if dst == node)
                    outflow = sum(flow for (src, dst), flow in flows.items() if src == node)
                    self.assertEqual(inflow, outflow)
    
    def test_no_feasible_solution(self):
        # Test with a graph where there's no path from source to destination
        nodes = ['A', 'B', 'C', 'D']
        edges = {
            'A': [('B', [(0, 1), (10, 2)])],
            'B': [('C', [(0, 1), (10, 2)])],
            'C': [],
            'D': []
        }
        commodities = [('A', 'D', 5)]
        
        # This should either return an empty dictionary or raise a specific exception
        try:
            result = optimize_multi_commodity_flow(nodes, edges, commodities)
            # If it returns a result, it should indicate no flow is possible
            self.assertTrue(all(sum(flow for edge, flow in flows.items()) == 0 
                               for k, flows in result.items()))
        except Exception as e:
            # It's also acceptable to raise an exception for infeasible problems
            self.assertIn("infeasible", str(e).lower())
    
    def test_large_network(self):
        # Test performance with a larger network
        n_nodes = 50
        nodes = [f'N{i}' for i in range(n_nodes)]
        
        # Create a grid-like network
        edges = {node: [] for node in nodes}
        for i in range(n_nodes - 1):
            # Connect to the next node with a basic cost function
            edges[f'N{i}'].append((f'N{i+1}', [(0, 1), (10, 2)]))
            
            # Add some cross-connections for every 5 nodes
            if i % 5 != 0 and i + 5 < n_nodes:
                edges[f'N{i}'].append((f'N{i+5}', [(0, 2), (10, 3)]))
        
        # Define commodities with different source-destination pairs
        commodities = [
            (f'N{0}', f'N{n_nodes-1}', 10),  # Long path commodity
            (f'N{10}', f'N{20}', 5),         # Medium path commodity
            (f'N{30}', f'N{35}', 8)          # Short path commodity
        ]
        
        # Check if the algorithm can handle larger networks in reasonable time
        import time
        start_time = time.time()
        result = optimize_multi_commodity_flow(nodes, edges, commodities)
        end_time = time.time()
        
        # Check if we get a valid solution
        self.assertIsInstance(result, dict)
        self.assertEqual(len(result), 3)
        
        # Verify all demands are satisfied
        for k, (source, dest, demand) in enumerate(commodities):
            outflow = sum(flow for (src, dst), flow in result[k].items() if src == source)
            inflow = sum(flow for (src, dst), flow in result[k].items() if dst == dest)
            self.assertEqual(outflow, demand)
            self.assertEqual(inflow, demand)
        
        # The execution time should be reasonable (adjust as needed)
        execution_time = end_time - start_time
        print(f"Large network execution time: {execution_time:.2f} seconds")
        self.assertLess(execution_time, 30)  # Should complete within 30 seconds
    
    def _calculate_cost(self, flow, cost_function):
        """Helper method to calculate cost based on piecewise linear function"""
        if flow <= 0:
            return cost_function[0][1]
        
        for i in range(len(cost_function) - 1):
            flow1, cost1 = cost_function[i]
            flow2, cost2 = cost_function[i + 1]
            
            if flow1 <= flow <= flow2:
                # Linear interpolation
                return cost1 + (flow - flow1) * (cost2 - cost1) / (flow2 - flow1)
        
        # If flow exceeds the maximum defined point, use the last cost
        return cost_function[-1][1]


if __name__ == '__main__':
    unittest.main()