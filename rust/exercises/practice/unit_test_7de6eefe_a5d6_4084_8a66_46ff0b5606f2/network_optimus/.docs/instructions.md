Okay, here's a challenging Rust coding problem designed to be comparable to a LeetCode "Hard" level question.

## Project Name

`network-optimus`

## Question Description

You are designing a robust and efficient communication network for a distributed system. The system consists of `n` nodes, each uniquely identified by an integer from `0` to `n-1`.  The nodes need to exchange data frequently.  Due to physical constraints, not all nodes can directly communicate with each other. The possible direct communication links between nodes are represented as a list of edges.

Each edge is represented as a tuple `(u, v, cost)`, where `u` and `v` are the IDs of the nodes connected by the edge, and `cost` is a non-negative integer representing the cost of sending data directly between those two nodes. The network is undirected, meaning if `(u, v, cost)` exists, data can flow from `u` to `v` and from `v` to `u` at the same cost.  Multiple edges between the same pair of nodes are allowed, but they will always have different costs.

**The Challenge:**

Implement a function that determines the minimum *average* cost to send data between *any* two nodes in the network, subject to a crucial reliability constraint. The reliability constraint is defined by a *critical threshold* `k`.

To meet the reliability constraint, for *every* pair of nodes `(i, j)` in the network, there must exist at least `k` *distinct* paths between them. Distinct here means that no two paths share any edges.  The cost of a path is the sum of the costs of its edges. The average cost is calculated by summing the minimum cost achievable between each of the `n * (n - 1) / 2` pairs of nodes (considering only paths that satisfy the `k` distinct paths criteria), and then dividing by the total number of node pairs.

If, for *any* pair of nodes, it is impossible to find `k` distinct paths between them, the function should return `None`.

**Function Signature:**

```rust
fn min_average_cost(n: usize, edges: Vec<(usize, usize, u32)>, k: usize) -> Option<f64> {
    // Implementation here
}
```

**Input:**

*   `n`: The number of nodes in the network (1 <= n <= 100).
*   `edges`: A vector of tuples representing the direct communication links.  (0 <= u, v < n, 0 <= cost <= 1000). The number of edges can be up to 5000.
*   `k`: The minimum number of distinct paths required between any two nodes (1 <= k <= 5).

**Output:**

*   `Some(average_cost)`: The minimum average cost to send data between any two nodes in the network, rounded to 6 decimal places.
*   `None`: If it's impossible to find `k` distinct paths between all pairs of nodes.

**Constraints:**

*   The graph may not be fully connected initially.
*   You must handle disconnected graphs gracefully (return `None`).
*   Optimize for performance, as the input size can be significant. A naive brute-force approach is unlikely to pass all test cases.
*   Edge costs are non-negative.
*   The graph is undirected.
*   The function should be implemented in Rust.

**Considerations:**

*   This problem requires a combination of graph algorithms and careful design to meet the performance requirements.
*   Think about how to efficiently find the *k* shortest distinct paths between any two nodes.  Consider the complexity of your approach.
*   Remember to handle edge cases, such as disconnected components or situations where `k` distinct paths cannot be found.
*   The averaging calculation must be accurate.

Good luck! This question will test your understanding of graph theory, algorithms, and Rust programming.
