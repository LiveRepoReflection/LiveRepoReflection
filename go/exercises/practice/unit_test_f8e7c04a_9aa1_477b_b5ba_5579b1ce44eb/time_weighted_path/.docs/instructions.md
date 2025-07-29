## Question: Optimal Path in a Weighted Multi-Graph with Time Constraints

**Problem Description:**

You are given a weighted, directed multi-graph representing a transportation network. A multi-graph allows multiple edges between the same pair of vertices. Each edge represents a possible route with a specific travel time (weight).

The graph is represented as follows:

*   `n`: The number of vertices (numbered 0 to n-1).
*   `edges`: A list of tuples, where each tuple `(u, v, w)` represents a directed edge from vertex `u` to vertex `v` with weight `w` (travel time).  Note there can be duplicate tuples in the list.

You are also given:

*   `start`: The starting vertex.
*   `end`: The destination vertex.
*   `k`: The maximum number of edges you can traverse.
*   `max_time`: The maximum allowable travel time.

Your task is to find the *minimum* travel time to reach the `end` vertex from the `start` vertex, traversing at most `k` edges, while ensuring the total travel time does not exceed `max_time`. If no such path exists, return -1.

**Constraints:**

1.  `1 <= n <= 100` (number of vertices)
2.  `0 <= len(edges) <= 1000`
3.  `0 <= u, v < n` for each edge `(u, v, w)`
4.  `1 <= w <= 100` for each edge `(u, v, w)`
5.  `0 <= start, end < n`
6.  `1 <= k <= 50` (maximum number of edges)
7.  `1 <= max_time <= 5000` (maximum travel time)

**Efficiency Requirements:**

The solution should be efficient enough to handle the maximum input sizes within a reasonable time limit (e.g., a few seconds). Naive approaches (e.g., brute-force search) are likely to time out. Consider using dynamic programming or other optimization techniques. It is important to avoid unnecessary computations.

**Edge Cases:**

1.  `start` and `end` vertices are the same.
2.  No path exists between `start` and `end`.
3.  `k` is smaller than the minimum number of edges required to reach the destination.
4.  All paths between `start` and `end` exceed `max_time`.
5.  The graph contains cycles. You need to handle cycles efficiently to avoid infinite loops.
6.  Duplicate Edges with different weights.

**Input Format:**

```
n: int
edges: [][]int
start: int
end: int
k: int
max_time: int
```

where `edges` is a 2D array (slice of slices) where each inner slice contains `u`, `v`, and `w`.

**Output Format:**

```
min_time: int
```

Return the minimum travel time, or -1 if no valid path exists.
