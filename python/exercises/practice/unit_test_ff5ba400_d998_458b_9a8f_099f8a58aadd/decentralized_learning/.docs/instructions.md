Okay, I'm ready to formulate a challenging Python coding problem. Here it is:

**Problem Title: Decentralized Collaborative Learning**

**Problem Description:**

You are tasked with simulating a decentralized collaborative learning environment.  Imagine a network of `n` nodes, each representing a machine learning model. These models need to collaboratively learn from a shared dataset, but the dataset is partitioned across the nodes due to privacy constraints. Direct data sharing is prohibited.

Each node `i` initially holds a subset of the training data `D_i` and a machine learning model `M_i`. The models are represented by a vector of weights `w_i`, and all models are of the same architecture. The goal is to collaboratively train these models to achieve a global model that performs well on the entire dataset.

The collaborative learning happens in rounds. In each round:

1.  **Model Aggregation:** Each node `i` sends its current model weights `w_i` to a central aggregator.
2.  **Weight Averaging:** The central aggregator computes the average of all received model weights: `w_avg = (1/n) * sum(w_i)` for all i in [1,n].
3.  **Model Update:** The central aggregator sends the averaged weights `w_avg` back to all nodes.
4.  **Local Training:** Each node `i` updates its model weights `w_i` by training on its local dataset `D_i` using the received averaged weights `w_avg` as a starting point. The update follows this rule:
`w_i = w_avg - learning_rate * gradient(Loss(w_avg, D_i))`. You can assume the gradient function is provided.

Your task is to simulate this decentralized learning process for a given number of rounds and evaluate the global performance of the learned models.

**Specific Requirements:**

1.  **Input:**
    *   `n`: The number of nodes in the network (integer, `1 <= n <= 1000`).
    *   `initial_weights`: A list of lists, where `initial_weights[i]` represents the initial model weights (a list of floats) for node `i`. All `initial_weights[i]` will have the same length.
    *   `local_data`: A list of lists, where `local_data[i]` represents the local dataset `D_i` for node `i`. Each `D_i` is a list of (feature_vector, label) tuples.  Each feature vector is a list of floats, and each label is an integer.
    *   `learning_rate`: A float representing the learning rate used during local training (`0.0001 <= learning_rate <= 0.1`).
    *   `num_rounds`: The number of collaborative learning rounds to perform (integer, `1 <= num_rounds <= 100`).
    *   `gradient(weights, data)`: A function that takes model weights (a list of floats) and a dataset (a list of (feature_vector, label) tuples) and returns the gradient of the loss function with respect to the weights (a list of floats). This function is provided.
    *   `test_data`: A list of (feature_vector, label) tuples representing the test dataset used to evaluate model performance. Each feature vector is a list of floats, and each label is an integer.
    *   `predict(weights, feature_vector)`: A function that takes model weights (a list of floats) and a feature vector (a list of floats) and returns a predicted label (an integer). This function is provided.

2.  **Output:**
    *   The accuracy of the *averaged* model (i.e., using `w_avg`) on the `test_data` *after* all collaborative learning rounds are completed. Accuracy is defined as the number of correct predictions divided by the total number of test samples.  Return the accuracy as a float.

**Constraints and Considerations:**

*   **Efficiency:** The solution should be reasonably efficient, especially regarding the averaging and gradient calculation steps.  Avoid unnecessary computations or data copies.  Consider vectorized operations where appropriate.
*   **Correctness:** Ensure that the weight averaging and local training steps are implemented correctly.  The gradient calculation is assumed to be accurate.
*   **Scalability:** Although `n` is limited to 1000, consider how your solution might scale to larger networks in terms of memory usage and computation time.  Avoid storing large intermediate results if possible.
*   **Edge Cases:** Consider edge cases such as empty local datasets `D_i`. The model should still be able to function, even if some nodes contribute no training data in a particular round.

**Example:** (Simplified for illustration)

```python
def gradient(weights, data):
  # Simplified gradient calculation for demonstration
  grad = [0.0] * len(weights)
  for feature_vector, label in data:
    # Example: Assume a linear model and calculate a simple gradient
    prediction = sum(w * f for w, f in zip(weights, feature_vector))
    error = prediction - label
    for i in range(len(weights)):
      grad[i] += error * feature_vector[i]
  return grad

def predict(weights, feature_vector):
    #Simplified predict calculation for demonstration
    prediction = sum(w * f for w, f in zip(weights, feature_vector))
    return 1 if prediction > 0 else 0 #Example binary classification

n = 3
initial_weights = [[0.1, 0.2], [0.3, 0.4], [0.5, 0.6]]
local_data = [
  [([1.0, 2.0], 1), ([2.0, 3.0], 0)],
  [([3.0, 4.0], 1)],
  [([4.0, 5.0], 0), ([5.0, 6.0], 1)]
]
learning_rate = 0.01
num_rounds = 2
test_data = [([1.5, 2.5], 1), ([4.5, 5.5], 0)]

# Expected output (approximate): 0.5
```

**Goal:** Implement a function `decentralized_learning(n, initial_weights, local_data, learning_rate, num_rounds, gradient, test_data, predict)` that takes the inputs described above and returns the final accuracy of the averaged model on the test data.

This problem combines elements of distributed systems, machine learning, and numerical computation, requiring careful consideration of efficiency and correctness. Good luck!
