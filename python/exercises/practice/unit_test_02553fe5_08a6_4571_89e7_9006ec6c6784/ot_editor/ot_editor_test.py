import unittest
from ot_editor import transform

class TestOTEditor(unittest.TestCase):
    def test_insert_delete_transform(self):
        # op1 inserts "X" at index 1, op2 deletes 1 character at index 2.
        op1 = {'type': 'insert', 'index': 1, 'text': 'X'}
        op2 = {'type': 'delete', 'index': 2, 'length': 1}
        # Since op1 is inserted at index 1, op2 should shift right by len("X") which is 1.
        expected = {'type': 'delete', 'index': 3, 'length': 1}
        self.assertEqual(transform(op1, op2), expected)

    def test_insert_insert_transform_same_index(self):
        # Both operations insert at the same index.
        op1 = {'type': 'insert', 'index': 3, 'text': 'A'}
        op2 = {'type': 'insert', 'index': 3, 'text': 'B'}
        # When the indexes are equal, assume local op1 takes precedence so remote op2 shifts right.
        expected = {'type': 'insert', 'index': 4, 'text': 'B'}
        self.assertEqual(transform(op1, op2), expected)

    def test_insert_insert_transform_different_index(self):
        # op1 inserts after op2's insertion index.
        op1 = {'type': 'insert', 'index': 5, 'text': 'Hello'}
        op2 = {'type': 'insert', 'index': 3, 'text': 'World'}
        # op1 occurs after op2; therefore, op2 remains unchanged.
        expected = {'type': 'insert', 'index': 3, 'text': 'World'}
        self.assertEqual(transform(op1, op2), expected)

    def test_delete_insert_transform(self):
        # op1 deletes two characters starting at index 2, op2 inserts at index 5.
        op1 = {'type': 'delete', 'index': 2, 'length': 2}
        op2 = {'type': 'insert', 'index': 5, 'text': 'Z'}
        # Since op1 deletion is before op2 index, remote op2 should shift left by 2.
        expected = {'type': 'insert', 'index': 3, 'text': 'Z'}
        self.assertEqual(transform(op1, op2), expected)

    def test_delete_delete_transform_non_overlap(self):
        # op1 deletes characters at index 1 (length 2), op2 deletes starting at index 5 (length 3).
        op1 = {'type': 'delete', 'index': 1, 'length': 2}
        op2 = {'type': 'delete', 'index': 5, 'length': 3}
        # Since op1 deletion is entirely before op2, op2's index should shift left by 2.
        expected = {'type': 'delete', 'index': 3, 'length': 3}
        self.assertEqual(transform(op1, op2), expected)

    def test_delete_delete_transform_overlap(self):
        # op1 deletes from index 2 to index 4 (length 3), op2 deletes starting at index 4 (length 2).
        op1 = {'type': 'delete', 'index': 2, 'length': 3}
        op2 = {'type': 'delete', 'index': 4, 'length': 2}
        # op2 starts in the region deleted by op1. Assume transformation adjusts op2's index to op1['index']
        # and reduces its length by the overlapping portion.
        # Overlap: from index 4 to op1_end (2+3=5) => 1 character overlap. New op2 length = 2 - 1 = 1.
        expected = {'type': 'delete', 'index': 2, 'length': 1}
        self.assertEqual(transform(op1, op2), expected)

    def test_insert_delete_no_effect(self):
        # op1 inserts at index 10, op2 deletes at index 3; op1 occurs after op2, so no transformation.
        op1 = {'type': 'insert', 'index': 10, 'text': 'Hello'}
        op2 = {'type': 'delete', 'index': 3, 'length': 1}
        expected = {'type': 'delete', 'index': 3, 'length': 1}
        self.assertEqual(transform(op1, op2), expected)

    def test_delete_insert_no_effect(self):
        # op1 deletes at index 10, op2 inserts at index 5; op1 occurs after op2, so op2 remains unchanged.
        op1 = {'type': 'delete', 'index': 10, 'length': 3}
        op2 = {'type': 'insert', 'index': 5, 'text': 'World'}
        expected = {'type': 'insert', 'index': 5, 'text': 'World'}
        self.assertEqual(transform(op1, op2), expected)

    def test_boundary_conditions(self):
        # op1 inserts at the very beginning of the document,
        # op2 deletes starting at index 0.
        op1 = {'type': 'insert', 'index': 0, 'text': 'Start'}
        op2 = {'type': 'delete', 'index': 0, 'length': 3}
        # Since op1 insertion is at index 0 and takes precedence when indexes are equal,
        # op2 deletion should be shifted to the right by len("Start").
        expected = {'type': 'delete', 'index': 5, 'length': 3}
        self.assertEqual(transform(op1, op2), expected)

    def test_empty_operation(self):
        # Testing when op1 is effectively a no-op due to an empty string insert.
        op1 = {'type': 'insert', 'index': 4, 'text': ''}
        op2 = {'type': 'insert', 'index': 7, 'text': 'abc'}
        # op1 should not affect op2.
        expected = {'type': 'insert', 'index': 7, 'text': 'abc'}
        self.assertEqual(transform(op1, op2), expected)

if __name__ == '__main__':
    unittest.main()