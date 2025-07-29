import unittest
import numpy as np
from federated_aggregate import aggregate_model_updates

class FederatedAggregateTest(unittest.TestCase):
    def setUp(self):
        self.initial_model = {
            "layer1": np.array([[1.0, 2.0], [3.0, 4.0]]),
            "layer2": np.array([[5.0, 6.0]])
        }
        self.X_val = np.array([0])
        self.y_val = np.array([0])
        self.validation_data = (self.X_val, self.y_val)

    def models_are_equal(self, model1, model2):
        if set(model1.keys()) != set(model2.keys()):
            return False
        for key in model1:
            if model1[key].shape != model2[key].shape:
                return False
            if not np.allclose(model1[key], model2[key]):
                return False
        return True

    def test_no_clients(self):
        # When there are no clients, the aggregated model should equal the initial model.
        clients = []
        aggregated_model = aggregate_model_updates(clients, self.validation_data, 5, self.initial_model)
        self.assertTrue(self.models_are_equal(aggregated_model, self.initial_model))

    def test_budget_zero(self):
        # With zero server aggregation budget, no updates should be processed.
        clients = [{
            "id": 1,
            "updates": [("layer1", np.array([[10.0, 10.0], [10.0, 10.0]]))],
            "priority": 1.0,
            "max_updates": 1
        }]
        aggregated_model = aggregate_model_updates(clients, self.validation_data, 0, self.initial_model)
        self.assertTrue(self.models_are_equal(aggregated_model, self.initial_model))

    def test_clients_no_updates(self):
        # When clients have no available updates, the aggregated model remains unchanged.
        clients = [
            {
                "id": 1,
                "updates": [],
                "priority": 1.0,
                "max_updates": 1
            },
            {
                "id": 2,
                "updates": [],
                "priority": 2.0,
                "max_updates": 1
            }
        ]
        aggregated_model = aggregate_model_updates(clients, self.validation_data, 5, self.initial_model)
        self.assertTrue(self.models_are_equal(aggregated_model, self.initial_model))

    def test_invariant_model_shape(self):
        # Ensure that the aggregated model has the same layers and shapes as the initial model.
        clients = [
            {
                "id": 1,
                "updates": [
                    ("layer1", np.array([[2.0, 2.0], [2.0, 2.0]])),
                    ("layer2", np.array([[3.0, 3.0]]))
                ],
                "priority": 1.0,
                "max_updates": 2
            },
            {
                "id": 2,
                "updates": [
                    ("layer1", np.array([[4.0, 4.0], [4.0, 4.0]])),
                    ("layer2", np.array([[6.0, 6.0]]))
                ],
                "priority": 1.5,
                "max_updates": 2
            }
        ]
        aggregated_model = aggregate_model_updates(clients, self.validation_data, 4, self.initial_model)
        self.assertEqual(set(aggregated_model.keys()), set(self.initial_model.keys()))
        for layer in self.initial_model:
            self.assertEqual(aggregated_model[layer].shape, self.initial_model[layer].shape)

    def test_single_client_update(self):
        # Test with a single client providing updates.
        clients = [{
            "id": 1,
            "updates": [
                ("layer1", np.array([[5.0, 5.0], [5.0, 5.0]])),
                ("layer2", np.array([[7.0, 7.0]]))
            ],
            "priority": 1.0,
            "max_updates": 2
        }]
        aggregated_model = aggregate_model_updates(clients, self.validation_data, 2, self.initial_model)
        self.assertEqual(set(aggregated_model.keys()), set(self.initial_model.keys()))
        # Verify that at least one layer has been updated compared to the initial model.
        updated = False
        for key in self.initial_model:
            if not np.allclose(aggregated_model[key], self.initial_model[key]):
                updated = True
        self.assertTrue(updated)

    def test_multiple_clients_partial_updates(self):
        # Test with multiple clients where the server aggregation budget is less than the total available updates.
        clients = [
            {
                "id": 1,
                "updates": [
                    ("layer1", np.array([[2.0, 2.0], [2.0, 2.0]])),
                    ("layer2", np.array([[3.0, 3.0]]))
                ],
                "priority": 1.0,
                "max_updates": 2
            },
            {
                "id": 2,
                "updates": [
                    ("layer1", np.array([[4.0, 4.0], [4.0, 4.0]])),
                    ("layer2", np.array([[6.0, 6.0]]))
                ],
                "priority": 2.0,
                "max_updates": 2
            },
            {
                "id": 3,
                "updates": [
                    ("layer1", np.array([[1.0, 1.0], [1.0, 1.0]]))
                ],
                "priority": 0.5,
                "max_updates": 1
            }
        ]
        # Set server budget to process only 3 updates in total.
        aggregated_model = aggregate_model_updates(clients, self.validation_data, 3, self.initial_model)
        self.assertEqual(set(aggregated_model.keys()), set(self.initial_model.keys()))
        for layer in self.initial_model:
            self.assertEqual(aggregated_model[layer].shape, self.initial_model[layer].shape)
        # Ensure that at least one layer differs from the initial model.
        changed = False
        for key in self.initial_model:
            if not np.allclose(aggregated_model[key], self.initial_model[key]):
                changed = True
        self.assertTrue(changed)

if __name__ == '__main__':
    unittest.main()