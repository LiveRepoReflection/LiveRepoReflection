import unittest
import random
from collaborative_text import Document

class TestCollaborativeText(unittest.TestCase):
    def create_operations(self, ops):
        """
        Returns a shallow copy of operations list.
        """
        return [op.copy() for op in ops]
    
    def apply_operations(self, doc, ops):
        """
        Applies a list of operations to the document.
        """
        for op in ops:
            doc.apply_operation(op)
    
    def test_sequential_insert(self):
        """
        Test sequential insert operations.
        Expected final state: "hello"
        """
        ops = [
            {"type": "insert", "pos": 0, "char": "h", "op_id": 1, "user": "A"},
            {"type": "insert", "pos": 1, "char": "e", "op_id": 2, "user": "A"},
            {"type": "insert", "pos": 2, "char": "l", "op_id": 3, "user": "A"},
            {"type": "insert", "pos": 3, "char": "l", "op_id": 4, "user": "A"},
            {"type": "insert", "pos": 4, "char": "o", "op_id": 5, "user": "A"}
        ]
        doc = Document()
        self.apply_operations(doc, ops)
        self.assertEqual(doc.get_text(), "hello")

    def test_insert_and_delete(self):
        """
        Insert letters to form 'world' then delete 'w' to form 'orld'.
        """
        ops = [
            {"type": "insert", "pos": 0, "char": "w", "op_id": 1, "user": "B"},
            {"type": "insert", "pos": 1, "char": "o", "op_id": 2, "user": "B"},
            {"type": "insert", "pos": 2, "char": "r", "op_id": 3, "user": "B"},
            {"type": "insert", "pos": 3, "char": "l", "op_id": 4, "user": "B"},
            {"type": "insert", "pos": 4, "char": "d", "op_id": 5, "user": "B"},
            {"type": "delete", "pos": 0, "op_id": 6, "user": "B"}
        ]
        doc = Document()
        self.apply_operations(doc, ops)
        self.assertEqual(doc.get_text(), "orld")

    def test_concurrent_inserts_consistency(self):
        """
        Simulate two documents receiving the same set of concurrent operations in different orders.
        Two users insert at the same position concurrently.
        Conflict resolution should deterministically order the inserts.
        """
        # Two concurrent operations at pos 0.
        # Lower op_id should be applied before.
        ops = [
            {"type": "insert", "pos": 0, "char": "A", "op_id": 10, "user": "A"},
            {"type": "insert", "pos": 0, "char": "B", "op_id": 11, "user": "B"},
            {"type": "insert", "pos": 2, "char": "C", "op_id": 12, "user": "A"}
        ]
        # Expected resolution: "AB C" where the first insert (A with id 10) takes position 0,
        # then B (id 11) goes immediately after, and then C at the end.
        # Expected final text: "ABC"
        expected = "ABC"

        # First document: operations in given order.
        doc1 = Document()
        self.apply_operations(doc1, self.create_operations(ops))

        # Second document: operations in shuffled order.
        shuffled_ops = self.create_operations(ops)
        random.shuffle(shuffled_ops)
        doc2 = Document()
        self.apply_operations(doc2, shuffled_ops)

        self.assertEqual(doc1.get_text(), expected)
        self.assertEqual(doc2.get_text(), expected)

    def test_out_of_order_delivery(self):
        """
        Simulate out-of-order delivery of multiple operations.
        Regardless of the order, the documents should converge.
        """
        ops = [
            {"type": "insert", "pos": 0, "char": "X", "op_id": 20, "user": "C"},
            {"type": "insert", "pos": 1, "char": "Y", "op_id": 21, "user": "C"},
            {"type": "insert", "pos": 2, "char": "Z", "op_id": 22, "user": "C"},
            {"type": "delete", "pos": 1, "op_id": 23, "user": "C"}
        ]
        # Expected final text: "XZ"
        expected = "XZ"

        doc1 = Document()
        doc2 = Document()
        
        # Applying ops in natural order to doc1.
        self.apply_operations(doc1, self.create_operations(ops))
        
        # Applying ops in reverse order to doc2.
        rev_ops = self.create_operations(ops)
        rev_ops.reverse()
        self.apply_operations(doc2, rev_ops)
        
        self.assertEqual(doc1.get_text(), expected)
        self.assertEqual(doc2.get_text(), expected)

    def test_idempotency(self):
        """
        Test that applying the same operation more than once does not affect the final state.
        """
        ops = [
            {"type": "insert", "pos": 0, "char": "I", "op_id": 30, "user": "D"},
            {"type": "insert", "pos": 1, "char": "D", "op_id": 31, "user": "D"}
        ]
        doc = Document()
        # Apply each operation twice.
        for op in ops:
            doc.apply_operation(op)
            doc.apply_operation(op)
        self.assertEqual(doc.get_text(), "ID")

    def test_complex_scenario(self):
        """
        Simulate a complex scenario with mixed concurrent operations,
        out-of-order delivery, and operations affecting overlapping positions.
        """
        ops = [
            {"type": "insert", "pos": 0, "char": "S", "op_id": 40, "user": "E"},
            {"type": "insert", "pos": 1, "char": "y", "op_id": 41, "user": "E"},
            {"type": "insert", "pos": 2, "char": "n", "op_id": 42, "user": "E"},
            {"type": "insert", "pos": 3, "char": "c", "op_id": 43, "user": "F"},
            {"type": "delete", "pos": 1, "op_id": 44, "user": "E"},  # remove 'y'
            {"type": "insert", "pos": 1, "char": "T", "op_id": 45, "user": "F"},
            {"type": "insert", "pos": 4, "char": "!", "op_id": 46, "user": "E"}
        ]
        # The final expected text computation depends on the conflict resolution.
        # One possible resolution (assuming op_ids determine ordering):
        # Step-by-step:
        # "S" (from op 40)
        # "Sy" (op 41) -> then "Syn" (op 42) -> then "Sync" (op 43) inserted at pos 3.
        # Deleting at pos 1 (op 44) -> removes 'y', text becomes "Snc"
        # Inserting at pos 1 "T" (op 45): text becomes "STnc"
        # Inserting "!" at pos 4 (op 46): text becomes "STnc!"
        expected = "STnc!"

        # Create two docs to simulate different ordering.
        doc1 = Document()
        doc2 = Document()

        order1 = self.create_operations(ops)
        order2 = self.create_operations(ops)
        random.shuffle(order2)

        self.apply_operations(doc1, order1)
        self.apply_operations(doc2, order2)

        self.assertEqual(doc1.get_text(), expected)
        self.assertEqual(doc2.get_text(), expected)


if __name__ == "__main__":
    unittest.main()