import unittest
from byzantine_broadcast import byzantine_broadcast

class ByzantineBroadcastTest(unittest.TestCase):
    def test_single_node_no_messages(self):
        """Test with a single node system (trivial case)."""
        result = byzantine_broadcast(1, 0, 1, [])
        self.assertEqual(result, 1)
    
    def test_no_byzantine_nodes_small(self):
        """Test with a small system where all nodes are loyal."""
        n = 4
        sender_id = 0
        initial_value = 1
        # All nodes relay the correct value
        messages = [
            (0, 1, 1),  # Sender to node 1
            (0, 2, 1),  # Sender to node 2
            (0, 3, 1),  # Sender to node 3
            (1, 2, 1),  # Node 1 to node 2
            (1, 3, 1),  # Node 1 to node 3
            (2, 1, 1),  # Node 2 to node 1
            (2, 3, 1),  # Node 2 to node 3
            (3, 1, 1),  # Node 3 to node 1
            (3, 2, 1),  # Node 3 to node 2
        ]
        result = byzantine_broadcast(n, sender_id, initial_value, messages)
        self.assertEqual(result, 1)
    
    def test_no_byzantine_nodes_zero_value(self):
        """Test with all loyal nodes and initial value of 0."""
        n = 4
        sender_id = 0
        initial_value = 0
        messages = [
            (0, 1, 0),  # Sender to node 1
            (0, 2, 0),  # Sender to node 2
            (0, 3, 0),  # Sender to node 3
            (1, 2, 0),  # Node 1 to node 2
            (1, 3, 0),  # Node 1 to node 3
            (2, 1, 0),  # Node 2 to node 1
            (2, 3, 0),  # Node 2 to node 3
            (3, 1, 0),  # Node 3 to node 1
            (3, 2, 0),  # Node 3 to node 2
        ]
        result = byzantine_broadcast(n, sender_id, initial_value, messages)
        self.assertEqual(result, 0)

    def test_one_byzantine_node_sender_loyal(self):
        """Test with one Byzantine node (not the sender)."""
        n = 4
        sender_id = 0
        initial_value = 1
        # Node 3 is Byzantine and sends conflicting values
        messages = [
            (0, 1, 1),  # Sender to node 1
            (0, 2, 1),  # Sender to node 2
            (0, 3, 1),  # Sender to node 3
            (1, 2, 1),  # Node 1 to node 2
            (1, 3, 1),  # Node 1 to node 3
            (2, 1, 1),  # Node 2 to node 1
            (2, 3, 1),  # Node 2 to node 3
            (3, 1, 0),  # Byzantine node 3 to node 1 (incorrect)
            (3, 2, 1),  # Byzantine node 3 to node 2 (correct)
        ]
        result = byzantine_broadcast(n, sender_id, initial_value, messages)
        self.assertEqual(result, 1)
    
    def test_byzantine_sender(self):
        """Test with the sender being Byzantine."""
        n = 7  # Need more nodes to tolerate f=2 Byzantine nodes
        sender_id = 0
        initial_value = 1  # This value should be ignored as sender is Byzantine
        
        # Sender sends conflicting values
        messages = [
            (0, 1, 1),  # Sender to node 1
            (0, 2, 0),  # Sender to node 2 (different value)
            (0, 3, 1),  # Sender to node 3
            (0, 4, 0),  # Sender to node 4 (different value)
            (0, 5, 1),  # Sender to node 5
            (0, 6, 0),  # Sender to node 6 (different value)
            
            # First round relays (nodes report what they received from sender)
            (1, 2, 1), (1, 3, 1), (1, 4, 1), (1, 5, 1), (1, 6, 1),
            (2, 1, 0), (2, 3, 0), (2, 4, 0), (2, 5, 0), (2, 6, 0),
            (3, 1, 1), (3, 2, 1), (3, 4, 1), (3, 5, 1), (3, 6, 1),
            (4, 1, 0), (4, 2, 0), (4, 3, 0), (4, 5, 0), (4, 6, 0),
            (5, 1, 1), (5, 2, 1), (5, 3, 1), (5, 4, 1), (5, 6, 1),
            (6, 1, 0), (6, 2, 0), (6, 3, 0), (6, 4, 0), (6, 5, 0),
        ]
        
        # Since the sender is Byzantine and sent equal numbers of 0s and 1s,
        # we don't specifically test for the exact returned value, just that it's binary
        result = byzantine_broadcast(n, sender_id, initial_value, messages)
        self.assertIn(result, [0, 1])
    
    def test_multiple_byzantine_nodes(self):
        """Test with multiple Byzantine nodes but less than n/3."""
        n = 10
        sender_id = 0
        initial_value = 1
        
        # Let's say nodes 7, 8, 9 are Byzantine
        messages = []
        
        # Sender sends correct value to all
        for i in range(1, n):
            messages.append((0, i, 1))
        
        # Loyal nodes relay correctly
        for i in range(1, 7):
            for j in range(1, n):
                if i != j:
                    messages.append((i, j, 1))
        
        # Byzantine nodes 7, 8, 9 send conflicting values
        for i in range(7, 10):
            for j in range(n):
                if i != j:
                    # Byzantine node sends 0 to half the nodes and 1 to the other half
                    value = 0 if j % 2 == 0 else 1
                    messages.append((i, j, value))
        
        result = byzantine_broadcast(n, sender_id, initial_value, messages)
        self.assertEqual(result, 1)
    
    def test_edge_case_maximum_tolerable_failures(self):
        """Test with exactly n/3-1 Byzantine nodes."""
        n = 10  # Can tolerate 3 Byzantine nodes
        sender_id = 0
        initial_value = 0
        
        # Nodes 7, 8, 9 are Byzantine
        messages = []
        
        # Sender sends correct value to all
        for i in range(1, n):
            messages.append((0, i, 0))
        
        # Loyal nodes relay correctly
        for i in range(1, 7):
            for j in range(n):
                if i != j:
                    messages.append((i, j, 0))
        
        # Byzantine nodes sending all 1s (incorrect)
        for i in range(7, 10):
            for j in range(n):
                if i != j:
                    messages.append((i, j, 1))
        
        result = byzantine_broadcast(n, sender_id, initial_value, messages)
        self.assertEqual(result, 0)
    
    def test_partial_messages(self):
        """Test with incomplete message set (some messages not delivered)."""
        n = 7
        sender_id = 0
        initial_value = 1
        
        # Only some messages are delivered
        messages = [
            (0, 1, 1),
            (0, 2, 1),
            (0, 3, 1),
            # Missing messages to nodes 4, 5, 6
            (1, 2, 1),
            (1, 4, 1),
            # Missing other relays
            (2, 3, 1),
            (2, 6, 1),
            (3, 5, 1),
            (4, 6, 1),
        ]
        
        result = byzantine_broadcast(n, sender_id, initial_value, messages)
        self.assertEqual(result, 1)
    
    def test_larger_network(self):
        """Test with a larger network to ensure scalability."""
        n = 16
        sender_id = 0
        initial_value = 0
        
        # Limited messages for test feasibility
        messages = []
        
        # Sender sends to all
        for i in range(1, n):
            messages.append((0, i, 0))
        
        # Only select relays to keep test size manageable
        for i in range(1, n):
            # Each node relays to 5 random other nodes
            for j in range(1, 6):
                target = (i + j) % n
                if target != i:
                    messages.append((i, target, 0))
        
        # Byzantine behavior from nodes 13, 14, 15 (less than n/3)
        for i in range(13, 16):
            for j in range(n):
                if j != i and j < 8:  # Send incorrect values to half the nodes
                    messages.append((i, j, 1))
        
        result = byzantine_broadcast(n, sender_id, initial_value, messages)
        self.assertEqual(result, 0)

    def test_incomplete_communication_rounds(self):
        """Test with insufficient message rounds for traditional Byzantine agreement."""
        n = 7
        sender_id = 0
        initial_value = 1
        
        # Only first round messages (not enough for complete Byzantine agreement)
        messages = [
            (0, 1, 1),
            (0, 2, 1),
            (0, 3, 1),
            (0, 4, 1),
            (0, 5, 1),
            (0, 6, 1),
            # No second or third round messages
        ]
        
        # The algorithm should still make a best-effort decision
        result = byzantine_broadcast(n, sender_id, initial_value, messages)
        self.assertEqual(result, 1)

if __name__ == '__main__':
    unittest.main()