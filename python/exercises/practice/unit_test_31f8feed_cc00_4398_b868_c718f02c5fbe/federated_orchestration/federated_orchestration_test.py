import unittest
import numpy as np
from federated_orchestration import (
    simulate_federated_learning
)

class FederatedOrchestrationTest(unittest.TestCase):
    def test_small_system_no_failures(self):
        # Small system, no device failures
        num_devices = 10
        model_size = 5
        selection_size = 5
        noise_stddev = 0.0
        failure_rate = 0.0
        num_rounds = 3
        local_training_steps = 1
        
        result = simulate_federated_learning(
            num_devices, model_size, selection_size, noise_stddev, 
            failure_rate, num_rounds, local_training_steps
        )
        
        # Check we have the right number of rounds
        self.assertEqual(len(result), num_rounds)
        # Check each round produces a model of the right size
        for model in result:
            self.assertEqual(len(model), model_size)
            # Check all values are floating point
            for weight in model:
                self.assertIsInstance(weight, float)
    
    def test_with_differential_privacy(self):
        # Test with differential privacy (noise)
        num_devices = 10
        model_size = 5
        selection_size = 5
        noise_stddev = 0.1
        failure_rate = 0.0
        num_rounds = 2
        local_training_steps = 1
        
        np.random.seed(42)  # For reproducibility
        result = simulate_federated_learning(
            num_devices, model_size, selection_size, noise_stddev, 
            failure_rate, num_rounds, local_training_steps
        )
        
        # Models with noise should be different in consecutive rounds
        # We can't predict exact values due to randomness
        self.assertEqual(len(result), num_rounds)
        for model in result:
            self.assertEqual(len(model), model_size)
    
    def test_with_device_failures(self):
        # Test with device failures
        num_devices = 20
        model_size = 5
        selection_size = 10
        noise_stddev = 0.0
        failure_rate = 0.5  # 50% chance of failure
        num_rounds = 3
        local_training_steps = 1
        
        np.random.seed(42)  # For reproducibility
        result = simulate_federated_learning(
            num_devices, model_size, selection_size, noise_stddev, 
            failure_rate, num_rounds, local_training_steps
        )
        
        # System should still produce models despite failures
        self.assertEqual(len(result), num_rounds)
        for model in result:
            self.assertEqual(len(model), model_size)
    
    def test_asynchronous_updates(self):
        # Test handling asynchronous updates
        num_devices = 15
        model_size = 10
        selection_size = 10
        noise_stddev = 0.05
        failure_rate = 0.2
        num_rounds = 2
        local_training_steps = 5  # More training steps to simulate variation
        
        np.random.seed(42)  # For reproducibility
        result = simulate_federated_learning(
            num_devices, model_size, selection_size, noise_stddev, 
            failure_rate, num_rounds, local_training_steps
        )
        
        self.assertEqual(len(result), num_rounds)
        for model in result:
            self.assertEqual(len(model), model_size)
    
    def test_edge_case_single_device(self):
        # Edge case: only one device
        num_devices = 1
        model_size = 3
        selection_size = 1
        noise_stddev = 0.0
        failure_rate = 0.0
        num_rounds = 2
        local_training_steps = 1
        
        result = simulate_federated_learning(
            num_devices, model_size, selection_size, noise_stddev, 
            failure_rate, num_rounds, local_training_steps
        )
        
        self.assertEqual(len(result), num_rounds)
        for model in result:
            self.assertEqual(len(model), model_size)
    
    def test_edge_case_full_failure(self):
        # Edge case: all devices fail (should handle gracefully)
        num_devices = 5
        model_size = 3
        selection_size = 5
        noise_stddev = 0.0
        failure_rate = 1.0  # 100% failure rate
        num_rounds = 2
        local_training_steps = 1
        
        np.random.seed(42)  # For reproducibility
        result = simulate_federated_learning(
            num_devices, model_size, selection_size, noise_stddev, 
            failure_rate, num_rounds, local_training_steps
        )
        
        # Should still return models even with all failures
        self.assertEqual(len(result), num_rounds)
        for model in result:
            self.assertEqual(len(model), model_size)
    
    def test_large_scale_simulation(self):
        # Test with larger scale (but not too large for unit test)
        num_devices = 100
        model_size = 50
        selection_size = 20
        noise_stddev = 0.01
        failure_rate = 0.1
        num_rounds = 2
        local_training_steps = 3
        
        result = simulate_federated_learning(
            num_devices, model_size, selection_size, noise_stddev, 
            failure_rate, num_rounds, local_training_steps
        )
        
        self.assertEqual(len(result), num_rounds)
        for model in result:
            self.assertEqual(len(model), model_size)
    
    def test_model_values_change(self):
        # Test that model values actually change during training
        num_devices = 10
        model_size = 5
        selection_size = 10
        noise_stddev = 0.0  # No noise to make comparison deterministic
        failure_rate = 0.0  # No failures
        num_rounds = 3
        local_training_steps = 2
        
        result = simulate_federated_learning(
            num_devices, model_size, selection_size, noise_stddev, 
            failure_rate, num_rounds, local_training_steps
        )
        
        # Check that models from different rounds are not identical
        # At least one weight should change between rounds
        for i in range(1, len(result)):
            self.assertFalse(all(result[i][j] == result[i-1][j] for j in range(model_size)))
    
    def test_parameter_validation(self):
        # Test with invalid parameters
        # num_devices less than selection_size
        with self.assertRaises(ValueError):
            simulate_federated_learning(5, 10, 10, 0.0, 0.0, 2, 1)
        
        # Invalid failure rate
        with self.assertRaises(ValueError):
            simulate_federated_learning(10, 10, 5, 0.0, 1.5, 2, 1)
        
        # Invalid noise stddev
        with self.assertRaises(ValueError):
            simulate_federated_learning(10, 10, 5, -0.1, 0.0, 2, 1)

if __name__ == '__main__':
    unittest.main()