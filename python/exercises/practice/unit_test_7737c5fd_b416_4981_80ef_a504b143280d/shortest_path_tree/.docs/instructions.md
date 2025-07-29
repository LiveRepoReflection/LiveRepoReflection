## Question Title: Optimal Multi-Source Shortest Path Tree

### Question Description:

You are given a weighted, directed graph representing a transportation network. The graph consists of `n` nodes (numbered from 0 to n-1) and `m` edges. Each edge has a source node, a destination node, and a weight representing the travel time along that edge.

Additionally, you are given a set of `k` source nodes. Your task is to construct an **Optimal Multi-Source Shortest Path Tree (OMSSPT)** rooted at these `k` source nodes.

An OMSSPT is a directed tree that satisfies the following properties:

1.  **Reachability:** All nodes reachable from at least one of the `k` source nodes in the original graph must be included in the tree.
2.  **Shortest Paths:** For every reachable node `v`, the path from the closest source node in `k` to `v` in the OMSSPT must have the same shortest path distance as the shortest path from any of the source nodes `k` to `v` in the original graph. If multiple shortest paths exist, any one of them is acceptable.
3.  **Optimality:** The total weight of all edges in the OMSSPT should be minimized. Among all possible shortest path trees satisfying properties 1 and 2, choose the one with the minimum total edge weight.

**Input:**

*   `n`: The number of nodes in the graph (1 <= n <= 10<sup>5</sup>).
*   `m`: The number of edges in the graph (0 <= m <= 2 * 10<sup>5</sup>).
*   `edges`: A list of tuples, where each tuple `(u, v, w)` represents a directed edge from node `u` to node `v` with weight `w` (0 <= u, v < n, 1 <= w <= 10<sup>3</sup>).
*   `sources`: A list of source nodes (0 <= source < n). It's guaranteed that there is at least one source node. All source nodes are unique.

**Output:**

Return a list of tuples representing the edges of the OMSSPT.  Each tuple should be in the format `(u, v, w)`, representing a directed edge from node `u` to node `v` with weight `w` in the constructed tree. The order of edges does not matter. If no nodes are reachable from the source nodes, return an empty list.

**Constraints:**

*   Your solution must have a time complexity of O(m log n), where 'm' is the number of edges and 'n' is the number of nodes. Solutions with higher time complexity will not pass.
*   The graph might not be strongly connected.
*   Multiple edges between two nodes are allowed, but your solution needs to handle them correctly (choose the edge with minimal weight).
*   Self-loops are allowed.

**Example:**

```
n = 5
m = 6
edges = [(0, 1, 2), (0, 2, 4), (1, 2, 1), (1, 3, 5), (2, 3, 2), (4, 0, 3)]
sources = [0, 4]

Output (one possible solution):
[(0, 1, 2), (1, 2, 1), (2, 3, 2), (4, 0, 3)]
```

**Explanation:**

*   Nodes 0, 1, 2, and 3 are reachable from sources 0 and 4. Node 4 can reach node 0.
*   The shortest path from 0 to 1 is 0 -> 1 (distance 2).
*   The shortest path from 0 to 2 is 0 -> 1 -> 2 (distance 3).
*   The shortest path from 0 to 3 is 0 -> 1 -> 2 -> 3 (distance 5).
*   The shortest path from 4 to 0 is 4 -> 0 (distance 3).

The selected edges form a tree rooted at 0 and 4 that maintains the shortest path distances from the sources. The total weight is 2 + 1 + 2 + 3 = 8. There might be other valid trees, but this one satisfies the conditions.

**Judging Criteria:**

Your code will be judged based on:

*   **Correctness:** Does your solution produce a valid OMSSPT?
*   **Completeness:** Does your solution handle all valid graph inputs, including edge cases like disconnected graphs, multiple edges, and self-loops?
*   **Efficiency:** Does your solution meet the time complexity requirement of O(m log n)?
*   **Optimality:** Does your solution produce a valid tree with the minimal weight?
