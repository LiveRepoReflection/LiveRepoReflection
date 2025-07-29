## Project Name

```
k-clique-enumeration
```

## Question Description

You are given a large undirected graph represented as an adjacency list. Your task is to enumerate all cliques of size *k* in this graph. A clique is a subset of vertices in the graph such that every two distinct vertices in the clique are adjacent.

**Input:**

*   `n`: The number of vertices in the graph, labeled from 0 to n-1. (1 <= n <= 1000)
*   `k`: The size of the cliques to find. (1 <= k <= 6)
*   `adjList`: A map representing the adjacency list of the graph. The keys are vertex IDs (0 to n-1), and the values are slices of vertex IDs representing the neighbors of that vertex. The adjacency list is guaranteed to be symmetric (if `u` is a neighbor of `v`, then `v` is a neighbor of `u`).

**Output:**

*   A slice of slices, where each inner slice represents a clique of size *k*. Each inner slice should contain the vertex IDs of the clique, sorted in ascending order. The outer slice should contain all such cliques, with no duplicates and sorted lexicographically (i.e., sort by the first element, then the second, and so on).

**Constraints:**

*   The graph may be sparse or dense.
*   The input graph is guaranteed to be valid (no self-loops, symmetric adjacency list).
*   The order of neighbors in the input adjacency list is not guaranteed.
*   Your solution must be efficient enough to handle graphs with up to 1000 vertices within a reasonable time limit (e.g., a few seconds).  Brute-force solutions that check all possible subsets will likely time out for larger graphs.
*   Consider memory usage as well. Storing all possible subsets of vertices can quickly exhaust memory for larger graphs.

**Example:**

```
n = 5
k = 3
adjList = map[int][]int{
    0: {1, 2, 3},
    1: {0, 2, 3},
    2: {0, 1, 3},
    3: {0, 1, 2, 4},
    4: {3},
}

Expected Output:
[[0, 1, 2], [0, 1, 3], [0, 2, 3], [1, 2, 3]]
```

**Hints:**

*   Consider using backtracking or recursion to explore possible cliques.
*   Optimize your search by pruning branches that cannot lead to valid cliques.
*   Think about how to efficiently check if a set of vertices forms a clique.
*   Use sets to deduplicate cliques and sort the results appropriately.
*   The provided constraints suggest an optimized backtracking or branch-and-bound approach is necessary.
