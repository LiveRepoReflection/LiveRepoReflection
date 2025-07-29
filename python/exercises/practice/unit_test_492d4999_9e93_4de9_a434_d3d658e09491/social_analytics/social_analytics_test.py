import unittest
import uuid
from unittest.mock import MagicMock
from social_analytics import get_mutual_friends, find_shortest_path, detect_community

class SocialAnalyticsTest(unittest.TestCase):
    def setUp(self):
        # Create fixed UUIDs for testing
        self.user1 = str(uuid.uuid4())
        self.user2 = str(uuid.uuid4())
        self.user3 = str(uuid.uuid4())
        self.user4 = str(uuid.uuid4())
        self.user5 = str(uuid.uuid4())
        self.user6 = str(uuid.uuid4())
        self.user7 = str(uuid.uuid4())
        self.user8 = str(uuid.uuid4())
        
        # Create mock DHT data
        self.mock_data = {
            self.user1: {
                "profile": {"name": "User 1"},
                "connections": [self.user2, self.user3, self.user4]
            },
            self.user2: {
                "profile": {"name": "User 2"},
                "connections": [self.user1, self.user3, self.user5]
            },
            self.user3: {
                "profile": {"name": "User 3"},
                "connections": [self.user1, self.user2, self.user4, self.user5]
            },
            self.user4: {
                "profile": {"name": "User 4"},
                "connections": [self.user1, self.user3, self.user6]
            },
            self.user5: {
                "profile": {"name": "User 5"},
                "connections": [self.user2, self.user3, self.user7]
            },
            self.user6: {
                "profile": {"name": "User 6"},
                "connections": [self.user4, self.user8]
            },
            self.user7: {
                "profile": {"name": "User 7"},
                "connections": [self.user5]
            },
            self.user8: {
                "profile": {"name": "User 8"},
                "connections": [self.user6]
            }
        }
        
        # Mock DHT query function
        self.dht_query = MagicMock(side_effect=lambda user_id: self.mock_data.get(user_id))

    def test_get_mutual_friends_basic(self):
        # User1 and User2 have User3 as a mutual friend
        mutual = get_mutual_friends(self.user1, self.user2, self.dht_query)
        self.assertEqual(mutual, {self.user3})
        
        # Verify we only made necessary DHT queries
        self.assertLessEqual(self.dht_query.call_count, 2)
        self.dht_query.reset_mock()

    def test_get_mutual_friends_multiple(self):
        # User2 and User3 have User1 and User5 as mutual friends
        mutual = get_mutual_friends(self.user2, self.user3, self.dht_query)
        self.assertEqual(mutual, {self.user1, self.user5})
        
        # Verify we only made necessary DHT queries
        self.assertLessEqual(self.dht_query.call_count, 2)
        self.dht_query.reset_mock()

    def test_get_mutual_friends_none(self):
        # User7 and User8 have no mutual friends
        mutual = get_mutual_friends(self.user7, self.user8, self.dht_query)
        self.assertEqual(mutual, set())
        
        # Verify we only made necessary DHT queries
        self.assertLessEqual(self.dht_query.call_count, 2)
        self.dht_query.reset_mock()

    def test_get_mutual_friends_nonexistent_user(self):
        # Test with a user that doesn't exist
        nonexistent_id = str(uuid.uuid4())
        mutual = get_mutual_friends(self.user1, nonexistent_id, self.dht_query)
        self.assertEqual(mutual, set())
        
        # Verify we gracefully handle non-existent users
        self.dht_query.reset_mock()

    def test_find_shortest_path_direct(self):
        # Direct connection between User1 and User2
        path = find_shortest_path(self.user1, self.user2, self.dht_query)
        self.assertEqual(path, [self.user1, self.user2])
        self.dht_query.reset_mock()

    def test_find_shortest_path_one_hop(self):
        # Path from User1 to User5 via User2 or User3
        path = find_shortest_path(self.user1, self.user5, self.dht_query)
        self.assertEqual(len(path), 3)  # Should be 3 users in the path
        self.assertEqual(path[0], self.user1)
        self.assertEqual(path[-1], self.user5)
        # The middle node should be either User2 or User3
        self.assertIn(path[1], [self.user2, self.user3])
        self.dht_query.reset_mock()

    def test_find_shortest_path_two_hops(self):
        # Path from User1 to User7 via User3 and User5 or other valid paths
        path = find_shortest_path(self.user1, self.user7, self.dht_query)
        self.assertEqual(len(path), 4)  # Should be 4 users in the path
        self.assertEqual(path[0], self.user1)
        self.assertEqual(path[-1], self.user7)
        self.dht_query.reset_mock()

    def test_find_shortest_path_no_path(self):
        # No path should exist to a non-existent user
        nonexistent_id = str(uuid.uuid4())
        path = find_shortest_path(self.user1, nonexistent_id, self.dht_query)
        self.assertEqual(path, [])
        self.dht_query.reset_mock()

    def test_detect_community_threshold_1(self):
        # With threshold=1, community should include all users connected to User1
        community = detect_community(self.user1, self.dht_query, 1)
        expected_minimum = {self.user1, self.user2, self.user3, self.user4}
        # All expected users should be in the community
        for user in expected_minimum:
            self.assertIn(user, community)
        self.dht_query.reset_mock()

    def test_detect_community_threshold_2(self):
        # With threshold=2, community might be smaller and include only users with 2+ connections within community
        community = detect_community(self.user1, self.dht_query, 2)
        # This is a more complex test since the exact community depends on the implementation
        # We'll assert that key users are in the community and it's reasonable in size
        self.assertIn(self.user1, community)
        self.assertGreaterEqual(len(community), 3)  # Should include at least a few users
        self.dht_query.reset_mock()

    def test_detect_community_nonexistent_user(self):
        # Community detection should handle non-existent users gracefully
        nonexistent_id = str(uuid.uuid4())
        community = detect_community(nonexistent_id, self.dht_query, 1)
        self.assertEqual(community, set())
        self.dht_query.reset_mock()

    def test_detect_community_high_threshold(self):
        # Very high threshold should result in empty or very small community
        community = detect_community(self.user1, self.dht_query, 100)
        self.assertLessEqual(len(community), 1)  # Might include just the seed user or be empty
        self.dht_query.reset_mock()

    def test_query_efficiency_mutual_friends(self):
        # Reset the mock to track calls
        self.dht_query.reset_mock()
        
        # Test mutual friends
        get_mutual_friends(self.user1, self.user2, self.dht_query)
        
        # Should only need to query each user once
        self.assertLessEqual(self.dht_query.call_count, 2)
        self.dht_query.reset_mock()

    def test_query_efficiency_shortest_path(self):
        # Reset the mock to track calls
        self.dht_query.reset_mock()
        
        # Test shortest path for distant users
        find_shortest_path(self.user1, self.user8, self.dht_query)
        
        # Shouldn't query every user in the network
        self.assertLess(self.dht_query.call_count, len(self.mock_data))
        self.dht_query.reset_mock()

if __name__ == '__main__':
    unittest.main()