import math
import unittest

from social_reputation import calculate_reputation

class SocialReputationTest(unittest.TestCase):
    def assertDictAlmostEqual(self, d1, d2, places=5):
        self.assertEqual(set(d1.keys()), set(d2.keys()))
        for key in d1:
            self.assertAlmostEqual(d1[key], d2[key], places=places)
    
    def test_no_posts_or_endorsements(self):
        users = ["u1", "u2", "u3"]
        posts = []
        endorsements = []
        expected = {"u1": 0.0, "u2": 0.0, "u3": 0.0}
        result = calculate_reputation(users, posts, endorsements)
        self.assertDictAlmostEqual(result, expected)
    
    def test_single_post_non_reciprocal(self):
        users = ["u1", "u2"]
        posts = [("p1", "u1")]
        endorsements = [("p1", "u2")]
        # For a non-reciprocal endorsement, reciprocal count = 0,
        # bonus = 1 / log2(0+2) = 1 / 1 = 1.
        expected = {"u1": 1.0, "u2": 0.0}
        result = calculate_reputation(users, posts, endorsements)
        self.assertDictAlmostEqual(result, expected)
    
    def test_reciprocal_endorsement(self):
        users = ["u1", "u2"]
        posts = [("p1", "u1"), ("p2", "u2")]
        endorsements = [("p1", "u2"), ("p2", "u1")]
        # For u1's post p1: endorsement from u2.
        # Reciprocal: count = number of endorsements from u1 on posts by u2.
        # u1 endorsed post p2 once, so r = 1, bonus = 1 / log2(1+2) = 1 / log2(3)
        bonus_u2 = 1 / math.log2(3)
        expected = {"u1": bonus_u2, "u2": bonus_u2}
        result = calculate_reputation(users, posts, endorsements)
        self.assertDictAlmostEqual(result, expected)

    def test_duplicate_endorsements_ignored(self):
        users = ["u1", "u2", "u3", "u4"]
        posts = [("p1", "u1"), ("p2", "u1")]
        endorsements = [
            ("p1", "u2"),
            ("p1", "u3"),
            ("p1", "u2"),  # duplicate endorsement by u2 for p1, should be ignored
            ("p2", "u4"),
            ("p2", "u2")
        ]
        # For u1's posts, there is no reciprocity because u1 has not endorsed any posts by u2, u3, or u4.
        # Therefore, each unique endorsement contributes 1 (bonus = 1 / log2(0+2) = 1).
        # p1: endorsements from u2 and u3 => score 1 + 1 = 2
        # p2: endorsements from u4 and u2 => score 1 + 1 = 2
        # Total for u1 = 4, others = 0.
        expected = {"u1": 4.0, "u2": 0.0, "u3": 0.0, "u4": 0.0}
        result = calculate_reputation(users, posts, endorsements)
        self.assertDictAlmostEqual(result, expected)

    def test_complex_scenario_with_multiple_reciprocities(self):
        users = ["u1", "u2", "u3"]
        posts = [
            ("p1", "u1"),
            ("p2", "u2"),
            ("p3", "u2"),
            ("p4", "u3")
        ]
        endorsements = [
            # u1's post p1 endorsed by u2 and u3.
            ("p1", "u2"),
            ("p1", "u3"),
            # u2's posts:
            ("p2", "u1"),
            ("p3", "u3"),
            # u3's post:
            ("p4", "u1"),
            ("p4", "u2")
        ]
        # Calculations:
        # For u1's post p1:
        #    Endorsement from u2:
        #       Reciprocal count = number of endorsements from u1 on posts by u2.
        #       u1 endorsed p2 (from u2) => count = 1, bonus = 1 / log2(1+2)
        bonus_u2_for_u1 = 1 / math.log2(3)
        #    Endorsement from u3:
        #       Reciprocal count = endorsements from u1 on posts by u3.
        #       u1 endorsed p4 (from u3) => count = 1, bonus = 1 / log2(3)
        bonus_u3_for_u1 = 1 / math.log2(3)
        score_u1 = bonus_u2_for_u1 + bonus_u3_for_u1

        # For u2's posts:
        #    p2: endorsed by u1.
        #       Reciprocal count = endorsements from u2 on posts by u1.
        #       u2 endorsed p1 (from u1) => count = 1, bonus = 1 / log2(3)
        bonus_u1_for_u2 = 1 / math.log2(3)
        #    p3: endorsed by u3.
        #       Reciprocal count = endorsements from u2 on posts by u3.
        #       u2 endorsed p4 (from u3) => count = 1, bonus = 1 / log2(3)
        bonus_u3_for_u2 = 1 / math.log2(3)
        score_u2 = bonus_u1_for_u2 + bonus_u3_for_u2

        # For u3's post:
        #    p4: endorsed by u1 and u2.
        #    For endorsement from u1:
        #       Reciprocal count = endorsements from u3 on posts by u1.
        #       u3 endorsed p1 (from u1) => count = 1, bonus = 1 / log2(3)
        bonus_u1_for_u3 = 1 / math.log2(3)
        #    For endorsement from u2:
        #       Reciprocal count = endorsements from u3 on posts by u2.
        #       u3 endorsed p3 (from u2) => count = 1, bonus = 1 / log2(3)
        bonus_u2_for_u3 = 1 / math.log2(3)
        score_u3 = bonus_u1_for_u3 + bonus_u2_for_u3

        expected = {
            "u1": round(score_u1, 5),
            "u2": round(score_u2, 5),
            "u3": round(score_u3, 5)
        }
        result = calculate_reputation(users, posts, endorsements)
        # Round the results for comparison
        result_rounded = {k: round(v, 5) for k, v in result.items()}
        self.assertEqual(result_rounded, expected)

if __name__ == '__main__':
    unittest.main()