import unittest
from decentralized_social import DSN

class TestDecentralizedSocial(unittest.TestCase):
    def setUp(self):
        # Initialize DSN with an inbox size of 3.
        self.inbox_size = 3
        self.dsn = DSN(self.inbox_size)
        # Create sample users
        self.dsn.create_user("user1", "alice", "Alice", "Bio of Alice")
        self.dsn.create_user("user2", "bob", "Bob", "Bio of Bob")
        self.dsn.create_user("user3", "charlie", "Charlie", "Bio of Charlie")

    def test_create_user_success(self):
        self.dsn.create_user("user4", "dave", "Dave", "Bio of Dave")
        user = self.dsn.get_user("user4")
        self.assertEqual(user["username"], "dave")
        self.assertEqual(user["display_name"], "Dave")
        self.assertEqual(user["bio"], "Bio of Dave")
        self.assertEqual(user["followers"], [])
        self.assertEqual(user["following"], [])

    def test_create_user_duplicate(self):
        with self.assertRaises(Exception):
            self.dsn.create_user("user1", "alice2", "Alice2", "Another bio")

    def test_update_user_success(self):
        self.dsn.update_user("user1", username="alice_new", display_name="Alice New", bio="Updated bio")
        user = self.dsn.get_user("user1")
        self.assertEqual(user["username"], "alice_new")
        self.assertEqual(user["display_name"], "Alice New")
        self.assertEqual(user["bio"], "Updated bio")

    def test_update_user_nonexistent(self):
        with self.assertRaises(Exception):
            self.dsn.update_user("nonexistent", username="nouser")

    def test_get_user_nonexistent(self):
        with self.assertRaises(Exception):
            self.dsn.get_user("nonexistent")

    def test_follow_user_success(self):
        # user1 follows user2
        self.dsn.follow_user("user1", "user2")
        user1 = self.dsn.get_user("user1")
        user2 = self.dsn.get_user("user2")
        self.assertIn("user2", user1["following"])
        self.assertIn("user1", user2["followers"])

    def test_follow_user_nonexistent(self):
        with self.assertRaises(Exception):
            self.dsn.follow_user("user1", "nonexistent")
        with self.assertRaises(Exception):
            self.dsn.follow_user("nonexistent", "user1")

    def test_unfollow_user_success(self):
        # user1 follows then unfollows user2
        self.dsn.follow_user("user1", "user2")
        self.dsn.unfollow_user("user1", "user2")
        user1 = self.dsn.get_user("user1")
        user2 = self.dsn.get_user("user2")
        self.assertNotIn("user2", user1["following"])
        self.assertNotIn("user1", user2["followers"])

    def test_unfollow_user_nonexistent(self):
        with self.assertRaises(Exception):
            self.dsn.unfollow_user("user1", "nonexistent")
        with self.assertRaises(Exception):
            self.dsn.unfollow_user("nonexistent", "user1")

    def test_create_post_and_get_post_success(self):
        self.dsn.create_post("post1", "user1", "Hello World", 1000)
        post = self.dsn.get_post("post1")
        self.assertEqual(post["author_id"], "user1")
        self.assertEqual(post["content"], "Hello World")
        self.assertEqual(post["timestamp"], 1000)

    def test_create_post_duplicate_or_invalid_author(self):
        self.dsn.create_post("post1", "user1", "Hello World", 1000)
        with self.assertRaises(Exception):
            self.dsn.create_post("post1", "user1", "Duplicate post", 1001)
        with self.assertRaises(Exception):
            self.dsn.create_post("post2", "nonexistent", "Invalid author", 1002)

    def test_get_post_nonexistent(self):
        with self.assertRaises(Exception):
            self.dsn.get_post("nonexistent_post")

    def test_distribute_post_and_inbox_eviction(self):
        # user2 and user3 follow user1
        self.dsn.follow_user("user2", "user1")
        self.dsn.follow_user("user3", "user1")
        
        # Create and distribute the first post
        self.dsn.create_post("post1", "user1", "Content 1", 1000)
        self.dsn.distribute_post("post1")
        inbox_user2 = self.dsn.get_inbox("user2")
        inbox_user3 = self.dsn.get_inbox("user3")
        self.assertIn("post1", inbox_user2)
        self.assertIn("post1", inbox_user3)
        
        # Distribute additional posts to test inbox eviction
        self.dsn.create_post("post2", "user1", "Content 2", 1001)
        self.dsn.create_post("post3", "user1", "Content 3", 1002)
        self.dsn.create_post("post4", "user1", "Content 4", 1003)
        self.dsn.distribute_post("post2")
        self.dsn.distribute_post("post3")
        self.dsn.distribute_post("post4")
        
        # Since inbox size is 3, the oldest post ("post1") should be evicted.
        inbox_user2 = self.dsn.get_inbox("user2")
        inbox_user3 = self.dsn.get_inbox("user3")
        self.assertNotIn("post1", inbox_user2)
        self.assertNotIn("post1", inbox_user3)
        self.assertIn("post2", inbox_user2)
        self.assertIn("post3", inbox_user2)
        self.assertIn("post4", inbox_user2)
        self.assertEqual(len(inbox_user2), self.inbox_size)
        self.assertEqual(len(inbox_user3), self.inbox_size)

    def test_get_inbox_nonexistent_user(self):
        with self.assertRaises(Exception):
            self.dsn.get_inbox("nonexistent")

if __name__ == "__main__":
    unittest.main()