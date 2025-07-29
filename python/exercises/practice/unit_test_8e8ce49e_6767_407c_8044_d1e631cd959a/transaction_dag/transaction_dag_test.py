import unittest
from transaction_dag import optimize_transaction_order


class TestTransactionDag(unittest.TestCase):
    def test_empty_dag(self):
        """Test with an empty DAG."""
        adjacency_list = {}
        node_properties = {}
        expected = []
        self.assertEqual(optimize_transaction_order(adjacency_list, node_properties), expected)

    def test_single_node(self):
        """Test with a DAG containing a single node."""
        adjacency_list = {0: []}
        node_properties = {
            0: {"service_id": 1, "success_probability": 0.9, "operation_cost": 10, "rollback_cost": 5}
        }
        expected = [0]
        self.assertEqual(optimize_transaction_order(adjacency_list, node_properties), expected)

    def test_linear_dag(self):
        """Test with a linear DAG (0 -> 1 -> 2)."""
        adjacency_list = {0: [1], 1: [2], 2: []}
        node_properties = {
            0: {"service_id": 1, "success_probability": 0.9, "operation_cost": 10, "rollback_cost": 5},
            1: {"service_id": 2, "success_probability": 0.8, "operation_cost": 15, "rollback_cost": 8},
            2: {"service_id": 3, "success_probability": 0.7, "operation_cost": 20, "rollback_cost": 10}
        }
        result = optimize_transaction_order(adjacency_list, node_properties)
        # The result should be a valid topological sort
        self.assertEqual(len(result), 3)
        self.assertIn(0, result)
        self.assertIn(1, result)
        self.assertIn(2, result)
        self.assertTrue(result.index(0) < result.index(1))
        self.assertTrue(result.index(1) < result.index(2))

    def test_diamond_dag(self):
        """Test with a diamond-shaped DAG (0 -> 1,2 -> 3)."""
        adjacency_list = {0: [1, 2], 1: [3], 2: [3], 3: []}
        node_properties = {
            0: {"service_id": 1, "success_probability": 0.9, "operation_cost": 10, "rollback_cost": 5},
            1: {"service_id": 2, "success_probability": 0.8, "operation_cost": 15, "rollback_cost": 8},
            2: {"service_id": 3, "success_probability": 0.7, "operation_cost": 20, "rollback_cost": 10},
            3: {"service_id": 4, "success_probability": 0.6, "operation_cost": 25, "rollback_cost": 12}
        }
        result = optimize_transaction_order(adjacency_list, node_properties)
        # The result should be a valid topological sort
        self.assertEqual(len(result), 4)
        self.assertIn(0, result)
        self.assertIn(1, result)
        self.assertIn(2, result)
        self.assertIn(3, result)
        self.assertTrue(result.index(0) < result.index(1))
        self.assertTrue(result.index(0) < result.index(2))
        self.assertTrue(result.index(1) < result.index(3))
        self.assertTrue(result.index(2) < result.index(3))

    def test_complex_dag(self):
        """Test with a more complex DAG with multiple source and sink nodes."""
        adjacency_list = {0: [2], 1: [2, 3], 2: [4], 3: [5], 4: [5, 6], 5: [], 6: []}
        node_properties = {
            0: {"service_id": 1, "success_probability": 0.9, "operation_cost": 10, "rollback_cost": 5},
            1: {"service_id": 2, "success_probability": 0.8, "operation_cost": 15, "rollback_cost": 8},
            2: {"service_id": 3, "success_probability": 0.7, "operation_cost": 20, "rollback_cost": 10},
            3: {"service_id": 4, "success_probability": 0.6, "operation_cost": 25, "rollback_cost": 12},
            4: {"service_id": 5, "success_probability": 0.5, "operation_cost": 30, "rollback_cost": 15},
            5: {"service_id": 6, "success_probability": 0.4, "operation_cost": 35, "rollback_cost": 18},
            6: {"service_id": 7, "success_probability": 0.3, "operation_cost": 40, "rollback_cost": 20}
        }
        result = optimize_transaction_order(adjacency_list, node_properties)
        # Check if the result is a valid topological sort
        self.assertEqual(len(result), 7)
        for node, neighbors in adjacency_list.items():
            for neighbor in neighbors:
                self.assertTrue(result.index(node) < result.index(neighbor),
                               f"Node {node} should come before {neighbor}")

    def test_edge_case_zero_probability(self):
        """Test with nodes having zero success probability."""
        adjacency_list = {0: [1, 2], 1: [3], 2: [3], 3: []}
        node_properties = {
            0: {"service_id": 1, "success_probability": 0.0, "operation_cost": 10, "rollback_cost": 5},
            1: {"service_id": 2, "success_probability": 0.8, "operation_cost": 15, "rollback_cost": 8},
            2: {"service_id": 3, "success_probability": 0.7, "operation_cost": 20, "rollback_cost": 10},
            3: {"service_id": 4, "success_probability": 0.6, "operation_cost": 25, "rollback_cost": 12}
        }
        result = optimize_transaction_order(adjacency_list, node_properties)
        # The result should be a valid topological sort
        self.assertEqual(len(result), 4)
        # Since node 0 has 0 success probability, it might be optimal to execute it later
        # to minimize expected rollback costs for other nodes
        self.assertIn(0, result)
        self.assertIn(1, result)
        self.assertIn(2, result)
        self.assertIn(3, result)
        self.assertTrue(result.index(0) < result.index(1))
        self.assertTrue(result.index(0) < result.index(2))
        self.assertTrue(result.index(1) < result.index(3))
        self.assertTrue(result.index(2) < result.index(3))

    def test_edge_case_perfect_probability(self):
        """Test with nodes having perfect (1.0) success probability."""
        adjacency_list = {0: [1, 2], 1: [3], 2: [3], 3: []}
        node_properties = {
            0: {"service_id": 1, "success_probability": 1.0, "operation_cost": 10, "rollback_cost": 5},
            1: {"service_id": 2, "success_probability": 0.8, "operation_cost": 15, "rollback_cost": 8},
            2: {"service_id": 3, "success_probability": 0.7, "operation_cost": 20, "rollback_cost": 10},
            3: {"service_id": 4, "success_probability": 0.6, "operation_cost": 25, "rollback_cost": 12}
        }
        result = optimize_transaction_order(adjacency_list, node_properties)
        # The result should be a valid topological sort
        self.assertEqual(len(result), 4)
        # Since node 0 has 1.0 success probability, it might be optimal to execute it earlier
        self.assertIn(0, result)
        self.assertIn(1, result)
        self.assertIn(2, result)
        self.assertIn(3, result)
        self.assertTrue(result.index(0) < result.index(1))
        self.assertTrue(result.index(0) < result.index(2))
        self.assertTrue(result.index(1) < result.index(3))
        self.assertTrue(result.index(2) < result.index(3))

    def test_large_dag(self):
        """Test with a larger DAG to check efficiency."""
        # Create a larger DAG with 50 nodes
        adjacency_list = {}
        node_properties = {}
        
        # Create a simple linear chain for simplicity
        for i in range(49):
            adjacency_list[i] = [i+1]
            node_properties[i] = {
                "service_id": i,
                "success_probability": 0.9,
                "operation_cost": 10,
                "rollback_cost": 5
            }
        
        adjacency_list[49] = []
        node_properties[49] = {
            "service_id": 49,
            "success_probability": 0.9,
            "operation_cost": 10,
            "rollback_cost": 5
        }
        
        result = optimize_transaction_order(adjacency_list, node_properties)
        
        # Check if result is valid
        self.assertEqual(len(result), 50)
        for i in range(49):
            self.assertTrue(result.index(i) < result.index(i+1))

    def test_varying_rollback_costs(self):
        """Test with nodes having significantly different rollback costs."""
        adjacency_list = {0: [1, 2], 1: [3], 2: [3], 3: []}
        node_properties = {
            0: {"service_id": 1, "success_probability": 0.9, "operation_cost": 10, "rollback_cost": 5},
            1: {"service_id": 2, "success_probability": 0.8, "operation_cost": 15, "rollback_cost": 100},
            2: {"service_id": 3, "success_probability": 0.7, "operation_cost": 20, "rollback_cost": 10},
            3: {"service_id": 4, "success_probability": 0.6, "operation_cost": 25, "rollback_cost": 1000}
        }
        result = optimize_transaction_order(adjacency_list, node_properties)
        # Check if the result is a valid topological sort
        self.assertEqual(len(result), 4)
        self.assertIn(0, result)
        self.assertIn(1, result)
        self.assertIn(2, result)
        self.assertIn(3, result)
        self.assertTrue(result.index(0) < result.index(1))
        self.assertTrue(result.index(0) < result.index(2))
        self.assertTrue(result.index(1) < result.index(3))
        self.assertTrue(result.index(2) < result.index(3))

    def test_multiple_valid_orders(self):
        """Test with a DAG that has multiple valid topological orderings."""
        adjacency_list = {0: [2], 1: [2], 2: []}
        node_properties = {
            0: {"service_id": 1, "success_probability": 0.9, "operation_cost": 10, "rollback_cost": 5},
            1: {"service_id": 2, "success_probability": 0.8, "operation_cost": 15, "rollback_cost": 8},
            2: {"service_id": 3, "success_probability": 0.7, "operation_cost": 20, "rollback_cost": 10}
        }
        result = optimize_transaction_order(adjacency_list, node_properties)
        # Check if the result is a valid topological sort
        self.assertEqual(len(result), 3)
        self.assertIn(0, result)
        self.assertIn(1, result)
        self.assertIn(2, result)
        self.assertTrue(result.index(0) < result.index(2))
        self.assertTrue(result.index(1) < result.index(2))


if __name__ == '__main__':
    unittest.main()