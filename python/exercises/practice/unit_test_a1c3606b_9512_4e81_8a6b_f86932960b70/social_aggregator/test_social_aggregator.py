import unittest
from unittest.mock import Mock, patch
from social_aggregator import aggregate_and_rank_posts

class TestSocialAggregator(unittest.TestCase):
    def setUp(self):
        # Set up common test data
        self.user1_posts = [
            {"post_id": "post1", "author_id": "user1", "content": "Hello", "timestamp": 1000, "links": ["post2", "post3"], "node_id": 0},
            {"post_id": "post4", "author_id": "user1", "content": "Old post", "timestamp": 500, "links": [], "node_id": 0}
        ]
        
        self.user2_posts = [
            {"post_id": "post2", "author_id": "user2", "content": "Linked from user1", "timestamp": 900, "links": ["post5"], "node_id": 0}
        ]
        
        self.post3 = {"post_id": "post3", "author_id": "user3", "content": "Also linked from user1", "timestamp": 800, "links": [], "node_id": 1}
        self.post5 = {"post_id": "post5", "author_id": "user2", "content": "Depth 2 link", "timestamp": 700, "links": [], "node_id": 1}
        
        # Create mock node APIs
        self.node0_api = {
            "get_posts_by_user": Mock(),
            "get_post": Mock()
        }
        
        self.node1_api = {
            "get_posts_by_user": Mock(),
            "get_post": Mock()
        }
        
        # Configure mocks
        self.node0_api["get_posts_by_user"].side_effect = lambda user_id: (
            self.user1_posts if user_id == "user1" else
            self.user2_posts if user_id == "user2" else
            []
        )
        
        self.node0_api["get_post"].side_effect = lambda post_id: (
            self.user1_posts[0] if post_id == "post1" else
            self.user2_posts[0] if post_id == "post2" else
            self.user1_posts[1] if post_id == "post4" else
            None
        )
        
        self.node1_api["get_posts_by_user"].side_effect = lambda user_id: (
            [self.post3] if user_id == "user3" else
            []
        )
        
        self.node1_api["get_post"].side_effect = lambda post_id: (
            self.post3 if post_id == "post3" else
            self.post5 if post_id == "post5" else
            None
        )
        
        self.node_apis = [self.node0_api, self.node1_api]

    def test_basic_aggregation(self):
        """Test basic post aggregation for a single user"""
        user_ids = ["user1"]
        
        result = aggregate_and_rank_posts(user_ids, self.node_apis)
        
        # Should have both posts from user1
        self.assertEqual(len(result), 2)
        
        # post1 should be first (newer timestamp)
        self.assertEqual(result[0]["post_id"], "post1")
        self.assertEqual(result[1]["post_id"], "post4")

    def test_multiple_users(self):
        """Test aggregation for multiple users"""
        user_ids = ["user1", "user2"]
        
        result = aggregate_and_rank_posts(user_ids, self.node_apis)
        
        # Should have all posts from user1 and user2
        self.assertEqual(len(result), 3)
        
        # Check if all expected posts are in the result
        post_ids = [post["post_id"] for post in result]
        self.assertIn("post1", post_ids)
        self.assertIn("post2", post_ids)
        self.assertIn("post4", post_ids)

    def test_link_depth_ranking(self):
        """Test that posts with higher link depth rank higher"""
        user_ids = ["user1", "user2"]
        
        result = aggregate_and_rank_posts(user_ids, self.node_apis)
        
        # post1 has links to post2 and post3
        # post2 has a link to post5
        # post4 has no links
        
        # post1 should rank higher than post2 (newer timestamp and higher link depth)
        # post2 should rank higher than post4 (higher link depth)
        self.assertEqual(result[0]["post_id"], "post1")
        self.assertEqual(result[1]["post_id"], "post2")
        self.assertEqual(result[2]["post_id"], "post4")

    def test_author_popularity(self):
        """Test that posts from more popular authors rank higher"""
        # Setup a case where timestamp and link depth are equal, but author popularity differs
        user1_post = {"post_id": "post6", "author_id": "user1", "content": "Same time", "timestamp": 1200, "links": [], "node_id": 0}
        user3_post = {"post_id": "post7", "author_id": "user3", "content": "Same time", "timestamp": 1200, "links": [], "node_id": 1}
        
        # user1 has 2 posts, user3 has 1 post
        self.node0_api["get_posts_by_user"].side_effect = lambda user_id: (
            self.user1_posts + [user1_post] if user_id == "user1" else
            self.user2_posts if user_id == "user2" else
            []
        )
        
        self.node1_api["get_posts_by_user"].side_effect = lambda user_id: (
            [self.post3, user3_post] if user_id == "user3" else
            []
        )
        
        self.node0_api["get_post"].side_effect = lambda post_id: (
            user1_post if post_id == "post6" else
            self.node0_api["get_post"].side_effect(post_id)
        )
        
        self.node1_api["get_post"].side_effect = lambda post_id: (
            user3_post if post_id == "post7" else
            self.node1_api["get_post"].side_effect(post_id)
        )
        
        user_ids = ["user1", "user3"]
        
        result = aggregate_and_rank_posts(user_ids, self.node_apis)
        
        # Identify the two posts with timestamp 1200
        new_posts = [post for post in result if post["timestamp"] == 1200]
        self.assertEqual(len(new_posts), 2)
        
        # user1 has more posts than user3, so user1's post should rank higher
        self.assertEqual(new_posts[0]["author_id"], "user1")
        self.assertEqual(new_posts[1]["author_id"], "user3")

    def test_cyclic_links(self):
        """Test that the system handles cyclic links gracefully"""
        # Create a cycle: post1 -> post2 -> post8 -> post1
        post8 = {"post_id": "post8", "author_id": "user2", "content": "Cyclic link", "timestamp": 600, "links": ["post1"], "node_id": 0}
        self.user2_posts[0]["links"] = ["post8"]  # post2 now links to post8
        
        self.node0_api["get_post"].side_effect = lambda post_id: (
            post8 if post_id == "post8" else
            self.node0_api["get_post"].side_effect(post_id)
        )
        
        user_ids = ["user1"]
        
        # This should not cause an infinite loop
        result = aggregate_and_rank_posts(user_ids, self.node_apis)
        
        # Verify that post1 is returned
        self.assertEqual(result[0]["post_id"], "post1")

    def test_node_failure(self):
        """Test that the system is resilient to node failures"""
        # Make node1 fail by raising an exception
        self.node1_api["get_post"].side_effect = Exception("Node failure")
        self.node1_api["get_posts_by_user"].side_effect = Exception("Node failure")
        
        user_ids = ["user1"]
        
        # The system should continue to function, possibly with reduced results
        result = aggregate_and_rank_posts(user_ids, self.node_apis)
        
        # We should still get the posts from node0
        self.assertGreaterEqual(len(result), 2)
        
        # post1 should still be first, even if its links could not be resolved
        self.assertEqual(result[0]["post_id"], "post1")

    def test_empty_input(self):
        """Test behavior with empty inputs"""
        # No users
        result = aggregate_and_rank_posts([], self.node_apis)
        self.assertEqual(result, [])
        
        # No nodes
        result = aggregate_and_rank_posts(["user1"], [])
        self.assertEqual(result, [])

    def test_large_scale(self):
        """Test with a large number of users and posts"""
        # Mock a large number of users and posts
        large_node_api = {
            "get_posts_by_user": Mock(),
            "get_post": Mock()
        }
        
        # Create 100 users, each with 10 posts
        users = []
        posts_by_user = {}
        all_posts = {}
        
        for i in range(100):
            user_id = f"user{i}"
            users.append(user_id)
            user_posts = []
            
            for j in range(10):
                post_id = f"post{i}_{j}"
                post = {
                    "post_id": post_id,
                    "author_id": user_id,
                    "content": f"Content {i}_{j}",
                    "timestamp": i * 100 + j,
                    "links": [],
                    "node_id": 0
                }
                
                # Add some links between posts
                if j > 0:
                    post["links"].append(f"post{i}_{j-1}")
                
                user_posts.append(post)
                all_posts[post_id] = post
            
            posts_by_user[user_id] = user_posts
        
        large_node_api["get_posts_by_user"].side_effect = lambda user_id: posts_by_user.get(user_id, [])
        large_node_api["get_post"].side_effect = lambda post_id: all_posts.get(post_id)
        
        # Test with a subset of users
        test_users = users[:10]
        result = aggregate_and_rank_posts(test_users, [large_node_api])
        
        # Should have 100 posts (10 users * 10 posts each)
        self.assertEqual(len(result), 100)
        
        # Verify that the ranking is correct (newest posts first)
        for i in range(1, len(result)):
            self.assertGreaterEqual(result[i-1]["timestamp"], result[i]["timestamp"])

    def test_timeout_handling(self):
        """Test that the system handles timeouts gracefully"""
        # Create a node that always times out
        timeout_node_api = {
            "get_posts_by_user": Mock(side_effect=TimeoutError("Request timed out")),
            "get_post": Mock(side_effect=TimeoutError("Request timed out"))
        }
        
        user_ids = ["user1"]
        
        # The system should continue to function with the remaining nodes
        result = aggregate_and_rank_posts(user_ids, [timeout_node_api, self.node0_api])
        
        # We should still get the posts from node0
        self.assertGreaterEqual(len(result), 2)
        
        # post1 should still be first
        self.assertEqual(result[0]["post_id"], "post1")

    def test_nonexistent_posts(self):
        """Test behavior when trying to resolve links to nonexistent posts"""
        # Create a post with a link to a nonexistent post
        self.user1_posts[0]["links"].append("nonexistent_post")
        
        user_ids = ["user1"]
        
        # This should not cause an error
        result = aggregate_and_rank_posts(user_ids, self.node_apis)
        
        # We should still get both posts from user1
        self.assertEqual(len(result), 2)
        
        # post1 should still be first
        self.assertEqual(result[0]["post_id"], "post1")

if __name__ == "__main__":
    unittest.main()