import unittest
from decentralized_learning import decentralized_learning

class TestDecentralizedLearning(unittest.TestCase):
    def test_basic_functionality(self):
        def gradient(weights, data):
            grad = [0.0] * len(weights)
            for feature_vector, label in data:
                prediction = sum(w * f for w, f in zip(weights, feature_vector))
                error = prediction - label
                for i in range(len(weights)):
                    grad[i] += error * feature_vector[i]
            return grad

        def predict(weights, feature_vector):
            prediction = sum(w * f for w, f in zip(weights, feature_vector))
            return 1 if prediction > 0 else 0

        n = 2
        initial_weights = [[0.1, 0.2], [0.1, 0.2]]
        local_data = [
            [([1.0, 2.0], 1), ([2.0, 3.0], 0)],
            [([1.0, 2.0], 1), ([2.0, 3.0], 0)]
        ]
        learning_rate = 0.01
        num_rounds = 1
        test_data = [([1.5, 2.5], 1), ([2.5, 3.5], 0)]

        accuracy = decentralized_learning(
            n, initial_weights, local_data, learning_rate,
            num_rounds, gradient, test_data, predict
        )
        self.assertIsInstance(accuracy, float)
        self.assertTrue(0 <= accuracy <= 1)

    def test_empty_local_data(self):
        def gradient(weights, data):
            return [0.0] * len(weights)

        def predict(weights, feature_vector):
            return 0

        n = 2
        initial_weights = [[0.1, 0.2], [0.1, 0.2]]
        local_data = [[], []]  # Empty datasets
        learning_rate = 0.01
        num_rounds = 1
        test_data = [([1.0, 2.0], 0)]

        accuracy = decentralized_learning(
            n, initial_weights, local_data, learning_rate,
            num_rounds, gradient, test_data, predict
        )
        self.assertEqual(accuracy, 1.0)  # Should predict all 0s

    def test_single_node(self):
        def gradient(weights, data):
            grad = [0.0] * len(weights)
            for feature_vector, label in data:
                error = sum(w * f for w, f in zip(weights, feature_vector)) - label
                for i in range(len(weights)):
                    grad[i] += error * feature_vector[i]
            return grad

        def predict(weights, feature_vector):
            return 1 if sum(w * f for w, f in zip(weights, feature_vector)) > 0 else 0

        n = 1
        initial_weights = [[0.1, 0.2]]
        local_data = [[([1.0, 2.0], 1), ([2.0, 3.0], 0)]]
        learning_rate = 0.01
        num_rounds = 2
        test_data = [([1.5, 2.5], 1), ([2.5, 3.5], 0)]

        accuracy = decentralized_learning(
            n, initial_weights, local_data, learning_rate,
            num_rounds, gradient, test_data, predict
        )
        self.assertIsInstance(accuracy, float)

    def test_multiple_rounds(self):
        def gradient(weights, data):
            return [w * 0.1 for w in weights]  # Simple gradient

        def predict(weights, feature_vector):
            return 0  # Always predict 0

        n = 3
        initial_weights = [[0.1, 0.2], [0.1, 0.2], [0.1, 0.2]]
        local_data = [
            [([1.0, 2.0], 0)],
            [([1.0, 2.0], 0)],
            [([1.0, 2.0], 0)]
        ]
        learning_rate = 0.1
        num_rounds = 5
        test_data = [([1.0, 2.0], 0)]

        accuracy = decentralized_learning(
            n, initial_weights, local_data, learning_rate,
            num_rounds, gradient, test_data, predict
        )
        self.assertEqual(accuracy, 1.0)

    def test_different_initial_weights(self):
        def gradient(weights, data):
            return [0.0] * len(weights)

        def predict(weights, feature_vector):
            return 1 if weights[0] > 0.5 else 0

        n = 2
        initial_weights = [[0.6, 0.7], [0.4, 0.5]]  # Different initial weights
        local_data = [
            [([1.0, 2.0], 1)],
            [([1.0, 2.0], 1)]
        ]
        learning_rate = 0.01
        num_rounds = 1
        test_data = [([1.0, 2.0], 1)]

        accuracy = decentralized_learning(
            n, initial_weights, local_data, learning_rate,
            num_rounds, gradient, test_data, predict
        )
        self.assertTrue(accuracy >= 0.0)

if __name__ == '__main__':
    unittest.main()