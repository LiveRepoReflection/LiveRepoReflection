import unittest
from dp_federated import run_dp_federated

class DPFederatedTest(unittest.TestCase):
    def test_single_participant(self):
        # Test with a single participant
        n_participants = 1
        local_dataset_sizes = [1000]
        global_model, total_privacy_budget, convergence_metric, communication_cost = run_dp_federated(
            n_participants=n_participants,
            local_dataset_sizes=local_dataset_sizes,
            model_type="linear_regression",
            dp_epsilon=1.0,
            dp_delta=1e-5,
            n_rounds=5,
            clipping_norm=1.0,
            learning_rate=0.01
        )
        # Validate global_model is a dictionary representing model parameters
        self.assertIsInstance(global_model, dict)
        # Validate total_privacy_budget is a tuple with two numeric values
        self.assertIsInstance(total_privacy_budget, tuple)
        self.assertEqual(len(total_privacy_budget), 2)
        self.assertTrue(isinstance(total_privacy_budget[0], (int, float)))
        self.assertTrue(isinstance(total_privacy_budget[1], (int, float)))
        # Validate convergence_metric is a float (e.g., loss, accuracy)
        self.assertIsInstance(convergence_metric, float)
        # Validate communication_cost is an integer indicating total parameter exchanges
        self.assertIsInstance(communication_cost, int)

    def test_multiple_participants(self):
        # Test with multiple participants and a neural network model
        n_participants = 5
        local_dataset_sizes = [500, 1000, 750, 1200, 900]
        global_model, total_privacy_budget, convergence_metric, communication_cost = run_dp_federated(
            n_participants=n_participants,
            local_dataset_sizes=local_dataset_sizes,
            model_type="neural_network",
            dp_epsilon=2.0,
            dp_delta=1e-6,
            n_rounds=10,
            clipping_norm=0.5,
            learning_rate=0.001
        )
        self.assertIsInstance(global_model, dict)
        self.assertIsInstance(total_privacy_budget, tuple)
        self.assertEqual(len(total_privacy_budget), 2)
        self.assertIsInstance(convergence_metric, float)
        self.assertIsInstance(communication_cost, int)
        # Communication cost should be greater than zero if training rounds occurred
        self.assertGreater(communication_cost, 0)

    def test_zero_rounds(self):
        # Test the scenario when no training rounds are executed
        n_participants = 3
        local_dataset_sizes = [300, 400, 500]
        global_model, total_privacy_budget, convergence_metric, communication_cost = run_dp_federated(
            n_participants=n_participants,
            local_dataset_sizes=local_dataset_sizes,
            model_type="logistic_regression",
            dp_epsilon=1.0,
            dp_delta=1e-5,
            n_rounds=0,
            clipping_norm=1.0,
            learning_rate=0.1
        )
        self.assertIsInstance(global_model, dict)
        # With zero rounds, the privacy budget consumed should be zero
        self.assertEqual(total_privacy_budget, (0, 0))
        self.assertIsInstance(convergence_metric, float)
        # Communication cost should be zero due to no rounds executed
        self.assertEqual(communication_cost, 0)

    def test_invalid_parameters(self):
        # Test error handling for mismatched participant count and dataset sizes
        n_participants = 2
        local_dataset_sizes = [1000]  # Mismatch: only one dataset size provided for two participants
        with self.assertRaises(ValueError):
            run_dp_federated(
                n_participants=n_participants,
                local_dataset_sizes=local_dataset_sizes,
                model_type="neural_network",
                dp_epsilon=1.0,
                dp_delta=1e-5,
                n_rounds=5,
                clipping_norm=1.0,
                learning_rate=0.01
            )

        # Test error handling for invalid differential privacy parameter (negative epsilon)
        local_dataset_sizes = [1000, 1500]
        with self.assertRaises(ValueError):
            run_dp_federated(
                n_participants=n_participants,
                local_dataset_sizes=local_dataset_sizes,
                model_type="neural_network",
                dp_epsilon=-1.0,
                dp_delta=1e-5,
                n_rounds=5,
                clipping_norm=1.0,
                learning_rate=0.01
            )

if __name__ == '__main__':
    unittest.main()