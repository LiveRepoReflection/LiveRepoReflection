import unittest
from collaborative_editor import Server, Client, InsertOperation, DeleteOperation, Document

class TestCollaborativeEditor(unittest.TestCase):
    def setUp(self):
        # Initialize the server with a simple document.
        self.server = Server(initial_document="Hello World")
        # Create two clients associated with the server.
        self.client1 = Client(server=self.server, client_id="client1")
        self.client2 = Client(server=self.server, client_id="client2")

    def test_single_client_insert(self):
        # Client1 inserts a comma into the document.
        op = InsertOperation(position=5, text=",")
        self.client1.send_operation(op)
        self.server.process_all_operations()
        expected = "Hello, World"
        self.assertEqual(self.server.document.content, expected)
        self.assertEqual(self.client1.document.content, expected)
        self.assertEqual(self.client2.document.content, expected)

    def test_concurrent_inserts_same_position(self):
        # Both clients insert different characters at the same position concurrently.
        op1 = InsertOperation(position=6, text="A")
        op2 = InsertOperation(position=6, text="B")
        self.client1.send_operation(op1)
        self.client2.send_operation(op2)
        self.server.process_all_operations()
        result = self.server.document.content
        self.assertTrue("A" in result and "B" in result)
        self.assertEqual(len(result), len("Hello World") + 2)

    def test_concurrent_insert_and_delete(self):
        # Client1 deletes a substring while Client2 inserts text inside that region concurrently.
        op1 = DeleteOperation(position=6, length=5)
        op2 = InsertOperation(position=8, text="Everyone")
        self.client1.send_operation(op1)
        self.client2.send_operation(op2)
        self.server.process_all_operations()
        result = self.server.document.content
        self.assertEqual(self.client1.document.content, result)
        self.assertEqual(self.client2.document.content, result)
        self.assertTrue("Everyone" in result or result.count("Everyone") == 1)

    def test_overlapping_deletes(self):
        # Both clients delete overlapping parts of the document.
        op1 = DeleteOperation(position=0, length=6)
        op2 = DeleteOperation(position=3, length=4)
        self.client1.send_operation(op1)
        self.client2.send_operation(op2)
        self.server.process_all_operations()
        self.assertEqual(self.client1.document.content, self.server.document.content)
        self.assertEqual(self.client2.document.content, self.server.document.content)
        self.assertTrue(len(self.server.document.content) < len("Hello World"))

    def test_edge_insertions(self):
        # Insertions at the beginning and end of the document.
        op1 = InsertOperation(position=0, text="Start-")
        op2 = InsertOperation(position=len(self.server.document.content), text="-End")
        self.client1.send_operation(op1)
        self.client1.send_operation(op2)
        self.server.process_all_operations()
        expected = "Start-Hello World-End"
        self.assertEqual(self.server.document.content, expected)

    def test_acknowledgement_and_sync(self):
        # Multiple operations sent from a client should be acknowledged and applied atomically.
        op1 = InsertOperation(position=5, text="X")
        op2 = DeleteOperation(position=3, length=2)
        self.client1.send_operation(op1)
        self.client1.send_operation(op2)
        pre_sync = self.client1.document.content
        self.server.process_all_operations()
        sync_state = self.server.document.content
        self.assertEqual(self.client1.document.content, sync_state)
        self.assertEqual(self.client2.document.content, sync_state)
        self.assertNotEqual(pre_sync, sync_state)

    def test_large_document_operations(self):
        # Evaluate operations on a large document.
        large_text = "a" * 10000
        self.server.document = Document(content=large_text)
        op1 = InsertOperation(position=5000, text="b" * 100)
        op2 = DeleteOperation(position=4000, length=200)
        self.client1.send_operation(op1)
        self.client2.send_operation(op2)
        self.server.process_all_operations()
        final_content = self.server.document.content
        self.assertEqual(self.client1.document.content, final_content)
        self.assertEqual(self.client2.document.content, final_content)
        expected_length = 10000 + 100 - 200
        self.assertEqual(len(final_content), expected_length)

if __name__ == "__main__":
    unittest.main()