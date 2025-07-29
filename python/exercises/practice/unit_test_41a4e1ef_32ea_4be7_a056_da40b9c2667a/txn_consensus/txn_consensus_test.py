import unittest
from txn_consensus import process_transactions

class TestTxnConsensus(unittest.TestCase):

    def test_single_transaction_commit(self):
        # Single transaction, no conflicts should commit.
        N = 3
        T = [("a", 100, 1)]
        max_messages = 5
        latency_matrix = [
            [0, 2, 3],
            [2, 0, 1],
            [3, 1, 0]
        ]
        initial_state = {"a": 50}
        expected = [True]
        result = process_transactions(N, T, max_messages, latency_matrix, initial_state)
        self.assertEqual(result, expected)

    def test_conflicting_transactions(self):
        # Two transactions on the same key; lower node id should win and the other aborts.
        N = 4
        # Transaction from node 2 and node 0 conflicting on key "b"
        T = [("b", 200, 2), ("b", 300, 0)]
        max_messages = 8
        latency_matrix = [
            [0, 4, 5, 6],
            [4, 0, 3, 2],
            [5, 3, 0, 3],
            [6, 2, 3, 0]
        ]
        initial_state = {"b": 150}
        # Assuming our deterministic conflict resolution prioritizes the lower node_id,
        # transaction from node 0 wins; therefore, the order of transactions is as given.
        expected = [False, True]
        result = process_transactions(N, T, max_messages, latency_matrix, initial_state)
        self.assertEqual(result, expected)
        
    def test_multiple_transactions(self):
        # Example test with three transactions, including a conflict on key "x".
        N = 3
        T = [("x", 10, 0), ("y", 20, 1), ("x", 15, 2)]
        max_messages = 6
        latency_matrix = [
            [0, 1, 2],
            [1, 0, 1],
            [2, 1, 0]
        ]
        initial_state = {"x": 5, "y": 10}
        expected = [True, True, False]
        result = process_transactions(N, T, max_messages, latency_matrix, initial_state)
        self.assertEqual(result, expected)

    def test_insufficient_max_messages(self):
        # Test case where the max_messages limit is too low for any consensus to be achieved.
        N = 3
        T = [("z", 30, 0)]
        # Provide an intentionally low message cap
        max_messages = 1
        latency_matrix = [
            [0, 10, 10],
            [10, 0, 10],
            [10, 10, 0]
        ]
        initial_state = {"z": 25}
        expected = [False]
        result = process_transactions(N, T, max_messages, latency_matrix, initial_state)
        self.assertEqual(result, expected)

    def test_varying_latency_effects(self):
        # Test that varying latencies might affect consensus decisions if the algorithm
        # optimizes for latency; this test assumes that lower latency paths help complete consensus.
        N = 4
        T = [("k", 500, 3)]
        max_messages = 10
        latency_matrix = [
            [0, 50, 50, 80],
            [50, 0, 20, 20],
            [50, 20, 0, 20],
            [80, 20, 20, 0]
        ]
        initial_state = {"k": 400}
        expected = [True]
        result = process_transactions(N, T, max_messages, latency_matrix, initial_state)
        self.assertEqual(result, expected)

    def test_repeated_calls_consistency(self):
        # Ensure that repeated calls to the process_transactions function
        # with the same inputs yield consistent results.
        N = 3
        T = [("x", 10, 0), ("x", 15, 1)]
        max_messages = 7
        latency_matrix = [
            [0, 2, 3],
            [2, 0, 2],
            [3, 2, 0]
        ]
        initial_state = {"x": 5}
        expected = [True, False]
        result1 = process_transactions(N, T, max_messages, latency_matrix, initial_state)
        result2 = process_transactions(N, T, max_messages, latency_matrix, initial_state)
        self.assertEqual(result1, expected)
        self.assertEqual(result2, expected)

if __name__ == "__main__":
    unittest.main()