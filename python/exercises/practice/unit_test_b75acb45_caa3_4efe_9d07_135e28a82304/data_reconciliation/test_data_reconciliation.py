import unittest
from data_reconciliation.data_reconciliation import reconcile_data

class TestDataReconciliation(unittest.TestCase):
    def test_empty_input(self):
        self.assertEqual(reconcile_data([]), {})

    def test_single_node(self):
        input_data = [
            {
                "key1": {"value": 10, "timestamp": 1678886400},
                "key2": {"value": 20, "timestamp": 1678886405}
            }
        ]
        expected = {"key1": 10, "key2": 20}
        self.assertEqual(reconcile_data(input_data), expected)

    def test_multiple_nodes_no_conflicts(self):
        input_data = [
            {
                "key1": {"value": 10, "timestamp": 1678886400},
                "key2": {"value": 20, "timestamp": 1678886405}
            },
            {
                "key3": {"value": 30, "timestamp": 1678886410}
            }
        ]
        expected = {"key1": 10, "key2": 20, "key3": 30}
        self.assertEqual(reconcile_data(input_data), expected)

    def test_conflict_resolution_latest_timestamp(self):
        input_data = [
            {
                "key1": {"value": 10, "timestamp": 1678886400},
                "key2": {"value": 20, "timestamp": 1678886405}
            },
            {
                "key1": {"value": 15, "timestamp": 1678886402},
                "key3": {"value": 30, "timestamp": 1678886410}
            }
        ]
        expected = {"key1": 15, "key2": 20, "key3": 30}
        self.assertEqual(reconcile_data(input_data), expected)

    def test_tie_breaker_lowest_value(self):
        input_data = [
            {
                "key1": {"value": 10, "timestamp": 1678886400},
                "key2": {"value": 20, "timestamp": 1678886400}
            },
            {
                "key1": {"value": 15, "timestamp": 1678886400},
                "key2": {"value": 25, "timestamp": 1678886405}
            }
        ]
        expected = {"key1": 10, "key2": 25}
        self.assertEqual(reconcile_data(input_data), expected)

    def test_node_with_empty_data(self):
        input_data = [
            {
                "key1": {"value": 10, "timestamp": 1678886400}
            },
            {},
            {
                "key2": {"value": 20, "timestamp": 1678886405}
            }
        ]
        expected = {"key1": 10, "key2": 20}
        self.assertEqual(reconcile_data(input_data), expected)

    def test_missing_timestamp(self):
        input_data = [
            {
                "key1": {"value": 10, "timestamp": 1678886400},
                "key2": {"value": 20}
            },
            {
                "key1": {"value": 15, "timestamp": 1678886402}
            }
        ]
        with self.assertRaises(ValueError):
            reconcile_data(input_data)

    def test_missing_value(self):
        input_data = [
            {
                "key1": {"timestamp": 1678886400},
                "key2": {"value": 20, "timestamp": 1678886405}
            }
        ]
        with self.assertRaises(ValueError):
            reconcile_data(input_data)

    def test_non_integer_value(self):
        input_data = [
            {
                "key1": {"value": "10", "timestamp": 1678886400},
                "key2": {"value": 20, "timestamp": 1678886405}
            }
        ]
        with self.assertRaises(ValueError):
            reconcile_data(input_data)

    def test_large_number_of_nodes(self):
        input_data = []
        expected = {}
        for i in range(1000):
            node_data = {
                f"key{i}": {"value": i, "timestamp": 1678886400 + i}
            }
            input_data.append(node_data)
            expected[f"key{i}"] = i
        self.assertEqual(reconcile_data(input_data), expected)

if __name__ == '__main__':
    unittest.main()