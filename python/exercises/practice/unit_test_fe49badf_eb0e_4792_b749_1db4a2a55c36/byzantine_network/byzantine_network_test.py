import unittest
from unittest.mock import patch, MagicMock
import random
from byzantine_network import solve_byzantine_agreement

class TestByzantineNetwork(unittest.TestCase):
    
    def test_simple_all_true_proposals_reliable_network(self):
        """Test with all nodes proposing True and perfect communication."""
        def reliable_channel(destination_id, message):
            return message
        
        result = solve_byzantine_agreement(4, 1, True, reliable_channel, 10)
        self.assertEqual(result, True)
    
    def test_simple_all_false_proposals_reliable_network(self):
        """Test with all nodes proposing False and perfect communication."""
        def reliable_channel(destination_id, message):
            return message
        
        result = solve_byzantine_agreement(4, 1, False, reliable_channel, 10)
        self.assertEqual(result, False)
    
    def test_partially_reliable_network(self):
        """Test with a network that drops 20% of messages."""
        random.seed(42)  # For reproducibility
        
        def partially_reliable_channel(destination_id, message):
            if random.random() < 0.2:  # 20% message loss
                return None
            return message
        
        result = solve_byzantine_agreement(7, 2, True, partially_reliable_channel, 20)
        self.assertEqual(result, True)
    
    def test_network_partition_recovery(self):
        """Test with simulated network partitions that heal over time."""
        partition_counter = [0]  # Using list to allow modification in closure
        
        def partitioned_network(destination_id, message):
            # Simulate partitions in first half of the rounds, then recover
            if partition_counter[0] < 5:
                if destination_id % 2 == 0:  # Even nodes can't receive messages
                    partition_counter[0] += 1
                    return None
            return message
        
        result = solve_byzantine_agreement(7, 2, True, partitioned_network, 20)
        self.assertEqual(result, True)
    
    def test_byzantine_behavior(self):
        """Test with simulated Byzantine nodes that send conflicting messages."""
        def byzantine_channel(destination_id, message):
            # Simulate byzantine behavior for certain destinations
            if destination_id == 2 and isinstance(message, bool):
                return not message  # Flip the boolean for node 2
            return message
        
        result = solve_byzantine_agreement(7, 2, True, byzantine_channel, 20)
        self.assertEqual(result, True)
    
    def test_complex_network_conditions(self):
        """Test with a combination of message loss, partitions, and Byzantine behavior."""
        random.seed(42)  # For reproducibility
        round_count = [0]  # Using list to allow modification in closure
        
        def complex_channel(destination_id, message):
            current_round = round_count[0]
            
            # Every message increments our round counter
            round_count[0] += 1
            
            # Simulate network partition in early rounds
            if current_round < 50 and destination_id > 3:
                return None
            
            # Simulate random message loss
            if random.random() < 0.3:
                return None
            
            # Simulate Byzantine behavior for certain nodes
            if destination_id == 1 and isinstance(message, bool):
                return not message  # Flip booleans sent to node 1
            
            return message
        
        result = solve_byzantine_agreement(10, 3, True, complex_channel, 30)
        self.assertEqual(result, True)
    
    def test_majority_false_proposals(self):
        """Test with majority of nodes proposing False."""
        proposal_map = {0: False, 1: False, 2: False, 3: True}
        
        # Patch the solve_byzantine_agreement to test with different initial proposals
        with patch('byzantine_network.solve_byzantine_agreement') as mock_solve:
            mock_solve.side_effect = lambda n, f, initial_proposal, comm_channel, max_rounds: \
                self._simulate_multiple_nodes(n, f, proposal_map.get(0, False), comm_channel, max_rounds, proposal_map)
            
            def reliable_channel(destination_id, message):
                return message
            
            result = solve_byzantine_agreement(4, 1, proposal_map[0], reliable_channel, 10)
            self.assertEqual(result, False)
    
    def test_exact_threshold(self):
        """Test with exactly n=3f+1 nodes."""
        def reliable_channel(destination_id, message):
            return message
        
        result = solve_byzantine_agreement(7, 2, True, reliable_channel, 10)
        self.assertEqual(result, True)
    
    def test_high_message_loss(self):
        """Test with very high message loss rate, requiring retransmissions."""
        random.seed(42)  # For reproducibility
        
        def unreliable_channel(destination_id, message):
            if random.random() < 0.7:  # 70% message loss
                return None
            return message
        
        result = solve_byzantine_agreement(7, 2, True, unreliable_channel, 30)
        self.assertEqual(result, True)
    
    def test_timeout_exceeded(self):
        """Test behavior when max_rounds is exceeded."""
        def slow_channel(destination_id, message):
            # This will cause the algorithm to need many rounds
            if random.random() < 0.9:  # 90% message loss
                return None
            return message
        
        # With very limited rounds, expect the algorithm to still terminate
        # with some reasonable default value (implementation-specific)
        result = solve_byzantine_agreement(7, 2, True, slow_channel, 3)
        self.assertIsInstance(result, bool)  # Should return some boolean decision

    def _simulate_multiple_nodes(self, n, f, default_proposal, comm_channel, max_rounds, proposal_map):
        """Helper to simulate multiple nodes with different initial proposals."""
        # This would be a simplified simulation - in reality nodes would run in parallel
        # This is just to test the behavior with different initial proposals
        
        # In a real implementation, this would launch multiple processes or threads
        # For testing purposes, we'll assume agreement would be reached based on majority
        
        true_count = sum(1 for node_id, proposal in proposal_map.items() if proposal is True)
        false_count = sum(1 for node_id, proposal in proposal_map.items() if proposal is False)
        
        # Simple majority rule for testing purposes
        return true_count > false_count


if __name__ == '__main__':
    unittest.main()