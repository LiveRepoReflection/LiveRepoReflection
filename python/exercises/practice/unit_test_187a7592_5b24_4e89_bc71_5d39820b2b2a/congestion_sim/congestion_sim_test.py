import unittest
from congestion_sim import network_congestion_control
import numpy as np


class NetworkCongestionControlTest(unittest.TestCase):
    def setUp(self):
        # Seed for reproducibility in tests
        np.random.seed(42)

    def test_basic_simulation(self):
        N = 2
        C = 10
        initial_rates = [4.0, 5.0]
        alpha = 0.1
        reduction_factor = 0.5
        T = 3
        congestion_notification_probability = 0.5
        
        results = network_congestion_control(
            N, C, initial_rates, alpha, reduction_factor, T, congestion_notification_probability
        )
        
        self.assertEqual(len(results), T + 1)  # Initial rates + T iterations
        self.assertEqual(len(results[0]), N)
        self.assertEqual(results[0], initial_rates)
        
        # Check that rates are always non-negative
        for iteration in results:
            for rate in iteration:
                self.assertGreaterEqual(rate, 0)

    def test_no_congestion(self):
        N = 3
        C = 100  # Very high capacity, no congestion
        initial_rates = [5.0, 10.0, 15.0]
        alpha = 0.5
        reduction_factor = 0.5
        T = 5
        congestion_notification_probability = 0.5
        
        results = network_congestion_control(
            N, C, initial_rates, alpha, reduction_factor, T, congestion_notification_probability
        )
        
        # Without congestion, all senders should increase their rates
        for i in range(1, T + 1):
            for j in range(N):
                self.assertGreaterEqual(results[i][j], results[i-1][j])

    def test_guaranteed_congestion_notification(self):
        N = 3
        C = 10  # Low capacity, guaranteed congestion
        initial_rates = [5.0, 10.0, 15.0]  # Total: 30 > C
        alpha = 0.1
        reduction_factor = 0.5
        T = 5
        congestion_notification_probability = 1.0  # 100% notification
        
        results = network_congestion_control(
            N, C, initial_rates, alpha, reduction_factor, T, congestion_notification_probability
        )
        
        # Check if rates decrease when congestion is certain
        total_rates = [sum(iteration) for iteration in results]
        # After some iterations, total rate should approach capacity
        self.assertLess(total_rates[-1], total_rates[0])

    def test_no_congestion_notification(self):
        N = 3
        C = 10
        initial_rates = [2.0, 3.0, 4.0]  # Total: 9 < C initially
        alpha = 0.5
        reduction_factor = 0.5
        T = 5
        congestion_notification_probability = 0.0  # 0% notification
        
        results = network_congestion_control(
            N, C, initial_rates, alpha, reduction_factor, T, congestion_notification_probability
        )
        
        # Rates should continuously increase until congestion
        for i in range(1, T + 1):
            for j in range(N):
                self.assertGreaterEqual(results[i][j], results[i-1][j])

    def test_large_number_of_senders(self):
        N = 100
        C = 500
        initial_rates = [5.0] * N
        alpha = 0.1
        reduction_factor = 0.5
        T = 10
        congestion_notification_probability = 0.3
        
        results = network_congestion_control(
            N, C, initial_rates, alpha, reduction_factor, T, congestion_notification_probability
        )
        
        self.assertEqual(len(results), T + 1)
        self.assertEqual(len(results[0]), N)

    def test_extreme_alpha_value(self):
        N = 3
        C = 20
        initial_rates = [5.0, 5.0, 5.0]
        alpha = 5.0  # Large alpha
        reduction_factor = 0.5
        T = 5
        congestion_notification_probability = 0.5
        
        results = network_congestion_control(
            N, C, initial_rates, alpha, reduction_factor, T, congestion_notification_probability
        )
        
        # Check that simulation completes without errors
        self.assertEqual(len(results), T + 1)

    def test_extreme_reduction_factor(self):
        N = 3
        C = 20
        initial_rates = [5.0, 5.0, 5.0]
        alpha = 0.1
        reduction_factor = 0.05  # Very small reduction factor
        T = 5
        congestion_notification_probability = 0.5
        
        results = network_congestion_control(
            N, C, initial_rates, alpha, reduction_factor, T, congestion_notification_probability
        )
        
        # Check that simulation completes without errors
        self.assertEqual(len(results), T + 1)

    def test_fairness_over_time(self):
        N = 5
        C = 25
        initial_rates = [1.0, 2.0, 3.0, 4.0, 5.0]  # Uneven initial distribution
        alpha = 0.1
        reduction_factor = 0.5
        T = 50  # Run for many iterations
        congestion_notification_probability = 0.5
        
        results = network_congestion_control(
            N, C, initial_rates, alpha, reduction_factor, T, congestion_notification_probability
        )
        
        # Check if rates converge to more fair distribution over time
        initial_std = np.std(initial_rates)
        final_std = np.std(results[-1])
        
        # Not guaranteed, but fairness algorithm should generally reduce standard deviation
        # This is a probabilistic test, so we use a softer assertion
        self.assertLessEqual(final_std, initial_std * 1.5)
        
    def test_zero_initial_rates(self):
        N = 3
        C = 10
        initial_rates = [0.0, 0.0, 0.0]
        alpha = 0.1
        reduction_factor = 0.5
        T = 10
        congestion_notification_probability = 0.5
        
        results = network_congestion_control(
            N, C, initial_rates, alpha, reduction_factor, T, congestion_notification_probability
        )
        
        # Check that rates increase from zero
        self.assertTrue(all(rate > 0 for rate in results[-1]))

    def test_total_rate_adjustment(self):
        N = 5
        C = 20
        initial_rates = [5.0, 5.0, 5.0, 5.0, 5.0]  # Total: 25 > C
        alpha = 0.1
        reduction_factor = 0.5
        T = 20
        congestion_notification_probability = 0.5
        
        results = network_congestion_control(
            N, C, initial_rates, alpha, reduction_factor, T, congestion_notification_probability
        )
        
        # After several iterations, the total rate should approach capacity
        final_total_rate = sum(results[-1])
        self.assertLess(abs(final_total_rate - C), C * 0.5)  # Within 50% of capacity


if __name__ == "__main__":
    unittest.main()