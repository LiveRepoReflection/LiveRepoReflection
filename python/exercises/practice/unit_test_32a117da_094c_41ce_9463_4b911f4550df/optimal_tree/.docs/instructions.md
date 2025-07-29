## Problem Title: Optimal Multi-Source Shortest Path Tree Construction

### Problem Description

You are given a directed graph representing a transportation network. The graph consists of `N` nodes (numbered from 0 to N-1) and `M` directed edges. Each edge has a source node, a destination node, and a cost (a non-negative integer) associated with traversing it.

You are also given a set `K` of source nodes. Your task is to construct an *optimal* shortest-path tree rooted at these `K` source nodes, such that the sum of the shortest path distances from each node in the graph to its *closest* source node is minimized.

Formally:

1.  For each node `i` in the graph, find the shortest distance `d(i)` from node `i` to its nearest source node (considering only the nodes in `K`).

2.  Construct a directed tree by selecting a subset of edges from the original graph. This tree must satisfy the following:
    *   For each node `i` in the graph, the path from `i` to its nearest source node in the tree must have the same cost `d(i)` as the shortest path in the original graph.
    *   The tree must be rooted at the K source nodes (meaning there is a directed path from every node to at least one of the source nodes in K).

3.  Among all such trees, minimize the total cost of edges included in the tree. The total cost of the tree is defined as the sum of the costs of the edges included in the tree.

**Input:**

*   `N`: The number of nodes in the graph (1 <= N <= 10<sup>5</sup>).
*   `M`: The number of edges in the graph (0 <= M <= 2 * 10<sup>5</sup>).
*   `edges`: A list of tuples, where each tuple `(u, v, cost)` represents a directed edge from node `u` to node `v` with cost `cost` (0 <= u, v < N, 0 <= cost <= 10<sup>4</sup>).
*   `K`: The number of source nodes (1 <= K <= N).
*   `sources`: A list of the source node indices (0 <= source < N).

**Output:**

Return the minimum possible total cost of the edges in the optimal shortest-path tree. If no such tree can be constructed (e.g., the graph is disconnected), return -1.

**Constraints:**

*   The graph may contain cycles.
*   There might be multiple edges between two nodes.
*   The graph may not be strongly connected.
*   You need to provide an efficient solution that can handle large graphs.

**Example:**

```
N = 6
M = 7
edges = [(0, 1, 2), (0, 2, 4), (1, 2, 1), (1, 3, 7), (2, 4, 3), (3, 5, 1), (4, 5, 5)]
K = 2
sources = [0, 5]

Output: 10

Explanation:
- Shortest distances: d(0)=0, d(1)=2, d(2)=3, d(3)=9, d(4)=6, d(5)=0.
- One possible optimal tree: Edges (0,1,2), (1,2,1), (2,4,3), (3,5,1), (1,3,7) are NOT included. An optimal tree is: (0,1,2), (1,2,1), (2,4,3), (4,5,5), (3,5,1) with total cost 2 + 1 + 3 + 1 = 7.

```

**Complexity Expectations:**

*   Time complexity: Aim for a solution with O(M log N) time complexity or better.
*   Space complexity: Aim for a solution with O(N + M) space complexity.

This problem requires a strong understanding of graph algorithms, shortest paths, and tree construction. Efficient implementation is crucial for passing all test cases. Good luck!
