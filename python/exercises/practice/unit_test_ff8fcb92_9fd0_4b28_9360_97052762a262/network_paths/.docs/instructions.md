Okay, I'm ready to craft a challenging programming competition problem.  Here it is:

### Project Name

`NetworkOptimization`

### Question Description

A large-scale distributed system is represented as a directed graph where nodes represent servers and edges represent network connections.  Each edge has a *capacity* (maximum data flow rate) and a *latency* (time delay for data transfer).

You are given the following:

*   `N`: The number of servers in the system (numbered 0 to N-1).
*   `edges`: A list of tuples, where each tuple `(u, v, capacity, latency)` represents a directed edge from server `u` to server `v` with the specified capacity and latency.
*   `source`: The ID of the source server (an integer between 0 and N-1).
*   `destination`: The ID of the destination server (an integer between 0 and N-1).
*   `k`: An integer representing the number of independent paths you need to find.

Your task is to find `k` *edge-disjoint* paths from the `source` server to the `destination` server. An edge-disjoint path is defined as a path that does not share any edges with any other path in the solution set.

For each of the `k` paths, you must determine:

1.  The list of server IDs in the path, in order from `source` to `destination`.
2.  The total latency of the path (sum of latencies of the edges in the path).
3.  The bottleneck capacity of the path (the minimum capacity of any edge in the path).

Your solution should return a list of `k` tuples, where each tuple is of the form: `(path, total_latency, bottleneck_capacity)`.

**Constraints and Requirements:**

*   **Edge Disjointness:** The `k` paths returned must be strictly edge-disjoint.  Sharing even a single edge invalidates the solution.
*   **Path Validity:** Each path must start at the `source` and end at the `destination`. All intermediate nodes must be reachable from the source and be able to reach the destination.
*   **Maximizing Bottleneck Capacity:** The algorithm should attempt to maximize the *sum* of the bottleneck capacities of all `k` paths. It is more important to have paths with higher bottleneck capacity, even if it means slightly higher latency.
*   **Handling Cycles:** The graph may contain cycles. Your solution must handle cycles gracefully and avoid infinite loops.
*   **Efficiency:** The algorithm must be efficient enough to handle graphs with up to 1000 nodes and 5000 edges within a reasonable time limit (e.g., a few seconds).
*   **No guarantee of existence:** If it's not possible to find k edge-disjoint paths from source to destination, the algorithm should return an empty list.
*   **Latency Tie-breaker:** If multiple possible sets of `k` edge-disjoint paths have the same total bottleneck capacity, return the set of paths with the lowest total latency.

**Input Format:**

```python
def find_k_edge_disjoint_paths(N: int, edges: list[tuple[int, int, int, int]], source: int, destination: int, k: int) -> list[tuple[list[int], int, int]]:
    """
    Finds k edge-disjoint paths from source to destination in a directed graph.

    Args:
        N: The number of servers in the system (nodes).
        edges: A list of tuples, where each tuple (u, v, capacity, latency)
               represents a directed edge from server u to server v.
        source: The ID of the source server.
        destination: The ID of the destination server.
        k: The number of edge-disjoint paths to find.

    Returns:
        A list of k tuples, where each tuple is of the form:
        (path, total_latency, bottleneck_capacity).
        Returns an empty list if k edge-disjoint paths cannot be found.
    """
    # Your implementation here

```

**Example:**

```python
N = 6
edges = [
    (0, 1, 10, 1),  # source
    (0, 2, 5, 2),
    (1, 3, 7, 3),
    (2, 3, 8, 1),
    (3, 4, 12, 2),
    (3, 5, 3, 4), # destination
    (1, 5, 5, 2),
    (2, 4, 2, 3),
    (4, 5, 9, 1)
]
source = 0
destination = 5
k = 2

result = find_k_edge_disjoint_paths(N, edges, source, destination, k)
print(result)
# Expected output (order might vary, but the total bottleneck capacity should be maximized):
# [([0, 1, 5], 3, 5), ([0, 2, 3, 5], 7, 3)]
# OR
# [([0, 2, 3, 5], 7, 3), ([0, 1, 5], 3, 5)]
```

This problem requires a combination of graph traversal, maximum flow/minimum cut concepts (though explicitly using those algorithms might be too slow), and careful path selection.  It challenges the solver to consider multiple constraints and optimize for both capacity and latency. Good luck!
