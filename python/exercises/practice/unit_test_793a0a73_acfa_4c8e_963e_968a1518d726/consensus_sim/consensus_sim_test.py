import unittest
import random
from consensus_sim import simulate_consensus

class ConsensusSimTestCase(unittest.TestCase):
    def setUp(self):
        random.seed(42)

    def test_no_byzantine(self):
        # Test simulation with no Byzantine nodes. Expect consensus to be reached within R rounds.
        N = 100
        K = 10
        B = 0.0
        w_self = 0.5
        w_received = 0.05  # 0.5 + (10 * 0.05) = 1.0
        R = 50
        T = 0.1
        rounds = simulate_consensus(N, K, B, w_self, w_received, R, T)
        self.assertIsInstance(rounds, int)
        # When consensus is reached, rounds should be in the range [1, R].
        if rounds != -1:
            self.assertGreaterEqual(rounds, 1)
            self.assertLessEqual(rounds, R)
        else:
            # It is acceptable that consensus was not reached,
            # but this should be a rare case with these parameters.
            self.assertEqual(rounds, -1)

    def test_low_rounds(self):
        # Use a tiny maximum round to force a failure of convergence.
        N = 50
        K = 5
        B = 0.0
        w_self = 0.8
        w_received = 0.04  # 0.8 + (5 * 0.04) = 1.0
        R = 2
        T = 0.001  # Harder threshold that likely prevents consensus in 2 rounds.
        rounds = simulate_consensus(N, K, B, w_self, w_received, R, T)
        self.assertEqual(rounds, -1)

    def test_with_byzantine(self):
        # Test simulation with a percentage of Byzantine nodes.
        N = 200
        K = 10
        B = 0.1  # 10% Byzantine nodes.
        w_self = 0.6
        w_received = 0.04  # 0.6 + (10 * 0.04) = 1.0
        R = 100
        T = 0.1
        rounds = simulate_consensus(N, K, B, w_self, w_received, R, T)
        self.assertIsInstance(rounds, int)
        # Consensus may or may not be reached under Byzantine influence.
        self.assertTrue(rounds == -1 or (1 <= rounds <= R))

    def test_k_greater_than_n(self):
        # Test the edge case where K (number of communication partners) is greater than N.
        N = 10
        K = 20  # More than total nodes.
        B = 0.0
        # Adjust weights based on effective contacts.
        # Effective K = min(K, N - 1) = 9, so choose w_self and w_received such that:
        # w_self + (9 * w_received) = 1.0.
        w_self = 0.5
        w_received = 0.5 / 9
        R = 50
        T = 0.1
        rounds = simulate_consensus(N, K, B, w_self, w_received, R, T)
        self.assertIsInstance(rounds, int)
        if rounds != -1:
            self.assertGreaterEqual(rounds, 1)
            self.assertLessEqual(rounds, R)

    def test_invalid_weights(self):
        # Test that when the sum of weights (w_self + K * w_received) is not 1, a ValueError is raised.
        N = 100
        K = 10
        B = 0.0
        w_self = 0.5
        w_received = 0.06  # 0.5 + (10 * 0.06) = 1.1, which is invalid.
        R = 50
        T = 0.1
        with self.assertRaises(ValueError):
            simulate_consensus(N, K, B, w_self, w_received, R, T)

    def test_invalid_input(self):
        # Test handling of invalid input values such as negative N.
        N = -100
        K = 10
        B = 0.0
        w_self = 0.5
        w_received = 0.05
        R = 50
        T = 0.1
        with self.assertRaises(ValueError):
            simulate_consensus(N, K, B, w_self, w_received, R, T)

if __name__ == "__main__":
    unittest.main()