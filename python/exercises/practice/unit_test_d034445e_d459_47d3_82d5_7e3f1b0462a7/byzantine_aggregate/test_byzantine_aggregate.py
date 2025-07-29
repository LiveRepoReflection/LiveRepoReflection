import unittest
import numpy as np
from byzantine_aggregate import aggregate_updates

class TestByzantineAggregate(unittest.TestCase):
    def setUp(self):
        self.model_shape = (10, 10)
        self.epsilon = 1e-6
        
    def test_no_byzantine_nodes(self):
        updates = [np.ones(self.model_shape) * i for i in range(10)]
        result = aggregate_updates(self.model_shape, updates, 0.0, self.epsilon)
        expected = np.mean(updates, axis=0)
        np.testing.assert_allclose(result, expected, rtol=1e-6)
        
    def test_sign_flipping_attack(self):
        updates = [np.ones(self.model_shape) * i for i in range(8)]
        updates.extend([-np.ones(self.model_shape) * 100 for _ in range(2)])  # 20% Byzantine
        result = aggregate_updates(self.model_shape, updates, 0.2, self.epsilon)
        self.assertFalse(np.allclose(result, np.mean(updates, axis=0), rtol=1e-6))
        
    def test_random_noise_attack(self):
        updates = [np.random.normal(0, 1, self.model_shape) for _ in range(8)]
        updates.extend([np.random.normal(100, 100, self.model_shape) for _ in range(2)])  # 20% Byzantine
        result = aggregate_updates(self.model_shape, updates, 0.2, self.epsilon)
        self.assertLess(np.linalg.norm(result), 10)  # Should be resilient to large outliers
        
    def test_all_byzantine_nodes(self):
        updates = [np.ones(self.model_shape) * 1000 for _ in range(10)]
        with self.assertRaises(ValueError):
            aggregate_updates(self.model_shape, updates, 1.0, self.epsilon)
            
    def test_edge_case_small_updates(self):
        updates = [np.ones(self.model_shape) * 1e-6 for _ in range(9)]
        updates.append(np.ones(self.model_shape) * 1e6)  # 10% Byzantine
        result = aggregate_updates(self.model_shape, updates, 0.1, self.epsilon)
        self.assertTrue(np.all(result < 1))  # Should not be affected by single large update
        
    def test_sparse_corruption(self):
        updates = [np.zeros(self.model_shape) for _ in range(9)]
        corrupt_update = np.zeros(self.model_shape)
        corrupt_update[0, 0] = 1e6  # Single corrupted parameter
        updates.append(corrupt_update)  # 10% Byzantine
        result = aggregate_updates(self.model_shape, updates, 0.1, self.epsilon)
        self.assertAlmostEqual(result[0, 0], 0, delta=1e-3)  # Should be resilient to sparse corruption
        
    def test_invalid_byzantine_fraction(self):
        updates = [np.ones(self.model_shape) for _ in range(10)]
        with self.assertRaises(ValueError):
            aggregate_updates(self.model_shape, updates, -0.1, self.epsilon)
        with self.assertRaises(ValueError):
            aggregate_updates(self.model_shape, updates, 1.1, self.epsilon)
            
    def test_empty_updates(self):
        with self.assertRaises(ValueError):
            aggregate_updates(self.model_shape, [], 0.1, self.epsilon)
            
    def test_shape_mismatch(self):
        updates = [np.ones(self.model_shape) for _ in range(9)]
        updates.append(np.ones((5, 5)))  # Incorrect shape
        with self.assertRaises(ValueError):
            aggregate_updates(self.model_shape, updates, 0.1, self.epsilon)

if __name__ == '__main__':
    unittest.main()