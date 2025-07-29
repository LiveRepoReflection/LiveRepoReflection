import unittest
from tx_validation import validate_transactions

class TxValidationTest(unittest.TestCase):

    def test_empty_transactions(self):
        transactions = []
        # Expect True because empty set has no conflicts
        self.assertTrue(validate_transactions(transactions))

    def test_single_transaction_no_conflict(self):
        transactions = [
            ("tx1", 1, "READ", "dataA")
        ]
        self.assertTrue(validate_transactions(transactions))

    def test_duplicate_entries(self):
        # Duplicate entries for same transaction should be handled correctly.
        transactions = [
            ("tx1", 1, "WRITE", "dataA"),
            ("tx1", 1, "WRITE", "dataA"),
            ("tx2", 2, "DELETE", "dataB"),
            ("tx2", 2, "DELETE", "dataB")
        ]
        self.assertTrue(validate_transactions(transactions))

    def test_multiple_transactions_no_conflict(self):
        transactions = [
            # Transaction tx1 on node 1 and node 2 (both READ)
            ("tx1", 1, "READ", "dataA"),
            ("tx1", 2, "READ", "dataA"),
            # Transaction tx2 on node 1, multiple READ operations on same data
            ("tx2", 1, "READ", "dataB"),
            ("tx2", 1, "READ", "dataB"),
            # Transaction tx3 on node 3 with WRITE (only one entry)
            ("tx3", 3, "WRITE", "dataC"),
            # Transaction tx4 on node 2 with DELETE (only one entry)
            ("tx4", 2, "DELETE", "dataD")
        ]
        self.assertTrue(validate_transactions(transactions))

    def test_conflict_different_transactions_same_node(self):
        transactions = [
            ("tx1", 1, "WRITE", "dataX"),
            ("tx2", 1, "READ", "dataX")
        ]
        # WRITE conflicts with READ on same node for same data.
        self.assertFalse(validate_transactions(transactions))

    def test_conflict_among_multiple_nodes(self):
        transactions = [
            # Two transactions conflicting at node 4 on same data.
            ("tx1", 4, "DELETE", "dataY"),
            ("tx2", 4, "WRITE", "dataY"),
            # Non-conflicting transactions on other nodes.
            ("tx3", 5, "READ", "dataZ"),
            ("tx4", 6, "WRITE", "dataZ")
        ]
        self.assertFalse(validate_transactions(transactions))

    def test_inconsistent_transaction_parts(self):
        # Same transaction ID with entries on different nodes must be consistent.
        transactions = [
            ("tx5", 1, "WRITE", "dataM"),
            ("tx5", 2, "WRITE", "dataM"),  # Consistent: same op and data.
            ("tx6", 3, "READ", "dataN"),
            ("tx6", 4, "WRITE", "dataN")   # Inconsistent: different operations.
        ]
        self.assertFalse(validate_transactions(transactions))

    def test_large_input_efficiency(self):
        # Create a large number of non-conflicting transactions.
        transactions = []
        # For nodes 1 to 1000, create transactions that do not conflict.
        for i in range(1, 1001):
            tx_id = f"tx{i}"
            # Each transaction appears twice on different nodes with same operation and data.
            transactions.append((tx_id, i, "READ", f"data{i}"))
            transactions.append((tx_id, (i % 1000) + 1, "READ", f"data{i}"))
        # Should handle large input efficiently, expecting True.
        self.assertTrue(validate_transactions(transactions))

    def test_duplicate_entries_with_inconsistency(self):
        # Even if duplicates exist, if there is any inconsistency in one transaction, the result should be False.
        transactions = [
            ("tx7", 1, "WRITE", "dataP"),
            ("tx7", 1, "WRITE", "dataP"),
            ("tx7", 2, "DELETE", "dataP"),  # Inconsistent with other duplicate entries.
            ("tx8", 3, "READ", "dataQ"),
            ("tx8", 3, "READ", "dataQ")
        ]
        self.assertFalse(validate_transactions(transactions))

if __name__ == "__main__":
    unittest.main()