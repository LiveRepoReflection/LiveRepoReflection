## Question: Optimal Meeting Point in a Weighted Tree

### Question Description

You are given a connected, undirected tree with `n` nodes, numbered from 0 to `n-1`. Each node `i` has a weight `w[i]` associated with it. The edges in the tree are represented as a list of tuples `edges`, where each tuple `(u, v, cost)` represents an edge between node `u` and node `v` with a traversal cost of `cost`.

Your task is to find the "optimal meeting point" in the tree. The optimal meeting point is the node `x` that minimizes the **weighted sum of distances** to all other nodes in the tree. The weighted sum of distances for a node `x` is defined as:

```
Cost(x) = Σ (distance(x, i) * w[i])  for all i from 0 to n-1
```

where `distance(x, i)` is the shortest path distance (sum of edge costs) between node `x` and node `i` in the tree.

**Your goal is to write a function that takes the number of nodes `n`, the list of edges `edges`, and the list of node weights `w`, and returns the node number `x` that minimizes `Cost(x)`. If there are multiple nodes that achieve the minimum cost, return the node with the smallest node number.**

**Constraints:**

*   `1 <= n <= 10^5`
*   `0 <= edges.length <= min(10^5, n*(n-1)/2)`
*   `edges[i].length == 3`
*   `0 <= u, v < n`
*   `u != v`
*   `1 <= cost <= 10^3`
*   `w.length == n`
*   `1 <= w[i] <= 10^3`
*   The graph represented by `edges` is a connected tree.

**Optimization Requirements:**

*   A naive solution that calculates the distance between all pairs of nodes for each potential meeting point will likely result in a Time Limit Exceeded (TLE) error. You need to find a more efficient algorithm.
*   Consider how you can reuse distance information calculated for one node to efficiently calculate distances for neighboring nodes.
*   Minimize memory usage, especially for larger trees.

**Edge Cases to Consider:**

*   A tree with a small number of nodes (e.g., `n=1`, `n=2`).
*   A tree where all nodes have the same weight.
*   A tree that is a star graph (one central node connected to all other nodes).
*   A tree with very large edge costs.

**Example:**

```
n = 4
edges = [[0, 1, 1], [0, 2, 5], [1, 3, 2]]
w = [3, 4, 2, 1]

# Expected Output: 1
```

**Explanation for the example:**

*   Cost(0) = (0\*3) + (1\*4) + (5\*2) + (3\*1) = 4 + 10 + 3 = 17
*   Cost(1) = (1\*3) + (0\*4) + (6\*2) + (2\*1) = 3 + 12 + 2 = 17
*   Cost(2) = (5\*3) + (6\*4) + (0\*2) + (8\*1) = 15 + 24 + 8 = 47
*   Cost(3) = (3\*3) + (2\*4) + (8\*2) + (0\*1) = 9 + 8 + 16 = 33

Both node 0 and node 1 have the minimum cost (17). Since we need to return the smallest node number, the answer is 1.
