import unittest
from social_influencer import SocialNetwork

class TestSocialInfluencer(unittest.TestCase):
    def setUp(self):
        self.network = SocialNetwork()

    def test_add_user(self):
        # Test adding a new user
        result = self.network.add_user(1, "Alice", {"reach": "50"})
        self.assertTrue(result)
        # Attempt to add a duplicate user should fail
        result_dup = self.network.add_user(1, "Alice Duplicate", {"reach": "60"})
        self.assertFalse(result_dup)

    def test_add_friendship_and_get_friends(self):
        # Create users
        self.network.add_user(1, "Alice", {"reach": "50"})
        self.network.add_user(2, "Bob", {"reach": "40"})
        self.network.add_user(3, "Charlie", {"reach": "70"})
        # Initially no friends
        self.assertEqual(self.network.get_friends(1), set())
        # Add friendship between Alice and Bob
        result = self.network.add_friendship(1, 2)
        self.assertTrue(result)
        # Friendship should be bidirectional
        self.assertIn(2, self.network.get_friends(1))
        self.assertIn(1, self.network.get_friends(2))
        # Adding friendship with a non-existent user returns False
        result_nonexistent = self.network.add_friendship(1, 999)
        self.assertFalse(result_nonexistent)
        # Duplicate friendship should return False
        duplicate_friendship = self.network.add_friendship(1, 2)
        self.assertFalse(duplicate_friendship)

    def test_get_user_attributes(self):
        self.network.add_user(1, "Alice", {"reach": "50", "location": "NY"})
        attrs = self.network.get_user_attributes(1)
        self.assertEqual(attrs, {"reach": "50", "location": "NY"})
        # For a non-existent user, return an empty dict
        self.assertEqual(self.network.get_user_attributes(999), {})

    def test_get_influencers_degree_zero(self):
        self.network.add_user(1, "Alice", {"reach": "100"})
        influencers = self.network.get_influencers(1, 0, "reach")
        # When degree is 0, only the user itself should be returned
        self.assertEqual(influencers, [(1, 100)])

    def test_get_influencers_invalid_user(self):
        influencers = self.network.get_influencers(999, 1, "reach")
        # For non-existent user, return an empty list or handle gracefully
        self.assertEqual(influencers, [])

    def test_get_influencers_negative_degree(self):
        self.network.add_user(1, "Alice", {"reach": "100"})
        # Negative degree should be handled gracefully; here we expect only the starting user
        influencers = self.network.get_influencers(1, -1, "reach")
        self.assertEqual(influencers, [(1, 100)])

    def test_get_influencers_ranking_and_tie_breaking(self):
        # Create a network with multiple users and connections
        self.network.add_user(1, "Alice", {"reach": "30"})
        self.network.add_user(2, "Bob", {"reach": "50"})
        self.network.add_user(3, "Charlie", {"reach": "50"})
        self.network.add_user(4, "David", {"reach": "20"})
        self.network.add_user(5, "Eve", {"reach": "not_an_int"})  # Non-convertible reach => 0

        # Establish connections
        # Alice's friends: Bob and Charlie
        self.network.add_friendship(1, 2)
        self.network.add_friendship(1, 3)
        # Additional friendships for degree 2
        self.network.add_friendship(2, 4)
        self.network.add_friendship(3, 5)

        # Testing degree 1 influencers: should include direct friends plus self
        influencers_degree1 = self.network.get_influencers(1, 1, "reach")
        # Expected ranking: Bob (50), Charlie (50), then Alice (30); tie breaking by user id for Bob and Charlie
        expected_degree1 = [(2, 50), (3, 50), (1, 30)]
        self.assertEqual(influencers_degree1, expected_degree1)

        # Testing degree 2 influencers: now should include all friends within two hops
        influencers_degree2 = self.network.get_influencers(1, 2, "reach")
        # Expected users: Bob (50), Charlie (50), Alice (30), David (20), Eve (0)
        expected_degree2 = [(2, 50), (3, 50), (1, 30), (4, 20), (5, 0)]
        self.assertEqual(influencers_degree2, expected_degree2)

    def test_cycle_handling(self):
        # Create a cyclic network
        self.network.add_user(1, "Alice", {"reach": "10"})
        self.network.add_user(2, "Bob", {"reach": "20"})
        self.network.add_user(3, "Charlie", {"reach": "30"})
        self.network.add_friendship(1, 2)
        self.network.add_friendship(2, 3)
        self.network.add_friendship(3, 1)  # Introduce cycle

        influencers = self.network.get_influencers(1, 2, "reach")
        # Expect all users to be reachable without infinite recursion; ranked by reach descending
        expected = [(3, 30), (2, 20), (1, 10)]
        self.assertEqual(influencers, expected)

if __name__ == '__main__':
    unittest.main()