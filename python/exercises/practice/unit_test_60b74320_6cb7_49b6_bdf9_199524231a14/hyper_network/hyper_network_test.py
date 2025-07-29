import unittest
import threading
import time
from hyper_network import HyperSocialNetwork

class TestHyperSocialNetwork(unittest.TestCase):
    def setUp(self):
        self.network = HyperSocialNetwork()
        
    def test_create_user_basic(self):
        # Test creating a new user
        result = self.network.create_user(1)
        self.assertTrue(result, "Should return True when creating a new user")
        
        # Test creating a duplicate user
        result = self.network.create_user(1)
        self.assertFalse(result, "Should return False when creating a duplicate user")
    
    def test_create_group_basic(self):
        # Create users first
        self.network.create_user(1)
        self.network.create_user(2)
        
        # Test creating a new group with valid users
        result = self.network.create_group(10, [1, 2])
        self.assertTrue(result, "Should return True when creating a new group with valid users")
        
        # Test creating a duplicate group
        result = self.network.create_group(10, [1])
        self.assertFalse(result, "Should return False when creating a duplicate group")
        
        # Test creating a group with non-existent user
        result = self.network.create_group(20, [1, 3])
        self.assertFalse(result, "Should return False when creating a group with non-existent user")
    
    def test_record_interaction_basic(self):
        # Setup users and groups
        self.network.create_user(1)
        self.network.create_user(2)
        self.network.create_group(10, [1])
        self.network.create_group(20, [2])
        
        # Test recording a valid interaction
        result = self.network.record_interaction([10, 20], 100)
        self.assertTrue(result, "Should return True when recording a valid interaction")
        
        # Test recording an interaction with a non-existent group
        result = self.network.record_interaction([10, 30], 150)
        self.assertFalse(result, "Should return False when recording an interaction with a non-existent group")
        
        # Test recording an interaction with a timestamp less than the previous
        result = self.network.record_interaction([10, 20], 50)
        self.assertFalse(result, "Should return False when recording an interaction with earlier timestamp")
        
        # Test recording an interaction with a timestamp equal to the previous
        result = self.network.record_interaction([10, 20], 100)
        self.assertFalse(result, "Should return False when recording an interaction with same timestamp")
        
        # Test recording another valid interaction with a later timestamp
        result = self.network.record_interaction([20, 10], 200)
        self.assertTrue(result, "Should return True when recording a valid interaction with later timestamp")
    
    def test_get_interacting_groups_basic(self):
        # Setup network
        self.network.create_user(1)
        self.network.create_user(2)
        self.network.create_user(3)
        self.network.create_group(10, [1])
        self.network.create_group(20, [2])
        self.network.create_group(30, [3])
        
        # Record interactions
        self.network.record_interaction([10, 20], 100)
        self.network.record_interaction([30, 20], 150)
        self.network.record_interaction([10, 30], 200)
        
        # Test getting interacting groups
        result = self.network.get_interacting_groups(20, 0, 300)
        self.assertEqual(result, [10, 30], "Should return groups that interacted with group 20")
        
        # Test with time range
        result = self.network.get_interacting_groups(20, 0, 120)
        self.assertEqual(result, [10], "Should return only groups that interacted with group 20 in time range")
        
        # Test with no interactions
        result = self.network.get_interacting_groups(10, 0, 300)
        self.assertEqual(result, [], "Should return empty list when no groups interacted with the target")
    
    def test_get_interaction_path_basic(self):
        # Setup network
        self.network.create_user(1)
        self.network.create_user(2)
        self.network.create_user(3)
        self.network.create_user(4)
        self.network.create_group(10, [1])
        self.network.create_group(20, [2])
        self.network.create_group(30, [3])
        self.network.create_group(40, [4])
        
        # Record interactions
        self.network.record_interaction([10, 20], 100)
        self.network.record_interaction([20, 30], 150)
        self.network.record_interaction([30, 40], 200)
        
        # Test direct path
        result = self.network.get_interaction_path(10, 20, 1, 0, 300)
        self.assertEqual(result, [10, 20], "Should find direct path from group 10 to 20")
        
        # Test multi-step path
        result = self.network.get_interaction_path(10, 30, 2, 0, 300)
        self.assertEqual(result, [10, 20, 30], "Should find path from group 10 to 30 through 20")
        
        # Test path with max length constraint
        result = self.network.get_interaction_path(10, 40, 2, 0, 300)
        self.assertEqual(result, [], "Should return empty list when path exists but exceeds max length")
        
        # Test path with sufficient max length
        result = self.network.get_interaction_path(10, 40, 3, 0, 300)
        self.assertEqual(result, [10, 20, 30, 40], "Should find path from group 10 to 40")
        
        # Test path with time range constraint
        result = self.network.get_interaction_path(10, 30, 2, 0, 120)
        self.assertEqual(result, [], "Should return empty list when path doesn't exist within time range")
        
        # Test non-existent path
        self.network.create_group(50, [1])
        result = self.network.get_interaction_path(50, 40, 10, 0, 300)
        self.assertEqual(result, [], "Should return empty list when no path exists")
    
    def test_complex_scenario(self):
        # Setup a more complex network
        for i in range(1, 11):
            self.network.create_user(i)
        
        self.network.create_group(10, [1, 2])
        self.network.create_group(20, [3, 4])
        self.network.create_group(30, [5, 6])
        self.network.create_group(40, [7, 8])
        self.network.create_group(50, [9, 10])
        
        # Record a complex set of interactions
        self.network.record_interaction([10, 20], 100)
        self.network.record_interaction([20, 30], 150)
        self.network.record_interaction([10, 40], 200)
        self.network.record_interaction([40, 50], 250)
        self.network.record_interaction([30, 50], 300)
        self.network.record_interaction([20, 50], 350)
        
        # Test various paths
        # Should find shortest path 10->20->50
        result = self.network.get_interaction_path(10, 50, 5, 0, 400)
        possible_paths = [[10, 20, 50], [10, 40, 50]]
        self.assertIn(result, possible_paths, "Should find one of the shortest paths")
        
        # Test with time constraint
        result = self.network.get_interaction_path(10, 50, 5, 0, 300)
        self.assertEqual(result, [10, 40, 50], "Should find path respecting time constraint")
        
        # Test multiple interacting groups
        result = self.network.get_interacting_groups(50, 0, 400)
        self.assertEqual(result, [20, 30, 40], "Should return all groups that interacted with 50")
    
    def test_concurrent_operations(self):
        # Setup initial network
        for i in range(1, 6):
            self.network.create_user(i)
        
        self.network.create_group(10, [1])
        self.network.create_group(20, [2])
        self.network.create_group(30, [3])
        
        # Define functions for thread operations
        def record_interactions():
            for i in range(100, 200, 10):
                self.network.record_interaction([10, 20], i)
                time.sleep(0.001)  # Small delay to ensure timestamp ordering
        
        def query_interactions():
            for _ in range(20):
                self.network.get_interacting_groups(20, 0, 300)
                time.sleep(0.001)
        
        def create_entities():
            for i in range(100, 110):
                self.network.create_user(i)
                self.network.create_group(i, [i])
                time.sleep(0.001)
        
        # Create and start threads
        threads = [
            threading.Thread(target=record_interactions),
            threading.Thread(target=query_interactions),
            threading.Thread(target=create_entities)
        ]
        
        for thread in threads:
            thread.start()
        
        for thread in threads:
            thread.join()
        
        # Verify that the network is still functional
        # Check if we can still record interactions
        result = self.network.record_interaction([10, 20], 300)
        self.assertTrue(result, "Should be able to record interaction after concurrent operations")
        
        # Check if we can still query
        interacting_groups = self.network.get_interacting_groups(20, 0, 400)
        self.assertIn(10, interacting_groups, "Should return correct results after concurrent operations")
    
    def test_edge_cases(self):
        # Setup
        self.network.create_user(1)
        self.network.create_user(2)
        self.network.create_group(10, [1])
        self.network.create_group(20, [2])
        
        # Test empty group IDs for interaction
        result = self.network.record_interaction([], 100)
        self.assertFalse(result, "Should return False when recording interaction with empty group IDs")
        
        # Test interaction with self
        result = self.network.record_interaction([10, 10], 100)
        self.assertTrue(result, "Should allow self-interaction")
        
        # Test create_group with no users
        result = self.network.create_group(30, [])
        self.assertTrue(result, "Should allow creating a group with no users")
        
        # Test get_interacting_groups with start_time equal to end_time
        result = self.network.get_interacting_groups(10, 100, 100)
        self.assertEqual(result, [], "Should return empty list when start_time equals end_time")
        
        # Test get_interaction_path with start and end being the same group
        result = self.network.get_interaction_path(10, 10, 1, 0, 200)
        # What the expected result should be depends on the implementation
        # If self-loops are not considered paths, this should be an empty list
        # If self-loops are considered paths and we have recorded a self-interaction, this should be [10, 10]
        
        # Test get_interaction_path with max_length of 0
        with self.assertRaises(ValueError):
            self.network.get_interaction_path(10, 20, 0, 0, 100)
    
    def test_large_scale(self):
        # Create a moderate number of users and groups
        for i in range(1, 101):
            self.network.create_user(i)
        
        for i in range(1, 31):
            self.network.create_group(i, [i, i+1, i+2])
        
        # Record many interactions
        timestamp = 100
        for i in range(1, 29):
            self.network.record_interaction([i, i+1], timestamp)
            timestamp += 10
        
        # Test path finding in a long chain
        result = self.network.get_interaction_path(1, 15, 20, 0, 1000)
        expected_length = 15  # [1, 2, 3, ..., 15]
        self.assertEqual(len(result), expected_length, "Should find correct path length in a chain")
        
        # Test path finding with limited max_length
        result = self.network.get_interaction_path(1, 15, 10, 0, 1000)
        self.assertEqual(result, [], "Should return empty list when path exists but exceeds max length")
        
        # Test get_interacting_groups with many interactions
        result = self.network.get_interacting_groups(15, 0, 1000)
        self.assertEqual(result, [14], "Should return correct interacting groups even with many interactions")

if __name__ == '__main__':
    unittest.main()