import unittest
from collab_edit import Peer

class TestCollabEdit(unittest.TestCase):
    def test_initial_document(self):
        peer = Peer("peer1", "")
        self.assertEqual(peer.get_document(), "")
        
    def test_local_insert(self):
        peer = Peer("peer1", "hello")
        # Insert at beginning
        peer.local_insert(0, "A")
        self.assertEqual(peer.get_document(), "Ahello")
        # Insert at position beyond current length; should append.
        peer.local_insert(10, "B")
        self.assertEqual(peer.get_document(), "AhelloB")
    
    def test_local_delete(self):
        peer = Peer("peer1", "abcdef")
        # Delete character at position 2 ('c')
        peer.local_delete(2)
        self.assertEqual(peer.get_document(), "abdef")
        # Attempt to delete at an out-of-bound position; document remains unchanged.
        peer.local_delete(10)
        self.assertEqual(peer.get_document(), "abdef")
    
    def test_receive_operation_insert(self):
        peer = Peer("peer1", "world")
        # Simulate an external insert operation at position 0.
        operation = {"type": "insert", "position": 0, "char": "H"}
        peer.receive_operation(operation, "peer2")
        self.assertEqual(peer.get_document(), "Hworld")
    
    def test_receive_operation_delete(self):
        peer = Peer("peer1", "hello")
        # Simulate an external delete operation at position 1 (remove 'e')
        operation = {"type": "delete", "position": 1}
        peer.receive_operation(operation, "peer2")
        self.assertEqual(peer.get_document(), "hllo")
    
    def test_causality_preservation(self):
        # Simulate out-of-order arrival of operations.
        peer = Peer("peer1", "abcd")
        op_insert = {"type": "insert", "position": 2, "char": "X"}
        op_delete = {"type": "delete", "position": 1}
        # Receive deletion then insertion.
        peer.receive_operation(op_delete, "peer2")
        peer.receive_operation(op_insert, "peer2")
        # Expected transformation:
        # Original: "abcd" -> after deletion at pos1: "acd"
        # Then insert "X" at pos2: "acXd"
        self.assertEqual(peer.get_document(), "acXd")
    
    def test_multiple_peers_consistency(self):
        # Simulate two peers exchanging operations.
        peer1 = Peer("peer1", "")
        peer2 = Peer("peer2", "")
        
        # Peer1 performs a local insert; broadcast the same operation to peer2.
        peer1.local_insert(0, "A")
        op1 = {"type": "insert", "position": 0, "char": "A"}
        peer2.receive_operation(op1, "peer1")
        
        # Peer2 performs a local insert at position 1; broadcast the same to peer1.
        peer2.local_insert(1, "B")
        op2 = {"type": "insert", "position": 1, "char": "B"}
        peer1.receive_operation(op2, "peer2")
        
        self.assertEqual(peer1.get_document(), "AB")
        self.assertEqual(peer2.get_document(), "AB")
    
    def test_out_of_bound_insert(self):
        peer = Peer("peer1", "123")
        # Inserting at an index greater than length should append the character.
        peer.local_insert(10, "4")
        self.assertEqual(peer.get_document(), "1234")
        
    def test_delete_on_empty_document(self):
        peer = Peer("peer1", "")
        # Deletion on an empty document should have no effect.
        peer.local_delete(0)
        self.assertEqual(peer.get_document(), "")
    
    def test_conflict_resolution(self):
        # Simulate a conflict: both deletion and insertion at nearly the same position.
        peer = Peer("peer1", "abcd")
        op_delete = {"type": "delete", "position": 1}
        op_insert = {"type": "insert", "position": 1, "char": "X"}
        # Apply deletion then insertion.
        peer.receive_operation(op_delete, "peer2")
        peer.receive_operation(op_insert, "peer2")
        # Result: "abcd" -> deletion at pos1 gives "acd"; then insertion at pos1 gives "aXcd".
        self.assertEqual(peer.get_document(), "aXcd")

if __name__ == '__main__':
    unittest.main()