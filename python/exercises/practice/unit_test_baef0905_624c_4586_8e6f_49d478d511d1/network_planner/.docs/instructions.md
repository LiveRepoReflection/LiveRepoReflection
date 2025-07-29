## Project Name:

```
OptimalNetworkPlanner
```

## Question Description:

You are tasked with designing a communication network for a large distributed system. The system consists of `N` nodes, each identified by a unique integer from `0` to `N-1`.

You are given a list of `M` potential communication links. Each link is represented by a tuple `(u, v, cost, latency)`, where:

*   `u` and `v` are the IDs of the two nodes connected by the link.
*   `cost` is the monetary cost of establishing the link.
*   `latency` is the time it takes for a message to travel across the link.

Your goal is to design a network that satisfies the following requirements:

1.  **Connectivity:** Every node must be able to communicate with every other node, either directly or indirectly through other nodes. In other words, the network must be a connected graph.

2.  **Latency Constraint:** For each pair of nodes (u, v), the maximum latency of the shortest path between them must not exceed `L`. The shortest path is defined as the path with the minimum total latency.

3.  **Budget Constraint:** The total cost of establishing the links in the network must not exceed `B`.

4.  **Optimization Goal:** Among all possible networks that satisfy the above constraints, you must find the network that minimizes the *average* latency between all pairs of nodes.  The average latency is calculated as the sum of shortest path latencies between all pairs of nodes, divided by the total number of pairs (`N * (N - 1) / 2`).

You are required to write a function `optimal_network_plan(N, M, links, L, B)` that takes the following inputs:

*   `N`: The number of nodes in the system (integer).
*   `M`: The number of potential communication links (integer).
*   `links`: A list of tuples, where each tuple represents a potential link in the format `(u, v, cost, latency)` (list of tuples).
*   `L`: The maximum allowed latency between any two nodes (integer).
*   `B`: The maximum budget allowed for establishing the network (integer).

The function should return a list of tuples, representing the links included in the optimal network plan. Each tuple in the returned list should be in the same format as the input `links` (i.e., `(u, v, cost, latency)`). If no network can satisfy all constraints, return an empty list.

**Constraints:**

*   `1 <= N <= 100`
*   `0 <= M <= N * (N - 1) / 2`
*   `0 <= u, v < N`
*   `u != v`
*   `1 <= cost <= 1000`
*   `1 <= latency <= 1000`
*   `1 <= L <= 10000`
*   `1 <= B <= 100000`

**Example:**

```python
N = 4
M = 5
links = [
    (0, 1, 10, 5),
    (0, 2, 15, 8),
    (1, 2, 20, 10),
    (1, 3, 25, 12),
    (2, 3, 30, 15),
]
L = 25
B = 60

result = optimal_network_plan(N, M, links, L, B)
# Possible optimal result: [(0, 1, 10, 5), (0, 2, 15, 8), (1, 3, 25, 12)]
```

**Note:** This problem requires careful consideration of graph algorithms, constraint satisfaction, and optimization techniques. Efficient implementation is crucial to solve the problem within reasonable time limits.  Multiple valid solutions may exist. Your solution should aim to find *one* optimal solution. The judge may have hidden test cases with strict time limits, and inefficient implementations would likely fail.
