## Question: Optimal Multi-Source Routing

### Description

You are tasked with designing an efficient routing algorithm for a large-scale distributed system. The system consists of `N` nodes, interconnected via a network. Each node has a unique ID from `0` to `N-1`.

A crucial requirement is to enable **multi-source routing**. This means, given a set of source nodes `S` and a destination node `D`, the algorithm must find the optimal path from *any* node in `S` to `D`.  Optimality is defined as minimizing the **total cost** of the path.

The network is represented as a weighted, directed graph. The weights represent the cost of traversing a direct link between two nodes. Some links might be unidirectional. If there is no directed link between node A and B, the cost of traversing from A to B is considered infinite (or practically, a very large number).

Your goal is to implement a function that takes the following inputs:

1.  `N`: The number of nodes in the network (1 <= N <= 10^5).
2.  `edges`: A list of tuples, where each tuple `(u, v, w)` represents a directed edge from node `u` to node `v` with a cost of `w` (0 <= u, v < N, 1 <= w <= 10^4).  There can be multiple edges between two nodes with different weights.
3.  `S`: A set of source node IDs (each ID is between 0 and N-1). The set `S` is non-empty.
4.  `D`: The destination node ID (0 <= D < N).

The function should return the minimum cost to reach the destination node `D` from any of the source nodes in `S`. If there is no path from any node in `S` to `D`, return -1.

**Constraints and Considerations:**

*   **Scale:** The network can be quite large (up to 10^5 nodes), so your solution needs to be efficient.  Brute-force approaches will likely time out.
*   **Edge Cases:** Handle cases where there are no paths between source and destination, where the source and destination are the same, or where the graph is disconnected.
*   **Optimization:** Prioritize minimizing the execution time of your algorithm.  Consider appropriate data structures and algorithmic techniques.
*   **Multiple Edges:** The graph can have multiple edges between two nodes with different weights. You must consider only the minimum edge weight for each pair of nodes.
*   **Negative Weights are NOT allowed.** All edge weights are positive.

**Example:**

```python
N = 5
edges = [(0, 1, 5), (0, 2, 3), (1, 3, 6), (2, 3, 2), (3, 4, 4), (0, 4, 15)]
S = {0, 1}
D = 4

# Possible paths:
# - 0 -> 4: cost 15
# - 0 -> 2 -> 3 -> 4: cost 3 + 2 + 4 = 9
# - 1 -> 3 -> 4: cost 6 + 4 = 10

# Minimum cost: 9
```

**Your Task:**

Write a Python function `optimal_multi_source_routing(N, edges, S, D)` that efficiently calculates and returns the minimum cost to reach the destination node `D` from any of the source nodes in the set `S`.
