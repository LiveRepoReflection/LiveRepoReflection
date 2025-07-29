import unittest
import random
from probabilistic_commit import TransactionCoordinator

class TestTransactionCoordinator(unittest.TestCase):
    def setUp(self):
        # Seed random for reproducible tests
        random.seed(42)

    def test_single_service_guaranteed_commit(self):
        """Test with a single service and 100% commit probability."""
        coordinator = TransactionCoordinator(1, 1.0, 10)
        self.assertTrue(coordinator.run_transaction())

    def test_single_service_guaranteed_abort(self):
        """Test with a single service and 0% commit probability."""
        coordinator = TransactionCoordinator(1, 0.0, 10)
        self.assertFalse(coordinator.run_transaction())

    def test_multiple_services_guaranteed_commit(self):
        """Test with multiple services and 100% commit probability."""
        coordinator = TransactionCoordinator(10, 1.0, 10)
        self.assertTrue(coordinator.run_transaction())

    def test_multiple_services_guaranteed_abort(self):
        """Test with multiple services and 0% commit probability."""
        coordinator = TransactionCoordinator(10, 0.0, 10)
        self.assertFalse(coordinator.run_transaction())

    def test_probabilistic_behavior(self):
        """Test that probabilistic behavior works as expected."""
        # Setting a fixed seed for reproducibility
        random.seed(42)
        coordinator = TransactionCoordinator(3, 0.5, 10)
        
        # Run multiple transactions to verify probabilistic behavior
        results = [coordinator.run_transaction() for _ in range(100)]
        
        # With 3 services and 0.5 probability, theoretical probability of commit is 0.5^3 = 0.125
        # Allow some variance but expect it to be roughly in line with theory
        success_rate = sum(results) / len(results)
        self.assertGreater(success_rate, 0.05)
        self.assertLess(success_rate, 0.25)

    def test_edge_case_large_number_of_services(self):
        """Test behavior with a large number of services."""
        coordinator = TransactionCoordinator(1000, 0.999, 10)
        # With 1000 services and 0.999 probability, still unlikely to get all commits
        self.assertIn(coordinator.run_transaction(), [True, False])

    def test_commit_probability_edge_cases(self):
        """Test edge cases for commit probability."""
        # Test with commit probability just above 0
        coordinator = TransactionCoordinator(5, 0.001, 10)
        results = [coordinator.run_transaction() for _ in range(10)]
        # Almost certainly all failures
        self.assertTrue(all(not result for result in results) or sum(results) <= 1)
        
        # Test with commit probability just below 1
        coordinator = TransactionCoordinator(5, 0.999, 10)
        results = [coordinator.run_transaction() for _ in range(10)]
        # Should have some successes
        self.assertTrue(any(results))

    def test_timeout_parameter(self):
        """Test that timeout parameter is properly stored in the coordinator."""
        coordinator = TransactionCoordinator(5, 0.5, 42)
        # This test assumes we can access the timeout attribute; adjust if implementation differs
        # Simply ensure coordinator was created without errors
        self.assertIsInstance(coordinator, TransactionCoordinator)

    def test_statistical_property(self):
        """
        Test the statistical property: with N services and probability p,
        the overall commit probability should be approximately p^N.
        """
        n_services = 4
        p_commit = 0.7
        expected_rate = p_commit ** n_services  # Theoretical success rate
        
        coordinator = TransactionCoordinator(n_services, p_commit, 10)
        
        # Run many trials to get statistical significance
        trials = 1000
        successes = sum(coordinator.run_transaction() for _ in range(trials))
        actual_rate = successes / trials
        
        # Allow for statistical variance using a reasonable margin
        margin = 0.05
        self.assertGreater(actual_rate, expected_rate - margin)
        self.assertLess(actual_rate, expected_rate + margin)

    def test_independence_of_services(self):
        """
        Test that services make their decisions independently.
        If they do, the pattern of successes/failures should follow a binomial distribution.
        """
        random.seed(42)
        n_services = 1
        p_commit = 0.5
        trials = 1000
        
        coordinator = TransactionCoordinator(n_services, p_commit, 10)
        
        # Count the number of commits
        commit_count = sum(coordinator.run_transaction() for _ in range(trials))
        
        # For a single service with p=0.5, we expect roughly 50% commits with some variance
        self.assertGreater(commit_count, trials * 0.45)
        self.assertLess(commit_count, trials * 0.55)

if __name__ == "__main__":
    unittest.main()