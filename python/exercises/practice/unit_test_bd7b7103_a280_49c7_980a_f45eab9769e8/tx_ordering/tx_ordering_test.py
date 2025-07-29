import unittest
from tx_ordering import order_transactions

class TestTransactionOrdering(unittest.TestCase):
    def test_simple_dependencies(self):
        transactions = [
            {"transaction_id": "T1", "dependencies": [], "timestamp": 1},
            {"transaction_id": "T2", "dependencies": ["T1"], "timestamp": 2},
            {"transaction_id": "T3", "dependencies": ["T1"], "timestamp": 3},
            {"transaction_id": "T4", "dependencies": ["T2", "T3"], "timestamp": 4},
        ]
        expected = ["T1", "T2", "T3", "T4"]
        self.assertEqual(order_transactions(transactions), expected)

    def test_multiple_independent_chains(self):
        transactions = [
            {"transaction_id": "A1", "dependencies": [], "timestamp": 10},
            {"transaction_id": "A2", "dependencies": ["A1"], "timestamp": 11},
            {"transaction_id": "B1", "dependencies": [], "timestamp": 5},
            {"transaction_id": "B2", "dependencies": ["B1"], "timestamp": 6},
        ]
        expected = ["B1", "B2", "A1", "A2"]
        self.assertEqual(order_transactions(transactions), expected)

    def test_timestamp_tiebreaker(self):
        transactions = [
            {"transaction_id": "X", "dependencies": [], "timestamp": 100},
            {"transaction_id": "Y", "dependencies": [], "timestamp": 99},
            {"transaction_id": "Z", "dependencies": ["X", "Y"], "timestamp": 101},
        ]
        expected = ["Y", "X", "Z"]
        self.assertEqual(order_transactions(transactions), expected)

    def test_complex_dag(self):
        transactions = [
            {"transaction_id": "1", "dependencies": [], "timestamp": 1},
            {"transaction_id": "2", "dependencies": ["1"], "timestamp": 2},
            {"transaction_id": "3", "dependencies": ["1"], "timestamp": 3},
            {"transaction_id": "4", "dependencies": ["2", "3"], "timestamp": 4},
            {"transaction_id": "5", "dependencies": ["3"], "timestamp": 5},
            {"transaction_id": "6", "dependencies": ["4", "5"], "timestamp": 6},
        ]
        expected = ["1", "2", "3", "4", "5", "6"]
        self.assertEqual(order_transactions(transactions), expected)

    def test_empty_input(self):
        self.assertEqual(order_transactions([]), [])

    def test_missing_dependency(self):
        transactions = [
            {"transaction_id": "T1", "dependencies": ["T0"], "timestamp": 1},
        ]
        with self.assertRaises(ValueError):
            order_transactions(transactions)

    def test_cycle_detection(self):
        transactions = [
            {"transaction_id": "A", "dependencies": ["B"], "timestamp": 1},
            {"transaction_id": "B", "dependencies": ["A"], "timestamp": 2},
        ]
        with self.assertRaises(ValueError):
            order_transactions(transactions)

    def test_large_number_of_transactions(self):
        transactions = []
        expected = []
        for i in range(1000):
            tx = {"transaction_id": f"T{i}", "dependencies": [], "timestamp": i}
            transactions.append(tx)
            expected.append(f"T{i}")
        self.assertEqual(order_transactions(transactions), expected)

    def test_mixed_dependencies(self):
        transactions = [
            {"transaction_id": "A", "dependencies": [], "timestamp": 5},
            {"transaction_id": "B", "dependencies": ["A"], "timestamp": 6},
            {"transaction_id": "C", "dependencies": [], "timestamp": 1},
            {"transaction_id": "D", "dependencies": ["C"], "timestamp": 2},
            {"transaction_id": "E", "dependencies": ["B", "D"], "timestamp": 7},
        ]
        expected = ["C", "D", "A", "B", "E"]
        self.assertEqual(order_transactions(transactions), expected)

if __name__ == '__main__':
    unittest.main()