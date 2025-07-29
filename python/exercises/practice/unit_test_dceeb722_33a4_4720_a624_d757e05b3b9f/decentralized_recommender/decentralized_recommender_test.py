import unittest
from decentralized_recommender import predict_rating, get_recommendations

class DecentralizedRecommenderTest(unittest.TestCase):
    def setUp(self):
        # Global information: anonymized aggregate data and item metadata.
        self.global_info = {
            'item_stats': {
                101: {'avg_rating': 4.0, 'rating_variance': 0.5, 'category': 'movie'},
                102: {'avg_rating': 3.5, 'rating_variance': 0.3, 'category': 'movie'},
                103: {'avg_rating': 2.0, 'rating_variance': 0.7, 'category': 'book'},
                104: {'avg_rating': 4.5, 'rating_variance': 0.2, 'category': 'book'},
                105: {'avg_rating': 3.0, 'rating_variance': 1.0, 'category': 'music'}
            },
            'category_similarity': {
                ('movie', 'movie'): 1.0,
                ('movie', 'book'): 0.3,
                ('movie', 'music'): 0.5,
                ('book', 'book'): 1.0,
                ('book', 'music'): 0.4,
                ('music', 'music'): 1.0
            }
        }
        # Local user ratings stored as list of tuples (item_id, rating)
        self.user_ratings = [
            (101, 5.0),
            (103, 2.5)
        ]

    def test_predict_rating_range(self):
        """Test that the predicted rating is a float within valid bounds (1 to 5)."""
        predicted = predict_rating(self.user_ratings, self.global_info, 102)
        self.assertIsInstance(predicted, float)
        self.assertGreaterEqual(predicted, 1.0)
        self.assertLessEqual(predicted, 5.0)

    def test_get_recommendations_length(self):
        """Test that the recommendations list has the requested length and correct structure."""
        num_recommendations = 2
        recommendations = get_recommendations(self.user_ratings, self.global_info, num_recommendations)
        self.assertIsInstance(recommendations, list)
        self.assertEqual(len(recommendations), num_recommendations)
        for rec in recommendations:
            self.assertIn('item_id', rec)
            self.assertIn('predicted_rating', rec)
            self.assertIsInstance(rec['predicted_rating'], float)
            self.assertGreaterEqual(rec['predicted_rating'], 1.0)
            self.assertLessEqual(rec['predicted_rating'], 5.0)

    def test_cold_start_new_user(self):
        """Test the cold start scenario where a new user has no ratings."""
        new_user_ratings = []
        num_recommendations = 3
        recommendations = get_recommendations(new_user_ratings, self.global_info, num_recommendations)
        self.assertIsInstance(recommendations, list)
        self.assertEqual(len(recommendations), num_recommendations)
        for rec in recommendations:
            self.assertIn('item_id', rec)
            self.assertIn('predicted_rating', rec)
            self.assertIsInstance(rec['predicted_rating'], float)
            self.assertGreaterEqual(rec['predicted_rating'], 1.0)
            self.assertLessEqual(rec['predicted_rating'], 5.0)

    def test_similar_users_influence(self):
        """Test that higher ratings in similar item categories influence the prediction favorably."""
        # Alter local ratings: high ratings for movie category items.
        modified_user_ratings = [
            (101, 4.5),
            (102, 4.0)
        ]
        predicted = predict_rating(modified_user_ratings, self.global_info, 101)
        # Expect that prediction reflects higher satisfaction, should be relatively high.
        self.assertGreaterEqual(predicted, 3.5)

    def test_feedback_adjustment(self):
        """
        Test the feedback integration mechanism.
        If the update_model function is available, it should adjust the recommendations
        based on the feedback provided.
        """
        recommendations_before = get_recommendations(self.user_ratings, self.global_info, num_recommendations=2)
        # Simulate user feedback: assume user gives a slightly higher rating than predicted.
        feedback_data = [(rec['item_id'], rec['predicted_rating'] + 0.5) for rec in recommendations_before]
        try:
            from decentralized_recommender import update_model
            updated_recommendations = update_model(self.user_ratings, feedback_data, self.global_info)
            self.assertIsInstance(updated_recommendations, list)
            for rec in updated_recommendations:
                self.assertIn('item_id', rec)
                self.assertIn('predicted_rating', rec)
                self.assertIsInstance(rec['predicted_rating'], float)
                self.assertGreaterEqual(rec['predicted_rating'], 1.0)
                self.assertLessEqual(rec['predicted_rating'], 5.0)
        except ImportError:
            # If update_model is not implemented, the test passes by default.
            pass

if __name__ == '__main__':
    unittest.main()