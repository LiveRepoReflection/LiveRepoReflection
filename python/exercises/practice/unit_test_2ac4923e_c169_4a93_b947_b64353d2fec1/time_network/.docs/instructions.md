## Problem: Optimal Multi-Source Shortest Paths with Time-Dependent Edge Costs

**Description:**

You are given a directed graph representing a transportation network. The graph consists of `N` nodes (numbered 0 to N-1) representing locations, and `M` directed edges representing transportation routes between these locations. Each edge `(u, v)` has a time-dependent cost associated with it, meaning the cost of traversing the edge depends on the time you *start* traversing it.

Specifically, for an edge `(u, v)`, you are given a list of `K` (timestamp, cost) pairs `[(t_1, c_1), (t_2, c_2), ..., (t_K, c_K)]`. These pairs are sorted by timestamp (i.e., `t_1 < t_2 < ... < t_K`). If you start traversing the edge `(u, v)` at time `t`, the cost you incur is `c_i` where `t_i` is the largest timestamp such that `t_i <= t`. If `t < t_1`, the cost is considered infinite (you cannot traverse the edge before time `t_1`).

You are also given a list of `S` source nodes. The goal is to find the minimum cost to reach all other nodes in the graph from *any* of the source nodes, starting at time 0.

**Input:**

*   `N`: The number of nodes in the graph (1 <= N <= 1000).
*   `M`: The number of edges in the graph (0 <= M <= 5000).
*   `edges`: A list of `M` tuples, where each tuple represents an edge: `(u, v, time_costs)`.
    *   `u`: The source node of the edge (0 <= u < N).
    *   `v`: The destination node of the edge (0 <= v < N).
    *   `time_costs`: A list of `K` tuples, where each tuple represents a time-dependent cost: `[(t_1, c_1), (t_2, c_2), ..., (t_K, c_K)]`.
        *   `t_i`: The timestamp (0 <= t_i <= 10^9).
        *   `c_i`: The cost (1 <= c_i <= 10^9).
        *   `1 <= K <= 100` for each edge.
*   `S`: A list of source nodes (1 <= |S| <= N), where each element is a node index (0 <= s < N).

**Output:**

*   A list of `N` integers, where the `i`-th integer represents the minimum cost to reach node `i` from *any* of the source nodes, starting at time 0. If a node is unreachable from any of the source nodes, its corresponding value should be `-1`.

**Constraints:**

*   The graph is directed.
*   There may be multiple edges between the same pair of nodes.
*   The graph may contain cycles.
*   The timestamps `t_i` for each edge are strictly increasing.
*   The cost `c_i` can be different for different edges, and the same cost can also appear multiple times in the same edge.

**Example:**

```
N = 4
M = 3
edges = [
    (0, 1, [(0, 10), (5, 20)]),
    (0, 2, [(2, 5), (7, 15)]),
    (1, 3, [(1, 30)])
]
S = [0]

Output: [0, 10, 5, 40]
```

**Explanation:**

*   Node 0 is a source node, so its cost is 0.
*   To reach node 1, we can take the edge (0, 1) starting at time 0, with a cost of 10.
*   To reach node 2, we can take the edge (0, 2) starting at time 2, with a cost of 5.
*   To reach node 3, we can take the edge (0, 1) to reach node 1 with a cost of 10, then take the edge (1, 3) starting at time 10, with a cost of 30. The total cost is 10 + 30 = 40.

**Optimization Requirements:**

*   The naive approach of trying all possible paths will likely result in a Time Limit Exceeded (TLE) error.
*   You need to optimize your solution to handle large graphs and time-dependent costs efficiently.  Consider using appropriate data structures and algorithms to achieve optimal performance.

**Multiple Valid Approaches with Different Trade-offs:**

*   Dijkstra's algorithm can be adapted to handle time-dependent edge costs. However, you need to be careful about how you update the distances based on the arrival time at a node.
*   Consider using a priority queue to efficiently explore the nodes with the lowest current cost.

This problem combines graph traversal, time-dependent costs, and optimization challenges, making it a difficult and sophisticated problem suitable for programming competitions. Good luck!
