import unittest
from supply_chain_resilience import optimize_supply_chain

class TestSupplyChainResilience(unittest.TestCase):
    def test_basic_case(self):
        graph = {
            "A": {"B": (10, 0.1), "C": (5, 0.2)},
            "B": {"D": (7, 0.05)},
            "C": {"D": (8, 0.15)},
            "D": {}
        }
        node_capacities = {"A": 15, "B": 8, "C": 10, "D": 20}
        source = "A"
        destination = "D"
        required_throughput = 12
        confidence_level = 0.95

        def node_upgrade_cost(node, additional_capacity):
            return additional_capacity * 10

        result = optimize_supply_chain(graph, node_capacities, source, destination,
                                     required_throughput, confidence_level, node_upgrade_cost)
        self.assertIsInstance(result, dict)
        self.assertTrue(all(isinstance(k, str) and isinstance(v, int) for k, v in result.items()))

    def test_no_upgrade_needed(self):
        graph = {
            "A": {"B": (20, 0.05)},
            "B": {"C": (20, 0.05)},
            "C": {}
        }
        node_capacities = {"A": 20, "B": 20, "C": 20}
        source = "A"
        destination = "C"
        required_throughput = 15
        confidence_level = 0.95

        def node_upgrade_cost(node, additional_capacity):
            return additional_capacity * 10

        result = optimize_supply_chain(graph, node_capacities, source, destination,
                                     required_throughput, confidence_level, node_upgrade_cost)
        self.assertEqual(result, {})

    def test_impossible_case(self):
        graph = {
            "A": {"B": (5, 0.5)},
            "B": {"C": (5, 0.5)},
            "C": {}
        }
        node_capacities = {"A": 5, "B": 5, "C": 5}
        source = "A"
        destination = "C"
        required_throughput = 10
        confidence_level = 0.95

        def node_upgrade_cost(node, additional_capacity):
            return additional_capacity * 10

        result = optimize_supply_chain(graph, node_capacities, source, destination,
                                     required_throughput, confidence_level, node_upgrade_cost)
        self.assertEqual(result, {})

    def test_multiple_paths(self):
        graph = {
            "A": {"B": (10, 0.1), "C": (10, 0.2)},
            "B": {"D": (8, 0.05)},
            "C": {"D": (8, 0.15)},
            "D": {"E": (15, 0.1)},
            "E": {}
        }
        node_capacities = {"A": 20, "B": 10, "C": 10, "D": 15, "E": 15}
        source = "A"
        destination = "E"
        required_throughput = 12
        confidence_level = 0.95

        def node_upgrade_cost(node, additional_capacity):
            return additional_capacity * 10

        result = optimize_supply_chain(graph, node_capacities, source, destination,
                                     required_throughput, confidence_level, node_upgrade_cost)
        self.assertIsInstance(result, dict)
        self.assertTrue(all(isinstance(k, str) and isinstance(v, int) for k, v in result.items()))

    def test_high_reliability_requirement(self):
        graph = {
            "A": {"B": (10, 0.3), "C": (10, 0.1)},
            "B": {"D": (8, 0.2)},
            "C": {"D": (8, 0.05)},
            "D": {}
        }
        node_capacities = {"A": 20, "B": 10, "C": 10, "D": 15}
        source = "A"
        destination = "D"
        required_throughput = 15
        confidence_level = 0.99

        def node_upgrade_cost(node, additional_capacity):
            return additional_capacity * 10

        result = optimize_supply_chain(graph, node_capacities, source, destination,
                                     required_throughput, confidence_level, node_upgrade_cost)
        self.assertIsInstance(result, dict)
        self.assertTrue(all(isinstance(k, str) and isinstance(v, int) for k, v in result.items()))

    def test_invalid_inputs(self):
        graph = {
            "A": {"B": (10, 0.1)},
            "B": {}
        }
        node_capacities = {"A": 10, "B": 10}
        source = "A"
        destination = "B"
        required_throughput = 15
        confidence_level = 1.1  # Invalid confidence level

        def node_upgrade_cost(node, additional_capacity):
            return additional_capacity * 10

        with self.assertRaises(ValueError):
            optimize_supply_chain(graph, node_capacities, source, destination,
                                required_throughput, confidence_level, node_upgrade_cost)

        with self.assertRaises(ValueError):
            optimize_supply_chain(graph, node_capacities, source, destination,
                                -5, 0.95, node_upgrade_cost)

    def test_single_node_network(self):
        graph = {
            "A": {}
        }
        node_capacities = {"A": 10}
        source = "A"
        destination = "A"
        required_throughput = 5
        confidence_level = 0.95

        def node_upgrade_cost(node, additional_capacity):
            return additional_capacity * 10

        result = optimize_supply_chain(graph, node_capacities, source, destination,
                                     required_throughput, confidence_level, node_upgrade_cost)
        self.assertEqual(result, {})

if __name__ == '__main__':
    unittest.main()