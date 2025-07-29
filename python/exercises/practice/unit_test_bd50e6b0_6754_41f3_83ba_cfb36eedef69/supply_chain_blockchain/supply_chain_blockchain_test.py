import unittest
from supply_chain_blockchain import optimize_supply_chain

class SupplyChainBlockchainTest(unittest.TestCase):
    def setUp(self):
        # Define a simple supply chain graph as a DAG.
        self.graph = {
            'nodes': {
                'supplier1': {'type': 'supplier', 'capacity': 100, 'products': ['componentA']},
                'factory1': {'type': 'factory', 'capacity': 50, 'products': ['final_product']},
                'distribution1': {'type': 'distribution', 'capacity': 150, 'products': []}
            },
            'edges': [
                {'source': 'supplier1', 'target': 'factory1', 'cost': 5, 'delay': 1},
                {'source': 'factory1', 'target': 'distribution1', 'cost': 10, 'delay': 1}
            ]
        }
        self.T = 3
        # Simple constant demand function.
        self.get_demand = lambda t: 20

        # Prepare a transaction log for capturing blockchain records.
        self.transaction_log = []
        def record_transaction(data):
            self.transaction_log.append(data)
        self.record_transaction = record_transaction

    def test_optimize_supply_chain_output_structure(self):
        # Test that the optimizer returns a tuple (schedule, total_cost)
        schedule, total_cost = optimize_supply_chain(
            self.graph,
            self.T,
            self.get_demand,
            self.record_transaction
        )
        self.assertIsInstance(schedule, dict)
        self.assertIsInstance(total_cost, (int, float))
        # Check that schedule contains entries for all nodes in the graph.
        for node in self.graph['nodes']:
            self.assertIn(node, schedule)
            # Each node's schedule should be a list with an activity record for each time period.
            self.assertIsInstance(schedule[node], list)
            self.assertEqual(len(schedule[node]), self.T)

    def test_capacity_constraints(self):
        # Test that the schedule respects the capacity constraints at each node.
        schedule, total_cost = optimize_supply_chain(
            self.graph,
            self.T,
            self.get_demand,
            self.record_transaction
        )
        for node, node_info in self.graph['nodes'].items():
            capacity = node_info['capacity']
            activities = schedule[node]
            for activity in activities:
                if node_info['type'] == 'supplier':
                    # Suppliers have an 'ordered' field.
                    ordered = activity.get('ordered', 0)
                    self.assertLessEqual(ordered, capacity)
                elif node_info['type'] == 'factory':
                    # Factories have a 'processed' field.
                    processed = activity.get('processed', 0)
                    self.assertLessEqual(processed, capacity)
                elif node_info['type'] == 'distribution':
                    # Distribution centers have a 'shipped' field.
                    shipped = activity.get('shipped', 0)
                    self.assertLessEqual(shipped, capacity)

    def test_record_transaction_calls(self):
        # Ensure that the record_transaction function is used during the optimization.
        self.transaction_log.clear()
        schedule, total_cost = optimize_supply_chain(
            self.graph,
            self.T,
            self.get_demand,
            self.record_transaction
        )
        # Expect at least one transaction to be recorded.
        self.assertTrue(len(self.transaction_log) > 0)
        # Each transaction should be a non-empty dictionary.
        for txn in self.transaction_log:
            self.assertIsInstance(txn, dict)
            self.assertTrue(txn)

    def test_unmet_demand_penalty(self):
        # Use a high demand function to force unmet demand penalties.
        high_demand = lambda t: 100
        schedule, total_cost = optimize_supply_chain(
            self.graph,
            self.T,
            high_demand,
            self.record_transaction
        )
        # With a high demand, the optimizer should incur penalties leading to a higher total cost.
        self.assertGreater(total_cost, 0)

if __name__ == '__main__':
    unittest.main()