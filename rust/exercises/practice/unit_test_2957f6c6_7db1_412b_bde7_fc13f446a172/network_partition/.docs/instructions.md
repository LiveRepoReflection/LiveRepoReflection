Okay, here's a challenging Rust programming problem, designed to be complex and require careful consideration of algorithms, data structures, and edge cases.

## Problem: Network Partitioning for Maximum Resilience

**Description:**

You are designing a highly reliable distributed system. The system consists of `n` nodes, interconnected via a network. The network's connectivity is represented as an undirected graph, where nodes are vertices and connections between them are edges. Each connection (edge) has a *resilience score* – a positive integer representing the connection's robustness. Higher resilience scores indicate more stable and less likely to fail connections.

Due to unforeseen circumstances (e.g., cyberattacks, natural disasters), parts of the network might become disconnected. Your goal is to determine the *minimum resilience loss* required to partition the network into `k` *disconnected* components (where `k` is a given integer).

*Resilience Loss* is defined as the sum of resilience scores of the edges removed to achieve the desired partition.

**Input:**

*   `n`: The number of nodes in the network (1 <= `n` <= 500).
*   `k`: The desired number of disconnected components (1 <= `k` <= `n`).
*   `edges`: A vector of tuples, where each tuple `(u, v, resilience)` represents an undirected edge between node `u` and node `v` with resilience score `resilience`. Node indices are 0-based (0 <= `u`, `v` < `n`). Resilience scores are positive integers (1 <= `resilience` <= 10,000). There will be no self-loops or duplicate edges.

**Output:**

*   The minimum resilience loss required to partition the network into exactly `k` disconnected components.
*   If it's impossible to partition the network into exactly `k` disconnected components (even by removing all edges), return -1.

**Constraints and Considerations:**

*   **Edge Cases:** Handle cases where `k` is 1 (no edges need to be removed if the graph is already disconnected into one component and should return 0 if the graph is connected), `k` is `n` (all edges must be removed), and cases where the graph is already disconnected into more or fewer than `k` components.
*   **Optimization:** The algorithm must be efficient. Naive approaches will likely time out for larger graphs. Consider using appropriate graph algorithms.
*   **Multiple Approaches:** There might be multiple valid approaches, but some will be more efficient than others. The efficiency of your solution will be a significant factor.
*   **Disconnected Components Definition:** A disconnected component is a set of nodes where every node in the set can reach every other node in the same set through some path, but no node in the set can reach any node in any other set.
*   **Graph Representation:** You are free to choose the most appropriate internal representation of the graph (e.g., adjacency list, adjacency matrix). The input is given as a list of edges, so you'll need to build your graph representation.
*   **Algorithmic Efficiency:** Pay close attention to the time and space complexity of your solution. Efficient algorithms and data structures are crucial for passing all test cases.
*   **Rust-Specific Considerations:** Leverage Rust's features for memory safety and performance. Consider using appropriate data structures from the standard library or crates like `petgraph` if needed.

**Example:**

```
n = 4
k = 2
edges = [(0, 1, 10), (1, 2, 5), (2, 3, 3), (3, 0, 7), (0, 2, 2)]

Expected Output: 10

Explanation: Removing the edge (0, 1) with resilience 10 will disconnect the graph into two components: {0, 2, 3} and {1}. This is the minimum resilience loss to achieve k = 2.
```

This problem requires a solid understanding of graph algorithms, optimization techniques, and careful handling of edge cases. Good luck!
