import unittest
from collaborative_editing import apply_operations

# Define operation types for clarity
INSERT = 0
DELETE = 1

class CollaborativeEditingTest(unittest.TestCase):
    def test_empty_document(self):
        current_document = ""
        operations = []
        expected_document = ""
        expected_transformed = []
        updated_document, transformed_operations = apply_operations(current_document, operations)
        self.assertEqual(updated_document, expected_document)
        self.assertEqual(transformed_operations, expected_transformed)

    def test_single_insert(self):
        current_document = "hello"
        operations = [
            (1, 5, " world", INSERT)
        ]
        expected_document = "hello world"
        expected_transformed = [
            (1, 5, " world", INSERT)
        ]
        updated_document, transformed_operations = apply_operations(current_document, operations)
        self.assertEqual(updated_document, expected_document)
        self.assertEqual(transformed_operations, expected_transformed)

    def test_single_delete(self):
        # For delete, assume that the operation removes a substring of length equal to len(text)
        # starting at the given position.
        current_document = "hello world"
        # Delete the space between "hello" and "world"
        operations = [
            (1, 5, " ", DELETE)
        ]
        expected_document = "helloworld"
        expected_transformed = [
            (1, 5, " ", DELETE)
        ]
        updated_document, transformed_operations = apply_operations(current_document, operations)
        self.assertEqual(updated_document, expected_document)
        self.assertEqual(transformed_operations, expected_transformed)

    def test_conflicting_inserts(self):
        # Test with two concurrent insertions at the same position.
        # Conflict resolution: lower user_id operation is applied first.
        current_document = "hello world"
        operations = [
            (1, 5, ", cruel", INSERT),  # User 1: insert at position 5
            (2, 5, "big ", INSERT)      # User 2: insert at position 5, gets shifted
        ]
        # Expected: first operation is applied at pos 5, then second operation's position is transformed.
        # "hello" + ", cruel" + "big " + " world"
        expected_document = "hello, cruelbig  world"
        expected_transformed = [
            (1, 5, ", cruel", INSERT),
            (2, 12, "big ", INSERT)
        ]
        updated_document, transformed_operations = apply_operations(current_document, operations)
        self.assertEqual(updated_document, expected_document)
        self.assertEqual(transformed_operations, expected_transformed)

    def test_complex_edit(self):
        # This test combines deletion and insertion operations.
        # Assume operations are processed concurrently with lower user_id prioritized.
        current_document = "abcdef"
        operations = [
            (1, 2, "cd", DELETE),   # Delete 'cd' starting from index 2 => "abef"
            (2, 2, "XYZ", INSERT)   # Insert "XYZ" at index 2, transformed relative to deletion op.
        ]
        # Expected transformation:
        # Apply deletion first: "abcdef" -> "abef"
        # Then apply insertion transformed at pos 2, yielding "abXYZef"
        expected_document = "abXYZef"
        expected_transformed = [
            (1, 2, "cd", DELETE),
            (2, 2, "XYZ", INSERT)
        ]
        updated_document, transformed_operations = apply_operations(current_document, operations)
        self.assertEqual(updated_document, expected_document)
        self.assertEqual(transformed_operations, expected_transformed)

if __name__ == '__main__':
    unittest.main()