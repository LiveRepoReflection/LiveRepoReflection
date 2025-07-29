## Question: Optimal High-Availability Load Balancing

**Problem Description:**

You are tasked with designing an optimal load balancing system for a highly critical service. The service receives a continuous stream of requests, and your goal is to distribute these requests across a cluster of servers to minimize latency and maximize availability.

**Input:**

*   `servers`: A list of tuples, where each tuple represents a server in the cluster. Each tuple contains:
    *   `server_id` (int): A unique identifier for the server.
    *   `capacity` (int): The maximum number of requests the server can handle concurrently.
    *   `health_score` (float): A value between 0.0 and 1.0 (inclusive) representing the server's health. 1.0 indicates perfect health, and 0.0 indicates complete failure.
*   `requests`: A list of integers, where each integer represents the processing time (in milliseconds) required to handle a request.
*   `time_window` (int): An integer representing a time window (in milliseconds). The load balancer must make decisions about request assignments at the start of each time window. Assume all requests in `requests` occur within a single `time_window`.
*   `alpha` (float): A float between 0.0 and 1.0 (inclusive) representing the weight given to latency vs. availability in the cost function. Higher values of `alpha` prioritize minimizing latency, while lower values prioritize maximizing availability.

**Output:**

A list of integers, where each integer represents the `server_id` to which the corresponding request in the `requests` list is assigned. The output list should have the same length as the `requests` list.

**Constraints and Requirements:**

1.  **Real-time Decision Making:** The load balancer must assign requests to servers at the beginning of the `time_window`. You do not have future knowledge of incoming requests beyond the current `time_window`.
2.  **Capacity Constraints:** A server cannot be assigned more requests than its `capacity` allows.
3.  **Health Awareness:** The load balancer should prioritize assigning requests to healthier servers. A server's `health_score` represents the probability that it will successfully handle a request without failure.
4.  **Optimization Goal:** Minimize a weighted cost function that balances latency and availability:

    *   **Latency Cost:** The sum of the processing times of all requests.
    *   **Availability Cost:** The sum, over all servers, of `(1 - health_score) * load_on_server`, where `load_on_server` is the total processing time assigned to that server. This penalizes assigning work to unhealthy servers.
    *   **Total Cost:** `alpha * (Latency Cost) + (1 - alpha) * (Availability Cost)`

5.  **Scalability:** The solution should be efficient enough to handle a large number of servers and requests. Consider the time complexity of your algorithm.
6.  **Edge Cases:** Handle edge cases such as:
    *   Empty `servers` or `requests` lists.
    *   Insufficient server capacity to handle all requests.
    *   Servers with a `health_score` of 0.

7.  **Multiple Valid Solutions:** There may be multiple valid assignments that minimize the cost function. Any assignment that achieves the minimum cost is acceptable.

**Example:**

```python
servers = [
    (1, 100, 0.9),  # server_id, capacity, health_score
    (2, 50, 0.7),
    (3, 75, 0.5)
]
requests = [20, 30, 40, 15, 25, 35, 20, 10, 5, 10]  # processing times
time_window = 1000
alpha = 0.6

# Expected output (example):
# [1, 1, 1, 1, 1, 2, 2, 3, 3, 3]
```

**Hints:**

*   Consider using optimization techniques like greedy algorithms, dynamic programming, or linear programming.
*   Carefully consider how to represent the problem state and make assignment decisions efficiently.
*   Think about how to handle the trade-off between latency and availability based on the `alpha` parameter.
*   Remember to handle edge cases gracefully.
