## Question Title: Efficient Multi-Source Shortest Paths with Resource Constraints

### Question Description

You are tasked with designing an efficient algorithm to find the shortest paths from multiple source nodes to all other nodes in a weighted, directed graph, subject to resource constraints.

**Graph Description:**

*   The graph consists of `N` nodes, numbered from `0` to `N-1`.
*   The graph has `M` directed edges. Each edge is defined by a tuple `(u, v, w, c)`, where:
    *   `u` is the source node of the edge.
    *   `v` is the destination node of the edge.
    *   `w` is the weight (distance/cost) of the edge.  `w` is a non-negative integer.
    *   `c` is the resource consumption of traversing the edge. `c` is a non-negative integer.

**Source Nodes:**

*   You are given a set of `K` source nodes, denoted by `S = {s1, s2, ..., sk}`.

**Resource Constraint:**

*   Each node `i` has a resource capacity `R[i]`.
*   The total resource consumption along any path from a source node to a destination node must not exceed the resource capacity of the destination node.  Formally, for any path `p = {v1, v2, ..., vn}` where `v1` is a source node and `vn` is the destination node, the sum of edge resource consumptions `c(v1, v2) + c(v2, v3) + ... + c(v(n-1), vn)` must be less than or equal to `R[vn]`.

**Objective:**

Compute the shortest distance from *any* source node in `S` to every other node in the graph, *subject to the resource constraint*. If a node is unreachable from any source node while respecting the resource constraint, its shortest distance should be considered infinite (represented as -1).

**Input:**

*   `N`: The number of nodes in the graph.
*   `M`: The number of edges in the graph.
*   `edges`: A list of `M` tuples, where each tuple `(u, v, w, c)` represents a directed edge.
*   `S`: A list of `K` integers representing the source nodes.
*   `R`: A list of `N` integers representing the resource capacity of each node.

**Output:**

*   A list of `N` integers, `D`, where `D[i]` represents the shortest distance from any source node in `S` to node `i`, subject to the resource constraint. If node `i` is unreachable, `D[i]` should be -1.

**Constraints:**

*   `1 <= N <= 10^5`
*   `1 <= M <= 2 * 10^5`
*   `1 <= K <= N`
*   `0 <= u, v < N`
*   `0 <= w <= 10^4`
*   `0 <= c <= 10^4`
*   `0 <= R[i] <= 10^9`
*   The graph may contain cycles.
*   The graph may not be strongly connected.
*   Multiple edges between the same pair of nodes are allowed.

**Efficiency Requirements:**

Your solution must be efficient enough to handle large graphs within a reasonable time limit.  Consider the time and space complexity of your chosen algorithm.  Solutions with high time complexity (e.g., O(N^2) or higher for a single-source shortest path) are unlikely to pass.

**Example:**

```
N = 5
M = 6
edges = [[0, 1, 5, 2], [0, 2, 3, 1], [1, 3, 6, 3], [2, 3, 2, 1], [3, 4, 4, 2], [2, 4, 8, 4]]
S = [0]
R = [10, 5, 5, 5, 10]

Output:
D = [0, 5, 3, 5, 9]
```

**Explanation:**

*   Shortest path from 0 to 1 is 0 -> 1 (distance 5, resource consumption 2 <= R[1] = 5).
*   Shortest path from 0 to 2 is 0 -> 2 (distance 3, resource consumption 1 <= R[2] = 5).
*   Shortest path from 0 to 3 is 0 -> 2 -> 3 (distance 3 + 2 = 5, resource consumption 1 + 1 = 2 <= R[3] = 5).
*   Shortest path from 0 to 4 is 0 -> 2 -> 3 -> 4 (distance 3 + 2 + 4 = 9, resource consumption 1 + 1 + 2 = 4 <= R[4] = 10).

```
N = 3
M = 3
edges = [[0, 1, 1, 5], [1, 2, 1, 5], [0, 2, 5, 1]]
S = [0]
R = [10, 4, 10]

Output:
D = [0, -1, 5]
```

**Explanation:**

Node 1 is unreachable due to the resource constraint of 4.
* Path 0 -> 1 has weight 1 and resource consumption 5, which is greater than R[1] = 4.
```
N = 4
M = 4
edges = [[0, 1, 1, 1], [1, 2, 1, 1], [2, 3, 1, 1], [0, 3, 5, 5]]
S = [0]
R = [10, 2, 2, 2]

Output:
D = [0, 1, 2, -1]
```

**Explanation:**

Node 3 is unreachable due to the resource constraint of 2.
* Path 0 -> 1 -> 2 -> 3 has weight 3 and resource consumption 3, which is greater than R[3] = 2.
* Path 0 -> 3 has weight 5 and resource consumption 5, which is greater than R[3] = 2.
