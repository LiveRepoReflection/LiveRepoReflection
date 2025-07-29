## Question: Robust Network Routing

### Question Description

You are designing a robust routing system for a large-scale communication network. The network consists of `n` nodes, labeled from `0` to `n-1`. The connections between nodes are represented by a set of undirected edges. Due to hardware limitations and potential link failures, each edge has a limited bandwidth capacity and a probability of failure.

Given the network topology, bandwidth capacities, failure probabilities, a source node `s`, a destination node `d`, and a minimum required bandwidth `b`, your task is to find the most reliable path from `s` to `d` that satisfies the bandwidth requirement.

**Reliability of a path is defined as the probability that all edges in the path are operational.** Assume edge failures are independent events.

**Input:**

*   `n`: The number of nodes in the network (1 <= n <= 500).
*   `edges`: A list of tuples, where each tuple `(u, v, bandwidth, failure_probability)` represents an undirected edge between node `u` and node `v`. `bandwidth` is an integer representing the capacity of the edge (1 <= bandwidth <= 1000), and `failure_probability` is a float between 0 and 1 representing the probability that the edge will fail.
*   `s`: The source node (0 <= s < n).
*   `d`: The destination node (0 <= d < n).
*   `b`: The minimum required bandwidth (1 <= b <= 1000). The selected path from `s` to `d` must have bandwidth to transmit `b`.

**Output:**

*   A float representing the maximum reliability (probability of success) of any path from `s` to `d` with at least bandwidth `b`. If no such path exists, return 0.0.

**Constraints and Considerations:**

*   The graph may not be fully connected.
*   There might be multiple paths from `s` to `d`.
*   You need to consider both bandwidth and reliability when finding the optimal path.
*   Optimize your solution for efficiency, as the network size can be relatively large.
*   Floating-point precision is important; ensure your comparisons and calculations are accurate enough to avoid incorrect results.  The tests will use a tolerance of `1e-9` for comparing floating point values.
*   Consider potential overflow issues when calculating probabilities.
*   Assume there is at most one edge between any two nodes.
*   The total number of edges is limited by the number of nodes, the total number of edges `e <= n*(n-1)/2`.

**Example:**

```python
n = 4
edges = [
    (0, 1, 100, 0.1),
    (0, 2, 50, 0.2),
    (1, 2, 80, 0.05),
    (1, 3, 120, 0.15),
    (2, 3, 60, 0.08)
]
s = 0
d = 3
b = 60

# Expected output: 0.7346  (Path 0->1->3 has reliability (1-0.1)*(1-0.15) = 0.765 and bandwidth 100 and 120, path 0->2->3 has reliability (1-0.2)*(1-0.08) = 0.736 and bandwidth 50 and 60, and path 0->1->2->3 has reliability (1-0.1)*(1-0.05)*(1-0.08) = 0.7346 and bandwidth 100, 80, and 60)

```

**Note**: This problem requires a combination of graph traversal, bandwidth constraints, and probability calculations. Finding an efficient algorithm that optimizes for both bandwidth and reliability is key to solving this problem.  Consider using appropriate data structures and algorithms.
