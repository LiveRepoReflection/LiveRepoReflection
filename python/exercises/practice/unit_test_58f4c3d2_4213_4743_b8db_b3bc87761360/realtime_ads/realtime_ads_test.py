import unittest
import importlib
import realtime_ads

class TestRealTimeAds(unittest.TestCase):
    def setUp(self):
        # Reload the realtime_ads module to reset its internal state between tests.
        importlib.reload(realtime_ads)
        self.model = realtime_ads
        # For our tests, we assume that the implementation in realtime_ads uses global parameters:
        # d: dimension of context vectors, k: number of ads, and alpha: exploration parameter.
        # Although not explicitly set by the tests, our tests are designed with the following assumptions:
        # d = 2, k = 2, and an appropriate alpha provided by the implementation.
        self.d = 2
        self.k = 2

    def test_choose_ad_returns_valid_index(self):
        # Test that choose_ad returns an integer within the valid range.
        context = [0.5, -0.3]
        chosen_ad = self.model.choose_ad(context)
        self.assertIsInstance(chosen_ad, int)
        self.assertGreaterEqual(chosen_ad, 0)
        self.assertLess(chosen_ad, self.k)

    def test_update_with_no_reward(self):
        # Test that updating with a reward of 0 does not break the selection mechanism.
        context = [1.0, 0.0]
        chosen_ad = self.model.choose_ad(context)
        self.model.update(context, chosen_ad, 0)
        new_choice = self.model.choose_ad(context)
        self.assertIsInstance(new_choice, int)
        self.assertGreaterEqual(new_choice, 0)
        self.assertLess(new_choice, self.k)

    def test_update_with_reward_effect(self):
        # Simulate repeated positive rewards for ad 0.
        context = [1.0, 0.0]
        # Update ad 0 multiple times with a reward of 1.
        for _ in range(10):
            self.model.update(context, 0, 1)
        # Now, when choosing an ad for the same context, ad 0 should be preferred.
        chosen_ad = self.model.choose_ad(context)
        self.assertEqual(chosen_ad, 0)

    def test_multiple_contexts_and_ads(self):
        # Test that different contexts favor different ads after targeted updates.
        context_ad0 = [1.0, 0.0]
        context_ad1 = [0.0, 1.0]
        # Favor ad 0 for context_ad0.
        for _ in range(5):
            self.model.update(context_ad0, 0, 1)
        # Favor ad 1 for context_ad1.
        for _ in range(5):
            self.model.update(context_ad1, 1, 1)
        choice_for_context_ad0 = self.model.choose_ad(context_ad0)
        choice_for_context_ad1 = self.model.choose_ad(context_ad1)
        self.assertEqual(choice_for_context_ad0, 0)
        self.assertEqual(choice_for_context_ad1, 1)

    def test_exploration_exploitation_balance(self):
        # Test that after an update with reward, the chosen ad remains valid under exploration settings.
        context = [0.2, 0.8]
        initial_choice = self.model.choose_ad(context)
        # Perform an update with a reward for the chosen ad.
        self.model.update(context, initial_choice, 1)
        new_choice = self.model.choose_ad(context)
        self.assertIsInstance(new_choice, int)
        self.assertGreaterEqual(new_choice, 0)
        self.assertLess(new_choice, self.k)

if __name__ == '__main__':
    unittest.main()