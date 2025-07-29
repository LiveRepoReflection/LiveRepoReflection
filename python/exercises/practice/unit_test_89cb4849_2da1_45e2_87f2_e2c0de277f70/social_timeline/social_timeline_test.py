import unittest
import time
from datetime import datetime, timedelta

from social_timeline import DecentralizedSocialNetwork

class TestDecentralizedSocialNetwork(unittest.TestCase):
    def setUp(self):
        # Create a sample follower graph:
        # User 1 follows users 2 and 3, User 2 follows user 3, and User 3 follows none.
        self.follower_graph = {
            1: {2, 3},
            2: {3},
            3: set(),
            4: {1, 2, 3},  # additional user following all three
            5: {1},       # additional user following user 1 only
        }
        # Initialize the DecentralizedSocialNetwork with 5 nodes.
        self.network = DecentralizedSocialNetwork(
            nodes=5,
            follower_graph=self.follower_graph
        )
        # Setup a base timestamp for posts.
        self.base_time = int(time.time())

    def test_post_creation_and_timeline_retrieval(self):
        # Create posts by different users over different timestamps
        posts = [
            (101, 2, self.base_time - 300, "Post from user 2 - old"),
            (102, 3, self.base_time - 200, "Post from user 3 - medium"),
            (103, 2, self.base_time - 100, "Post from user 2 - recent"),
            (104, 4, self.base_time - 150, "Post from user 4 - not followed by user 1"),
            (105, 3, self.base_time - 50, "Post from user 3 - newest")
        ]
        for post in posts:
            self.network.create_post(post)
        
        # User 1 follows users 2 and 3 so timeline should only include posts from users 2 and 3.
        timeline = self.network.get_timeline(1, self.base_time - 400, self.base_time)
        
        # Check that only posts from user 2 and 3 exist in timeline.
        for post in timeline:
            self.assertIn(post[1], {2, 3})
        # Check that timeline is sorted by timestamp in descending order.
        timestamps = [post[2] for post in timeline]
        self.assertEqual(timestamps, sorted(timestamps, reverse=True))
        # Check timeline covers correct time range.
        for post in timeline:
            self.assertGreaterEqual(post[2], self.base_time - 400)
            self.assertLessEqual(post[2], self.base_time)

    def test_time_range_edge_inclusivity(self):
        # Create posts exactly at time range boundaries and inside.
        start_time = self.base_time - 250
        end_time = self.base_time - 50

        posts = [
            (201, 3, start_time, "Edge start post from user 3"),
            (202, 2, self.base_time - 150, "Middle post from user 2"),
            (203, 3, end_time, "Edge end post from user 3"),
            (204, 1, self.base_time - 100, "Post from user 1, should not appear for self-follow query")
        ]
        for post in posts:
            self.network.create_post(post)
        
        # For user 1, who follows user 2 and 3, timeline should include posts at boundaries.
        timeline = self.network.get_timeline(1, start_time, end_time)
        expected_post_ids = {201, 202, 203}
        timeline_post_ids = {post[0] for post in timeline}
        self.assertEqual(timeline_post_ids, expected_post_ids)
        
    def test_no_posts_in_timeline(self):
        # Create posts outside the given time range.
        posts = [
            (301, 2, self.base_time - 500, "Old post from user 2"),
            (302, 3, self.base_time + 100, "Future post from user 3")
        ]
        for post in posts:
            self.network.create_post(post)
        
        # Request timeline for a range that doesn't include any posts.
        timeline = self.network.get_timeline(1, self.base_time - 250, self.base_time - 200)
        self.assertEqual(len(timeline), 0)

    def test_posts_from_non_followed_users(self):
        # User 5 follows only user 1. Create posts from user 1 and others.
        posts = [
            (401, 1, self.base_time - 100, "Post from user 1 - should appear for user 5"),
            (402, 2, self.base_time - 90, "Post from user 2 - should NOT appear for user 5"),
            (403, 3, self.base_time - 80, "Post from user 3 - should NOT appear for user 5"),
        ]
        for post in posts:
            self.network.create_post(post)
        
        timeline = self.network.get_timeline(5, self.base_time - 200, self.base_time)
        self.assertEqual(len(timeline), 1)
        self.assertEqual(timeline[0][1], 1)
        self.assertEqual(timeline[0][0], 401)

    def test_concurrent_post_creation_simulation(self):
        # Simulate concurrent post creation by interleaving post creation calls.
        # In a real scenario, these would run in separate threads/processes.
        posts = [
            (501, 2, self.base_time - 300, "Concurrent post from user 2 - first"),
            (502, 3, self.base_time - 290, "Concurrent post from user 3 - first"),
            (503, 2, self.base_time - 280, "Concurrent post from user 2 - second"),
            (504, 3, self.base_time - 270, "Concurrent post from user 3 - second")
        ]
        for post in posts:
            self.network.create_post(post)
        
        timeline = self.network.get_timeline(1, self.base_time - 310, self.base_time - 260)
        expected_post_ids = {501, 502, 503, 504}
        timeline_post_ids = {post[0] for post in timeline}
        self.assertEqual(timeline_post_ids, expected_post_ids)
        timestamps = [post[2] for post in timeline]
        self.assertEqual(timestamps, sorted(timestamps, reverse=True))

    def test_fault_tolerance_simulation(self):
        # Simulate a scenario where some nodes are offline.
        # For testing purposes, assume the network has a method to simulate node failure and recovery.
        posts = [
            (601, 2, self.base_time - 200, "Post before node failure"),
            (602, 3, self.base_time - 190, "Another post before node failure")
        ]
        for post in posts:
            self.network.create_post(post)
        
        # Simulate node failure
        self.network.simulate_node_failure(nodes=[2, 4])
        
        # Create further posts during node failure
        posts_during_failure = [
            (603, 2, self.base_time - 180, "Post during node failure"),
            (604, 3, self.base_time - 170, "Another post during node failure")
        ]
        for post in posts_during_failure:
            self.network.create_post(post)
        
        # Retrieve the timeline; even if nodes were down, eventually all posts should appear.
        timeline = self.network.get_timeline(1, self.base_time - 250, self.base_time - 160)
        expected_post_ids = {601, 602, 603, 604}
        timeline_post_ids = {post[0] for post in timeline}
        self.assertEqual(timeline_post_ids, expected_post_ids)
        
        # Simulate node recovery
        self.network.simulate_node_recovery(nodes=[2, 4])
        
        # Retrieve timeline after recovery to ensure consistency.
        timeline_after_recovery = self.network.get_timeline(1, self.base_time - 250, self.base_time - 160)
        timeline_after_recovery_ids = {post[0] for post in timeline_after_recovery}
        self.assertEqual(timeline_after_recovery_ids, expected_post_ids)

if __name__ == '__main__':
    unittest.main()