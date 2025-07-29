import unittest
from transaction_resolve import resolve_transactions


class TransactionResolveTest(unittest.TestCase):
    def test_all_prepared_should_commit(self):
        transactions = [
            [(1, 101, "PREPARED"), (2, 101, "PREPARED")]
        ]
        expected = {
            101: "COMMITTED"
        }
        self.assertEqual(resolve_transactions(transactions), expected)

    def test_any_commit_should_commit_globally(self):
        transactions = [
            [(1, 102, "COMMITTED"), (2, 102, "PREPARED")]
        ]
        expected = {
            102: "COMMITTED"
        }
        self.assertEqual(resolve_transactions(transactions), expected)

    def test_all_abort_should_abort(self):
        transactions = [
            [(1, 103, "ABORTED"), (2, 103, "ABORTED")]
        ]
        expected = {
            103: "ABORTED"
        }
        self.assertEqual(resolve_transactions(transactions), expected)

    def test_any_abort_without_commit_should_abort(self):
        transactions = [
            [(1, 104, "PREPARED"), (2, 104, "ABORTED")]
        ]
        expected = {
            104: "ABORTED"
        }
        self.assertEqual(resolve_transactions(transactions), expected)

    def test_commit_dominates_abort(self):
        transactions = [
            [(1, 105, "COMMITTED"), (2, 105, "ABORTED")]
        ]
        expected = {
            105: "COMMITTED"
        }
        self.assertEqual(resolve_transactions(transactions), expected)

    def test_multiple_transactions(self):
        transactions = [
            [(1, 101, "PREPARED"), (2, 101, "PREPARED")],
            [(1, 102, "COMMITTED"), (2, 102, "PREPARED")],
            [(1, 103, "ABORTED"), (2, 103, "PREPARED")],
            [(1, 104, "ABORTED"), (2, 104, "ABORTED")],
            [(1, 105, "COMMITTED"), (2, 105, "ABORTED")]
        ]
        expected = {
            101: "COMMITTED",
            102: "COMMITTED",
            103: "ABORTED",
            104: "ABORTED",
            105: "COMMITTED"
        }
        self.assertEqual(resolve_transactions(transactions), expected)

    def test_large_number_of_nodes(self):
        # Create a transaction with many nodes, all prepared
        large_transaction = [(i, 201, "PREPARED") for i in range(1, 101)]
        # Add one node that aborted
        large_transaction.append((101, 201, "ABORTED"))
        
        transactions = [large_transaction]
        expected = {201: "ABORTED"}
        
        self.assertEqual(resolve_transactions(transactions), expected)

    def test_large_number_of_transactions(self):
        # Create 1000 transactions, all prepared
        transactions = []
        for i in range(1, 1001):
            transactions.append([(1, i, "PREPARED"), (2, i, "PREPARED")])
        
        expected = {i: "COMMITTED" for i in range(1, 1001)}
        
        self.assertEqual(resolve_transactions(transactions), expected)

    def test_mixed_states_complex(self):
        transactions = [
            [(1, 301, "PREPARED"), (2, 301, "PREPARED"), (3, 301, "PREPARED")],
            [(1, 302, "COMMITTED"), (2, 302, "PREPARED"), (3, 302, "ABORTED")],
            [(1, 303, "ABORTED"), (2, 303, "PREPARED"), (3, 303, "PREPARED")],
            [(1, 304, "COMMITTED"), (2, 304, "COMMITTED"), (3, 304, "COMMITTED")],
            [(1, 305, "ABORTED"), (2, 305, "ABORTED"), (3, 305, "ABORTED")]
        ]
        expected = {
            301: "COMMITTED",
            302: "COMMITTED",
            303: "ABORTED",
            304: "COMMITTED",
            305: "ABORTED"
        }
        self.assertEqual(resolve_transactions(transactions), expected)

    def test_empty_input(self):
        transactions = []
        expected = {}
        self.assertEqual(resolve_transactions(transactions), expected)

    def test_single_node_transactions(self):
        transactions = [
            [(1, 401, "PREPARED")],
            [(1, 402, "COMMITTED")],
            [(1, 403, "ABORTED")]
        ]
        expected = {
            401: "COMMITTED",
            402: "COMMITTED",
            403: "ABORTED"
        }
        self.assertEqual(resolve_transactions(transactions), expected)

    def test_duplicate_node_entries(self):
        # Test handling of duplicate node entries (should consider the last state)
        transactions = [
            [(1, 501, "PREPARED"), (1, 501, "COMMITTED"), (2, 501, "PREPARED")]
        ]
        expected = {
            501: "COMMITTED"
        }
        self.assertEqual(resolve_transactions(transactions), expected)

    def test_edge_case_mix(self):
        transactions = [
            # Empty transaction (shouldn't happen in practice but test robustness)
            [],
            # Conflicting states within the same node (take last state)
            [(1, 601, "PREPARED"), (1, 601, "COMMITTED"), (2, 601, "ABORTED")],
            # Transaction with many nodes in different states
            [(i, 602, "PREPARED") for i in range(1, 10)] + [(10, 602, "ABORTED")]
        ]
        expected = {
            601: "COMMITTED",
            602: "ABORTED"
        }
        self.assertEqual(resolve_transactions(transactions), expected)


if __name__ == "__main__":
    unittest.main()