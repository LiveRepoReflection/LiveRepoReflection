import unittest
from supply_resilience import optimize_supply_chain

class TestOptimizeSupplyChain(unittest.TestCase):
    def setUp(self):
        # Sample supply chain graph with no disruptions (deterministic scenario)
        self.nodes = [
            {
                'id': 'A',
                'capacity': 100,
                'hardening_cost': 10,
                'disruption_probability': 0.0,
                'is_customer': False
            },
            {
                'id': 'B',
                'capacity': 50,
                'hardening_cost': 20,
                'disruption_probability': 0.0,
                'is_customer': False
            },
            {
                'id': 'C',
                'capacity': 30,
                'hardening_cost': 15,
                'disruption_probability': 0.0,
                'is_customer': False
            },
            {
                'id': 'D',
                'capacity': 100,
                'hardening_cost': 25,
                'disruption_probability': 0.0,
                'is_customer': True
            }
        ]
        self.edges = [
            {'source': 'A', 'target': 'B', 'capacity': 40},
            {'source': 'B', 'target': 'C', 'capacity': 30},
            {'source': 'C', 'target': 'D', 'capacity': 30},
            {'source': 'A', 'target': 'C', 'capacity': 20}
        ]
        self.budget = 50
        self.number_of_scenarios = 10

        self.graph_data = {
            'nodes': self.nodes,
            'edges': self.edges,
            'budget': self.budget,
            'number_of_scenarios': self.number_of_scenarios
        }

    def test_output_structure(self):
        """
        Test that the function returns a tuple with:
         - A set of facility ids (hardened facilities)
         - A set of redundant edges as 2-tuples (source_id, target_id)
         - A numeric expected minimum delivery value.
        """
        result = optimize_supply_chain(self.graph_data)
        self.assertIsInstance(result, tuple)
        self.assertEqual(len(result), 3)
        hardened, redundant, expected_delivery = result
        self.assertIsInstance(hardened, set)
        self.assertIsInstance(redundant, set)
        self.assertTrue(isinstance(expected_delivery, int) or isinstance(expected_delivery, float))

    def test_redundant_edges_validity(self):
        """
        Test that all redundant routes provided are valid, i.e. they exist as edges in the original graph.
        """
        result = optimize_supply_chain(self.graph_data)
        hardened, redundant, expected_delivery = result
        valid_edges = {(edge['source'], edge['target']) for edge in self.edges}
        for route in redundant:
            self.assertEqual(len(route), 2)
            self.assertIn(route, valid_edges)

    def test_expected_delivery_non_negative(self):
        """
        Test that the expected minimum delivery value is non-negative.
        """
        result = optimize_supply_chain(self.graph_data)
        hardened, redundant, expected_delivery = result
        self.assertGreaterEqual(expected_delivery, 0)

    def test_simulation_with_disruptions(self):
        """
        Test the algorithm using a graph with nonzero disruption probabilities and verify that:
         - Hardened facility ids are valid.
         - Expected delivery value respects an upper bound indicative of simulation.
        """
        nodes = [
            {
                'id': 'X',
                'capacity': 100,
                'hardening_cost': 10,
                'disruption_probability': 0.5,
                'is_customer': False
            },
            {
                'id': 'Y',
                'capacity': 80,
                'hardening_cost': 15,
                'disruption_probability': 0.2,
                'is_customer': False
            },
            {
                'id': 'Z',
                'capacity': 60,
                'hardening_cost': 20,
                'disruption_probability': 0.3,
                'is_customer': True
            }
        ]
        edges = [
            {'source': 'X', 'target': 'Y', 'capacity': 50},
            {'source': 'Y', 'target': 'Z', 'capacity': 40}
        ]
        budget = 30
        scenarios = 20
        graph_data = {
            'nodes': nodes,
            'edges': edges,
            'budget': budget,
            'number_of_scenarios': scenarios
        }
        result = optimize_supply_chain(graph_data)
        hardened, redundant, expected_delivery = result
        
        valid_ids = {node['id'] for node in nodes}
        for facility_id in hardened:
            self.assertIn(facility_id, valid_ids)
        
        # Since this simulation involves disruptions, we expect the delivery to be bounded.
        # For this simple network, the maximum possible delivery is limited by the edge capacities (e.g., 40 or below).
        self.assertGreaterEqual(expected_delivery, 0)
        self.assertLessEqual(expected_delivery, 90)

if __name__ == '__main__':
    unittest.main()