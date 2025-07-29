## Problem: Highly Connected Component Collapse

**Description:**

You are given a directed graph represented by a list of nodes and a list of edges. Each node has a unique integer ID from 0 to N-1, where N is the total number of nodes in the graph. Each edge is a tuple `(source, destination)` representing a directed connection from the source node to the destination node.

A **Highly Connected Component (HCC)** is a subset of nodes within the graph such that:

1.  **Strongly Connected:** For any two nodes `u` and `v` within the HCC, there exists a directed path from `u` to `v` and a directed path from `v` to `u`.

2.  **Density Threshold:** The density of the subgraph induced by the HCC must be greater than or equal to a given threshold `density_threshold`. The density of a directed subgraph is defined as:

    `density = (number of edges within the subgraph) / (number of nodes in the subgraph * (number of nodes in the subgraph - 1))`

    Note that self-loops are not allowed in the subgraph when calculating the number of edges.

3.  **Maximality:** It is not possible to add any node to the HCC without violating either the strongly connected condition or the density threshold.

Your task is to identify and "collapse" all the HCCs in the given graph. Collapsing an HCC means:

1.  **Identify HCCs:** Find all the HCCs in the graph that satisfy the above conditions. If there are overlapping HCCs, your algorithm should find the largest possible set of non-overlapping HCCs that maximize the total number of nodes included in all selected HCCs.

2.  **Contract Nodes:** For each identified HCC, contract all nodes within the HCC into a single "supernode". The ID of the supernode will be the smallest node ID among all the nodes in the HCC.

3.  **Adjust Edges:**
    *   Remove any edges between nodes within the same HCC (as they are now a single supernode).
    *   For any edge `(u, v)` where `u` is in HCC\_A and `v` is in HCC\_B (and HCC\_A and HCC\_B are different HCCs), the edge becomes `(supernode_A, supernode_B)`, where `supernode_A` is the ID of the supernode representing HCC\_A and `supernode_B` is the ID of the supernode representing HCC\_B.
    *   If `u` is in HCC\_A and `v` is *not* in any HCC, the edge becomes `(supernode_A, v)`.
    *   If `u` is *not* in any HCC and `v` is in HCC\_B, the edge becomes `(u, supernode_B)`.
    *   Remove duplicate edges.

Your function should return a tuple containing:

1.  A list of the remaining nodes in the collapsed graph (represented by their IDs).
2.  A list of the remaining edges in the collapsed graph (represented as tuples of `(source, destination)`).  The nodes should be sorted in ascending order. The edges should be sorted lexicographically.

**Input:**

*   `num_nodes`: An integer representing the total number of nodes in the graph (0 to `num_nodes - 1`).
*   `edges`: A list of tuples, where each tuple `(source, destination)` represents a directed edge in the graph.
*   `density_threshold`: A float representing the minimum density required for an HCC.  0 <= `density_threshold` <= 1.

**Constraints:**

*   1 <= `num_nodes` <= 1000
*   0 <= number of `edges` <= 5000
*   0 <= `source`, `destination` < `num_nodes`
*   The graph may contain cycles.
*   The graph may be disconnected.
*   Finding the optimal set of non-overlapping HCCs that maximize the total number of nodes can be computationally expensive. Your solution should aim to find a reasonably good solution within a reasonable time limit (e.g., a few seconds).

**Example:**

```python
num_nodes = 6
edges = [(0, 1), (1, 0), (1, 2), (2, 1), (3, 4), (4, 3), (0, 3), (3, 5)]
density_threshold = 0.5

# Expected output (order might vary as long as lexicographical ordering is followed):
# nodes: [0, 3, 5]
# edges: [(0, 3), (3, 5)]

# Explanation:
# 1. Nodes 0, 1, and 2 form an HCC (density = 2/3 >= 0.5).  They are collapsed into supernode 0.
# 2. Nodes 3 and 4 form an HCC (density = 1 >= 0.5). They are collapsed into supernode 3.
# 3. Remaining nodes: 0, 3, 5
# 4. Remaining edges: (0, 3), (3, 5)
```

**Note:** This is a challenging problem that requires a good understanding of graph algorithms, data structures, and optimization techniques.  Consider using algorithms like Tarjan's algorithm or Kosaraju's algorithm to find strongly connected components and then implementing a strategy to identify and collapse the HCCs based on the density threshold and maximality criteria. Finding the optimal set of HCCs might require heuristics or approximation algorithms. Your code should be efficient enough to handle graphs within the specified constraints.
