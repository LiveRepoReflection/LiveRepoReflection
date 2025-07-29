Okay, I'm ready to craft a challenging Go programming problem. Here it is:

## Project Name

```
efficient-network
```

## Question Description

You are tasked with designing and implementing a highly efficient and resilient communication network. The network consists of `n` nodes, each identified by a unique integer from `0` to `n-1`. The nodes are interconnected via bidirectional communication channels. Due to budget constraints, the network is sparsely connected.

Your goal is to implement a system capable of handling two types of queries efficiently:

1.  **Connectivity Check:** Given two node IDs, determine if there exists a path between them.

2.  **Critical Link Identification:** Identify and return a list of all 'critical links' in the network. A critical link is defined as a communication channel (edge) whose removal would disconnect at least two previously connected nodes. In other words, it is a bridge between two parts of the graph.

**Input:**

*   `n`: The number of nodes in the network (1 <= n <= 100,000).
*   `edges`: A list of tuples, where each tuple `(u, v)` represents a bidirectional communication channel between node `u` and node `v` (0 <= u, v < n, u != v). The number of edges `m` (0 <= m <= 200,000).

**Output:**

Implement the following functions:

*   `isConnected(node1 int, node2 int) bool`: Returns `true` if there is a path between `node1` and `node2`, and `false` otherwise.
*   `getCriticalLinks() [][]int`: Returns a list of critical links, where each critical link is represented as a list of two integers `[u, v]`. The order of links in the output list does not matter. The order of nodes within each link (e.g., `[u, v]` vs. `[v, u]`) also does not matter.

**Constraints and Requirements:**

*   **Efficiency is paramount.**  The `isConnected` function must execute in O(log n) average time complexity or better. The `getCriticalLinks` function should be as efficient as possible, ideally close to O(m + n) where `m` is the number of edges.
*   The network may not be fully connected. There might be multiple disjoint components.
*   The network topology is static (i.e., the nodes and edges do not change after initialization).
*   You must pre-process the network data during initialization to optimize query performance.  Naive solutions that perform a full graph traversal for each query will likely time out.
*   Consider using advanced data structures and algorithms to achieve the required performance.  Possible approaches include:
    *   Disjoint Set Union (DSU) with path compression and union by rank for connectivity checks.
    *   Tarjan's algorithm for finding bridges (critical links).
*   The `edges` list may contain duplicate entries or self-loops. These should be handled gracefully during initialization (e.g., ignored or treated as no-ops).
*   Your solution must be thread-safe. Multiple goroutines might concurrently call `isConnected` and `getCriticalLinks`.

**Example:**

```
n = 6
edges = [[0, 1], [0, 2], [1, 3], [2, 3], [3, 4], [4, 5]]

isConnected(0, 5)  // Returns true
getCriticalLinks() // Returns [[3, 4]] (or [[4, 3]])
```

**Grading Criteria:**

*   Correctness: The code must correctly identify connected components and critical links for all valid inputs.
*   Efficiency: The code must meet the specified time complexity requirements.
*   Code Quality: The code must be well-structured, readable, and maintainable. Thread safety will be checked.

This problem requires a strong understanding of graph algorithms and data structures, as well as the ability to optimize code for performance and handle concurrency. Good luck!
