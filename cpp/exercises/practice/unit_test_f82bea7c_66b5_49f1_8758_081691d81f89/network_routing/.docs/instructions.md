## Project Name:

**Optimal Network Routing**

## Question Description:

You are tasked with designing an efficient routing algorithm for a large-scale communication network. The network consists of `N` nodes (numbered 0 to N-1) and `M` bidirectional communication links. Each link connects two nodes and has an associated cost (a positive integer) representing the latency or bandwidth usage.

The network is dynamic, meaning links can fail or new links can be established. You need to implement a system that can handle these changes and efficiently calculate the optimal (lowest cost) path between any two nodes.

Your system must support the following operations:

1.  **`add_link(u, v, cost)`**: Adds a new link between nodes `u` and `v` with the given `cost`. If a link already exists between `u` and `v`, update its cost to the new `cost`. `0 <= u, v < N`, `1 <= cost <= 1000`.

2.  **`remove_link(u, v)`**: Removes the link between nodes `u` and `v`. If no link exists, the operation has no effect.

3.  **`get_optimal_path(start, end)`**: Returns the optimal (minimum cost) path between nodes `start` and `end`. If no path exists, return an empty vector. The path should be represented as a vector of node indices, starting with `start` and ending with `end`.  If multiple optimal paths exist, return any one of them. `0 <= start, end < N`.

**Constraints:**

*   `1 <= N <= 1000` (Number of nodes)
*   `0 <= M <= N * (N - 1) / 2` (Initial number of links)
*   The number of `add_link`, `remove_link`, and `get_optimal_path` operations will be up to 10000 in total.
*   The graph may not be connected initially and can become disconnected after link removals.
*   The cost of traversing a path is the sum of the costs of the links in that path.
*   Your solution should aim for the best possible performance for the `get_optimal_path` operation, as it will be called frequently.  Naive implementations will likely time out.  Consider the trade-offs between pre-computation and on-demand calculation.

**Example:**

```cpp
// Assume N = 5 initially
// add_link(0, 1, 5);
// add_link(1, 2, 3);
// add_link(0, 2, 10);
// get_optimal_path(0, 2); // Returns {0, 1, 2} (cost 8) or {0,2} (cost 10), {0,1,2} is optimal
// remove_link(1, 2);
// get_optimal_path(0, 2); // Returns {0, 2} (cost 10)

```

**Evaluation Criteria:**

Your solution will be evaluated based on:

*   **Correctness:**  Does the code produce the correct optimal paths?
*   **Efficiency:**  Does the code complete within the time limit, especially for a large number of queries?  The `get_optimal_path` call needs to be performant.
*   **Code Quality:** Is the code well-structured, readable, and maintainable?

**Hint:** Consider using appropriate data structures to represent the graph and exploring different shortest-path algorithms. Think about when it is appropriate to pre-compute information and when to compute it on demand.  Dynamic graph algorithms or caching strategies might be useful.
