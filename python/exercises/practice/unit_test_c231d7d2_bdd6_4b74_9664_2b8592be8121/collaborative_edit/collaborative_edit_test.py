import unittest
from collaborative_edit import process_operations

class CollaborativeEditTest(unittest.TestCase):
    def test_basic_insert(self):
        operations = [
            {"user_id": 1, "timestamp": 1000, "type": "insert", "index": 0, "content": "First Paragraph"}
        ]
        expected_document = ["First Paragraph"]
        self.assertEqual(process_operations(operations), expected_document)

    def test_conflicting_inserts_same_index(self):
        # Two insert operations at the same index. Conflict resolved by user_id (lower wins).
        operations = [
            {"user_id": 2, "timestamp": 1000, "type": "insert", "index": 0, "content": "B Paragraph"},
            {"user_id": 1, "timestamp": 1000, "type": "insert", "index": 0, "content": "A Paragraph"}
        ]
        # Expect only the operation from user 1 to be applied.
        expected_document = ["A Paragraph"]
        self.assertEqual(process_operations(operations), expected_document)

    def test_edit_over_delete_conflict(self):
        # Insert a paragraph, then an edit and a delete on the same index.
        operations = [
            {"user_id": 1, "timestamp": 1000, "type": "insert", "index": 0, "content": "Original Paragraph"},
            {"user_id": 1, "timestamp": 2000, "type": "edit", "index": 0, "content": "Edited Paragraph"},
            {"user_id": 2, "timestamp": 3000, "type": "delete", "index": 0, "content": None},
        ]
        # Since edit is non-destructive, it should override the delete.
        expected_document = ["Edited Paragraph"]
        self.assertEqual(process_operations(operations), expected_document)

    def test_out_of_order_operations(self):
        # Operations provided in unsorted order. The system must process them correctly.
        operations = [
            {"user_id": 1, "timestamp": 3000, "type": "edit", "index": 0, "content": "P1 edited"},
            {"user_id": 1, "timestamp": 1000, "type": "insert", "index": 0, "content": "P1"},
            {"user_id": 2, "timestamp": 2000, "type": "insert", "index": 1, "content": "P2"},
        ]
        # Expected: index 0 becomes "P1 edited" and index 1 is "P2"
        expected_document = ["P1 edited", "P2"]
        self.assertEqual(process_operations(operations), expected_document)

    def test_same_timestamp_tie_break(self):
        # Two insert operations at the same index and same timestamp should be resolved by user_id.
        operations = [
            {"user_id": 2, "timestamp": 1000, "type": "insert", "index": 0, "content": "B Paragraph"},
            {"user_id": 1, "timestamp": 1000, "type": "insert", "index": 0, "content": "A Paragraph"}
        ]
        # Expect the paragraph from user_id 1 to be chosen.
        expected_document = ["A Paragraph"]
        self.assertEqual(process_operations(operations), expected_document)

    def test_multiple_operations_complex(self):
        # A complex sequence of operations involving multiple indices.
        operations = [
            # Insert two paragraphs
            {"user_id": 1, "timestamp": 1000, "type": "insert", "index": 0, "content": "Paragraph 1"},
            {"user_id": 2, "timestamp": 1100, "type": "insert", "index": 1, "content": "Paragraph 2"},
            # Conflicting insert at index 1; lower user_id wins.
            {"user_id": 1, "timestamp": 1200, "type": "insert", "index": 1, "content": "Paragraph 1.5"},
            # Edit first paragraph
            {"user_id": 3, "timestamp": 1300, "type": "edit", "index": 0, "content": "Paragraph 1 edited"},
            # Delete second paragraph but then an edit comes to save it.
            {"user_id": 2, "timestamp": 1400, "type": "delete", "index": 1, "content": None},
            {"user_id": 2, "timestamp": 1500, "type": "edit", "index": 1, "content": "Paragraph 2 restored"},
            # Insert another paragraph at the end
            {"user_id": 4, "timestamp": 1600, "type": "insert", "index": 2, "content": "Paragraph 3"}
        ]
        # Expected resolution:
        # - At index 0: "Paragraph 1 edited"
        # - At index 1: Because of conflicting insert, user_id 1's "Paragraph 1.5" should win initially.
        #   Then deletion and subsequent edit are applied. Given that edit takes precedence over delete,
        #   the final content should be "Paragraph 2 restored".
        # - At index 2: "Paragraph 3"
        expected_document = ["Paragraph 1 edited", "Paragraph 2 restored", "Paragraph 3"]
        self.assertEqual(process_operations(operations), expected_document)

if __name__ == '__main__':
    unittest.main()