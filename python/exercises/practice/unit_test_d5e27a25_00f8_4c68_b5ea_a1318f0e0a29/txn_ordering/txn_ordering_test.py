import unittest
from collections import defaultdict

# Import the solution function from txn_ordering.py
from txn_ordering import order_transactions

class TxnOrderingTest(unittest.TestCase):
    
    def extract_dependencies(self, operations):
        """
        Extract dependencies from operations.
        For each node and data item, if there are consecutive conflicting operations
        (one of them being a WRITE), then the earlier transaction must come before the later one.
        Returns a set of dependency pairs (tx_before, tx_after).
        """
        dependencies = set()
        # Group operations by node and data_item preserving order in input
        groups = defaultdict(list)
        for op in operations:
            tx_id, node_id, data_item, op_type = op
            groups[(node_id, data_item)].append(tx_id + ":" + op_type)
        
        # Also, for dependency extraction, we need to process per node and data item using original order.
        # Actually, it's better to iterate over the input list and group per (node, data_item)
        # with indexes
        grouped_ops = defaultdict(list)
        for idx, op in enumerate(operations):
            tx_id, node_id, data_item, op_type = op
            grouped_ops[(node_id, data_item)].append((idx, tx_id, op_type))
        
        # For each group, all pairs of consecutive conflicting operations yield a dependency.
        for key, op_list in grouped_ops.items():
            # Sort op_list by original order (should already be sorted)
            op_list.sort(key=lambda x: x[0])
            for i in range(len(op_list) - 1):
                idx1, tx1, type1 = op_list[i]
                for j in range(i + 1, len(op_list)):
                    idx2, tx2, type2 = op_list[j]
                    # Only consider if transactions are different
                    if tx1 == tx2:
                        continue
                    # If either operation is WRITE, there is a conflict.
                    if type1 == "WRITE" or type2 == "WRITE":
                        dependencies.add((tx1, tx2))
                        # Once a dependency is added between these two on this group, we continue with next pair.
                        break
        return dependencies
    
    def validate_order(self, operations, order):
        """
        Validate that the given order of transactions is a valid serializable order based 
        on the dependencies derived from the operations.
        """
        # In a valid order, all transactions present in operations must appear in order
        expected_txns = set(op[0] for op in operations)
        self.assertEqual(set(order), expected_txns, "The output order must include exactly all transactions from input.")
        
        # Map transaction to its index in ordering for fast lookup.
        pos = {tx: i for i, tx in enumerate(order)}
        
        # Extract dependencies based on each node and data_item
        dependencies = self.extract_dependencies(operations)
        
        for a, b in dependencies:
            self.assertLess(pos[a], pos[b], f"Transaction {a} must come before {b} based on conflict dependency.")
    
    def test_empty_input(self):
        operations = []
        result = order_transactions(operations)
        self.assertEqual(result, [], "Empty input should return an empty list.")
        
    def test_single_transaction_read(self):
        operations = [
            ("T1", 1, "A", "READ")
        ]
        result = order_transactions(operations)
        self.assertEqual(result, ["T1"], "Single transaction should return a list with that transaction.")
        
    def test_single_transaction_write(self):
        operations = [
            ("T1", 1, "A", "WRITE")
        ]
        result = order_transactions(operations)
        self.assertEqual(result, ["T1"], "Single transaction should return a list with that transaction.")
    
    def test_independent_transactions(self):
        operations = [
            ("T1", 1, "A", "WRITE"),
            ("T2", 1, "B", "WRITE")
        ]
        result = order_transactions(operations)
        # There is no dependency: any order containing T1 and T2 is valid.
        self.assertEqual(set(result), {"T1", "T2"}, "Independent transactions should be a permutation of T1 and T2.")
    
    def test_conflicting_writes(self):
        operations = [
            ("T1", 1, "A", "WRITE"),
            ("T2", 1, "A", "WRITE")
        ]
        result = order_transactions(operations)
        # Extract dependency from same node and same data_item should force T1 before T2.
        self.assertEqual(result[0], "T1", "T1 must appear before T2 due to write-write conflict on A.")
        self.assertEqual(result[1], "T2", "T1 must appear before T2 due to write-write conflict on A.")
        self.validate_order(operations, result)
    
    def test_read_write_conflict(self):
        operations = [
            ("T1", 1, "A", "WRITE"),
            ("T2", 1, "A", "READ")
        ]
        result = order_transactions(operations)
        # T1 must appear before T2
        self.assertEqual(result[0], "T1", "T1 must come before T2 due to write-read conflict on A.")
        self.assertEqual(result[1], "T2", "T1 must come before T2 due to write-read conflict on A.")
        self.validate_order(operations, result)
    
    def test_multiple_conflicts_across_nodes(self):
        operations = [
            ("T1", 1, "A", "WRITE"),
            ("T2", 1, "A", "WRITE"),
            ("T1", 2, "B", "READ"),
            ("T2", 2, "C", "WRITE"),
            ("T3", 1, "B", "WRITE"),
            ("T3", 2, "A", "READ")
        ]
        result = order_transactions(operations)
        self.validate_order(operations, result)
    
    def test_non_conflicting_order_with_mixed_ops(self):
        operations = [
            ("T1", 1, "A", "READ"),
            ("T2", 1, "A", "READ"),
            ("T1", 2, "B", "WRITE"),
            ("T3", 2, "C", "READ"),
            ("T2", 2, "D", "WRITE")
        ]
        result = order_transactions(operations)
        # Since there are only read-read conflicts on A, the only conflict is on write operations on different data_items.
        self.validate_order(operations, result)
    
    def test_cycle_detection(self):
        # Create a cycle: T1 -> T2 and T2 -> T1 via different conflicts.
        operations = [
            ("T1", 1, "A", "WRITE"),  # T1 writes A
            ("T2", 1, "A", "READ"),   # T2 reads A: dependency T1 -> T2
            ("T2", 2, "B", "WRITE"),  # T2 writes B
            ("T1", 2, "B", "READ")    # T1 reads B: dependency T2 -> T1, causing a cycle
        ]
        result = order_transactions(operations)
        self.assertEqual(result, [], "Cycle in dependencies should result in an empty list.")

    def test_complex_scenario(self):
        operations = [
            ("T1", 1, "X", "WRITE"),
            ("T2", 1, "Y", "WRITE"),
            ("T3", 1, "X", "READ"),
            ("T4", 2, "Z", "WRITE"),
            ("T1", 2, "Y", "READ"),
            ("T2", 2, "Z", "READ"),
            ("T3", 2, "W", "WRITE"),
            ("T4", 1, "W", "READ"),
            ("T5", 2, "X", "WRITE"),
            ("T5", 1, "Y", "READ")
        ]
        result = order_transactions(operations)
        # Validate that the returned order is valid according to dependencies.
        self.validate_order(operations, result)

if __name__ == '__main__':
    unittest.main()