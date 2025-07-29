import unittest
import time

# Assume the content_recommender module provides a function get_recommendations(user_id)
from content_recommender import get_recommendations

class TestContentRecommender(unittest.TestCase):

    def test_valid_user_recommendations(self):
        # Test with an existing user that has a valid history.
        user_id = "existing_user"
        recommendations = get_recommendations(user_id)
        self.assertIsInstance(recommendations, list, "Recommendations should be returned as a list.")
        self.assertGreater(len(recommendations), 0, "The list of recommendations should not be empty for a valid user.")

        # Each recommendation is expected to be a dictionary with keys 'content_id' and 'score'
        for rec in recommendations:
            self.assertIsInstance(rec, dict, "Each recommendation should be a dictionary.")
            self.assertIn("content_id", rec, "Each recommendation should contain a 'content_id'.")
            self.assertIn("score", rec, "Each recommendation should contain a 'score'.")
            # Check that score is a float or int
            self.assertIsInstance(rec["score"], (float, int), "The recommendation 'score' must be a number.")

    def test_recommendations_sorted_by_score(self):
        # Test that recommendations are sorted in descending order by score.
        user_id = "existing_user"
        recommendations = get_recommendations(user_id)
        scores = [rec["score"] for rec in recommendations]
        sorted_scores = sorted(scores, reverse=True)
        self.assertEqual(scores, sorted_scores, "The recommendations should be sorted in descending order by score.")

    def test_cold_start_user(self):
        # Test the cold start scenario for a new user with no history.
        user_id = "new_user"
        recommendations = get_recommendations(user_id)
        self.assertIsInstance(recommendations, list, "Recommendations for a new user should be a list.")
        self.assertGreater(len(recommendations), 0, "Even a new user should receive some popularity based recommendations.")

    def test_latency(self):
        # Test that the recommendation generation is under 50ms for the 99th percentile case.
        user_id = "existing_user"
        start_time = time.time()
        _ = get_recommendations(user_id)
        end_time = time.time()
        elapsed_ms = (end_time - start_time) * 1000  # Convert seconds to milliseconds
        self.assertLess(elapsed_ms, 50, "The recommendation API should return within 50 milliseconds.")

    def test_invalid_user_input(self):
        # Test that passing an invalid user id (None) raises a ValueError.
        with self.assertRaises(ValueError):
            get_recommendations(None)

    def test_consistent_results_for_same_user(self):
        # For the same user and fixed underlying data,
        # the recommendation engine should return consistent results.
        user_id = "existing_user"
        recommendations1 = get_recommendations(user_id)
        recommendations2 = get_recommendations(user_id)
        self.assertEqual(recommendations1, recommendations2, "Recommendations should be consistent for the same user across calls.")

if __name__ == '__main__':
    unittest.main()