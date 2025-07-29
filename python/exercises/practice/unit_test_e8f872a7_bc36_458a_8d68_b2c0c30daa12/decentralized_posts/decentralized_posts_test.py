import unittest
from decentralized_posts import store_post, retrieve_posts
import hashlib
import random

class DecentralizedPostsTest(unittest.TestCase):
    def test_store_post_returns_valid_cid(self):
        cid = store_post(12345, "user1", 1678886400, "Hello, world!")
        # Check that the CID is a valid SHA-256 hash (64 hexadecimal characters)
        self.assertEqual(len(cid), 64)
        self.assertTrue(all(c in "0123456789abcdef" for c in cid))

    def test_store_post_deterministic_cid(self):
        # Same input should produce the same CID
        cid1 = store_post(12345, "user1", 1678886400, "Hello, world!")
        cid2 = store_post(54321, "user1", 1678886400, "Hello, world!")
        self.assertEqual(cid1, cid2)

    def test_store_post_different_content(self):
        # Different content should produce different CIDs
        cid1 = store_post(12345, "user1", 1678886400, "Hello, world!")
        cid2 = store_post(12345, "user1", 1678886400, "Different content")
        self.assertNotEqual(cid1, cid2)

    def test_retrieve_posts_empty(self):
        # No posts stored for this user
        posts = retrieve_posts(12345, "nonexistent_user")
        self.assertEqual(posts, [])

    def test_retrieve_posts_single_post(self):
        # Store a single post and retrieve it
        user_id = f"test_user_{random.randint(1, 1000000)}"
        timestamp = 1678886400
        content = "Single post test"
        
        store_post(12345, user_id, timestamp, content)
        posts = retrieve_posts(54321, user_id)
        
        self.assertEqual(len(posts), 1)
        self.assertEqual(posts[0], (timestamp, content))

    def test_retrieve_posts_multiple_posts_sorted(self):
        # Store multiple posts and verify they're returned in descending timestamp order
        user_id = f"test_user_{random.randint(1, 1000000)}"
        post_data = [
            (1678886400, "First post"),
            (1678886500, "Second post"),
            (1678886300, "Earlier post"),
            (1678887000, "Latest post")
        ]
        
        for timestamp, content in post_data:
            store_post(12345, user_id, timestamp, content)
        
        posts = retrieve_posts(54321, user_id)
        
        # Verify post count
        self.assertEqual(len(posts), len(post_data))
        
        # Verify posts are sorted by timestamp in descending order
        sorted_expected = sorted(post_data, key=lambda x: x[0], reverse=True)
        self.assertEqual(posts, sorted_expected)

    def test_retrieve_posts_different_nodes(self):
        # Posts should be retrievable from different nodes
        user_id = f"test_user_{random.randint(1, 1000000)}"
        timestamp = 1678886400
        content = "Node test post"
        
        store_post(12345, user_id, timestamp, content)
        
        # Retrieve from different nodes
        posts1 = retrieve_posts(54321, user_id)
        posts2 = retrieve_posts(98765, user_id)
        
        self.assertEqual(posts1, posts2)
        self.assertEqual(len(posts1), 1)
        self.assertEqual(posts1[0], (timestamp, content))

    def test_k_replication(self):
        # This test is more conceptual, as we're not directly testing the replication
        # but rather that the system works with different K values
        user_id = f"test_user_{random.randint(1, 1000000)}"
        timestamp = 1678886400
        content = "K replication test"
        
        # Store with default K
        store_post(12345, user_id, timestamp, content)
        posts = retrieve_posts(54321, user_id)
        
        self.assertEqual(len(posts), 1)
        self.assertEqual(posts[0], (timestamp, content))

    def test_multiple_users(self):
        # Test that posts from different users don't get mixed
        user1_id = f"test_user_{random.randint(1, 1000000)}"
        user2_id = f"test_user_{random.randint(1, 1000000)}"
        
        # Ensure different user IDs
        while user1_id == user2_id:
            user2_id = f"test_user_{random.randint(1, 1000000)}"
            
        # Store posts for user1
        store_post(12345, user1_id, 1678886400, "User1 post 1")
        store_post(12345, user1_id, 1678886500, "User1 post 2")
        
        # Store posts for user2
        store_post(12345, user2_id, 1678886600, "User2 post 1")
        
        # Retrieve posts
        posts1 = retrieve_posts(54321, user1_id)
        posts2 = retrieve_posts(54321, user2_id)
        
        # Check post counts
        self.assertEqual(len(posts1), 2)
        self.assertEqual(len(posts2), 1)
        
        # Check post content
        self.assertEqual(posts1[0][1], "User1 post 2")  # Higher timestamp first
        self.assertEqual(posts1[1][1], "User1 post 1")
        self.assertEqual(posts2[0][1], "User2 post 1")

    def test_large_number_of_posts(self):
        # Test system with a larger number of posts
        user_id = f"test_user_{random.randint(1, 1000000)}"
        num_posts = 50
        
        # Store posts with random timestamps
        post_data = []
        for i in range(num_posts):
            timestamp = 1678886400 + random.randint(0, 10000)
            content = f"Post {i} with random content {random.randint(1000, 9999)}"
            store_post(12345, user_id, timestamp, content)
            post_data.append((timestamp, content))
        
        # Retrieve posts
        posts = retrieve_posts(54321, user_id)
        
        # Verify post count
        self.assertEqual(len(posts), num_posts)
        
        # Verify posts are sorted correctly
        sorted_expected = sorted(post_data, key=lambda x: x[0], reverse=True)
        self.assertEqual(posts, sorted_expected)

    def test_stress_nodes(self):
        # Test with various node IDs
        user_id = f"test_user_{random.randint(1, 1000000)}"
        timestamp = 1678886400
        content = "Node stress test"
        
        store_post(12345, user_id, timestamp, content)
        
        # Test various node IDs for storage and retrieval
        for _ in range(10):
            store_node = random.randint(0, 2**20 - 1)
            retrieve_node = random.randint(0, 2**20 - 1)
            
            store_post(store_node, user_id, timestamp, content)
            posts = retrieve_posts(retrieve_node, user_id)
            
            self.assertTrue(len(posts) >= 1)
            self.assertTrue(any(p[1] == content for p in posts))

if __name__ == '__main__':
    unittest.main()