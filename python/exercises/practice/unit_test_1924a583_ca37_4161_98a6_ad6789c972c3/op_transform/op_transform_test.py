import unittest
from op_transform import transform_operation

class TestOpTransform(unittest.TestCase):
    def test_insert_remote_before_local(self):
        # Local insert at position 1, remote insert at position 0 shifts local op right.
        local_op = ("insert", 1, "X")
        remote_op = ("insert", 0, "Y")
        expected = ("insert", 2, "X")
        result = transform_operation(local_op, remote_op)
        self.assertEqual(result, expected)

    def test_insert_remote_after_local(self):
        # Local insert at position 2, remote insert at position 4 does not affect local op.
        local_op = ("insert", 2, "X")
        remote_op = ("insert", 4, "Y")
        expected = ("insert", 2, "X")
        result = transform_operation(local_op, remote_op)
        self.assertEqual(result, expected)

    def test_delete_remote_insert_before_local(self):
        # Local delete starting at position 5, remote insert at position 2 shifts deletion right.
        local_op = ("delete", 5, 3)
        remote_op = ("insert", 2, "abc")  # remote op inserts 3 characters
        expected = ("delete", 8, 3)
        result = transform_operation(local_op, remote_op)
        self.assertEqual(result, expected)

    def test_delete_remote_insert_after_local(self):
        # Local delete, remote insert happens after local deletion zone so no change.
        local_op = ("delete", 3, 2)
        remote_op = ("insert", 10, "P")
        expected = ("delete", 3, 2)
        result = transform_operation(local_op, remote_op)
        self.assertEqual(result, expected)

    def test_insert_remote_delete_before_local(self):
        # Local insert at position 5 and remote delete from position 2 of length 2.
        # Remote deletion removes indices 2 and 3, so local insertion position shifts left by 2.
        local_op = ("insert", 5, "Hello")
        remote_op = ("delete", 2, 2)
        expected = ("insert", 3, "Hello")
        result = transform_operation(local_op, remote_op)
        self.assertEqual(result, expected)

    def test_delete_remote_delete_before_local(self):
        # Both operations are deletes.
        # Remote delete from position 2, length 2 deletes two characters before local op.
        # Local op originally at position 6 shifts left by 2.
        local_op = ("delete", 6, 2)
        remote_op = ("delete", 2, 2)
        expected = ("delete", 4, 2)
        result = transform_operation(local_op, remote_op)
        self.assertEqual(result, expected)

    def test_delete_both_overlapping(self):
        # Both operations are deletes and overlapping:
        # Remote op: delete from 3, length 5 removes indices [3,7]
        # Local op: delete from 5, length 4 initially covers indices [5,8].
        # After remote deletion, local deletion start shifts left to index 3.
        # The overlap between remote deletion and local op is indices [5,7] => 3 characters.
        # So transformed local op should delete only the remaining 1 character.
        local_op = ("delete", 5, 4)
        remote_op = ("delete", 3, 5)
        expected = ("delete", 3, 1)
        result = transform_operation(local_op, remote_op)
        self.assertEqual(result, expected)

    def test_insert_remote_delete_overlapping_local(self):
        # Local op is an insert at position 3; remote op deletes from position 1, length 3.
        # Remote deletion removes indices [1,3]. Since local insertion’s position falls into the deleted region,
        # it should adjust to the start of the deletion.
        local_op = ("insert", 3, "A")
        remote_op = ("delete", 1, 3)
        expected = ("insert", 1, "A")
        result = transform_operation(local_op, remote_op)
        self.assertEqual(result, expected)

    def test_no_effect_transform(self):
        # When local and remote operations do not affect each other.
        local_op = ("delete", 8, 2)
        remote_op = ("insert", 3, "XYZ")
        # Since remote insert is before local delete position, need to shift: local pos becomes 11.
        expected = ("delete", 11, 2)
        result = transform_operation(local_op, remote_op)
        self.assertEqual(result, expected)

    def test_zero_length_operations(self):
        # Testing operations that have zero effect.
        local_op = ("insert", 4, "")
        remote_op = ("delete", 2, 0)
        # No matter remote op's effect, zero-length insertion should remain at same position.
        expected = ("insert", 4, "")
        result = transform_operation(local_op, remote_op)
        self.assertEqual(result, expected)

if __name__ == '__main__':
    unittest.main()