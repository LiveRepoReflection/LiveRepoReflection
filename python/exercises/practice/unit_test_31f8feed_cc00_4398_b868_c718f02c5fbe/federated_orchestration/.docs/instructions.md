## Federated Learning Orchestration

### Question Description

You are building a system to orchestrate federated learning across a network of edge devices. Each device possesses a local dataset and the ability to train a machine learning model. The goal is to collaboratively train a global model by aggregating updates from these devices without directly accessing their private data.

**System Architecture:**

*   **Server:** A central server coordinates the federated learning process. It initializes the global model, distributes it to participating devices, aggregates model updates, and updates the global model.

*   **Devices:** Edge devices with local datasets participate in the training process. They receive the global model from the server, train it on their local data, and send the updated model (or model updates) back to the server.

**Problem:**

Implement a system to simulate the federated learning process, focusing on efficient resource management and handling device failures.

**Specific Requirements:**

1.  **Device Selection:** Given a list of available devices, the server must select a subset of devices for each round of training. The number of devices selected should be configurable.

2.  **Asynchronous Updates:** Devices may have varying computational capabilities and network connectivity. The server should be able to handle asynchronous updates, meaning that it does not need to wait for all selected devices to complete training before aggregating updates.

3.  **Differential Privacy (Simplified):** To protect the privacy of individual devices' data, implement a simplified form of differential privacy. Before sending model updates to the server, each device should add Gaussian noise to their updates. The standard deviation of the noise should be configurable. Assume the model updates are represented as a list of floating-point numbers (weights).

4.  **Device Failures:** Simulate device failures. A device may fail to send its update to the server with a certain probability (configurable). The server should be able to handle these failures gracefully and continue the federated learning process.

5.  **Model Aggregation:** The server should aggregate the model updates received from devices.  A simple averaging of the weights is sufficient. The server should only aggregate weights from devices that have successfully sent their updates.

6.  **Optimization for Large Datasets:** Assume the number of devices and the size of the global model can be very large.  Consider the memory footprint and computational complexity of your solution. The global model and the model updates should be stored and processed efficiently.

7.  **Scalability:** The system should be designed to handle a large number of devices. Consider how your solution would scale as the number of devices increases.

**Input:**

*   `num_devices`: The total number of devices in the network.
*   `model_size`: The size of the global model (number of weights). Represent the model as a list of floats.
*   `selection_size`: The number of devices to select for each round.
*   `noise_stddev`: The standard deviation of the Gaussian noise for differential privacy.
*   `failure_rate`: The probability of a device failing to send its update.
*   `num_rounds`: The number of federated learning rounds to perform.
*   `local_training_steps`: The number of training steps each device performs on its local data. (This doesn't need to be simulated, just tracked as a parameter).

**Output:**

Simulate the federated learning process for the specified number of rounds.  Return a list containing the global model (list of floats) at the end of each round.

**Constraints:**

*   `1 <= num_devices <= 100000`
*   `1 <= model_size <= 10000`
*   `1 <= selection_size <= num_devices`
*   `0.0 <= noise_stddev <= 1.0`
*   `0.0 <= failure_rate <= 0.5`
*   `1 <= num_rounds <= 10`
*   `1 <= local_training_steps <= 100`

**Evaluation:**

The solution will be evaluated based on:

*   **Correctness:** The implementation should accurately simulate the federated learning process.
*   **Efficiency:** The code should be optimized for performance, especially with large numbers of devices and model sizes.
*   **Scalability:** The design should be scalable to handle a large number of devices.
*   **Robustness:** The code should handle device failures gracefully.
*   **Code Quality:** The code should be well-structured, readable, and maintainable.
