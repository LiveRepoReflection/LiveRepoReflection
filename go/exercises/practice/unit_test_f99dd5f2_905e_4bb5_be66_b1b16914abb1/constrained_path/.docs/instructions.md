Okay, here's a challenging problem designed for a high-level programming competition, focusing on graph manipulation, pathfinding with specific constraints, and efficiency considerations in Go.

### Project Name

```
ConstrainedShortestPath
```

### Question Description

You are tasked with designing a routing algorithm for a specialized delivery network. This network consists of `n` nodes, numbered from `0` to `n-1`, representing delivery locations.  The connections between locations are represented by a directed graph where each edge has a `cost` and a `risk` associated with it.

Your goal is to find the shortest path (minimum total `cost`) from a `start` node to a `destination` node, subject to a maximum allowable total `risk`.

**Input:**

*   `n`: An integer representing the number of nodes in the network.
*   `edges`: A slice of slices of integers, where each inner slice represents a directed edge in the form `[source, destination, cost, risk]`.
    *   `source` and `destination` are node indices (0 to n-1).
    *   `cost` is a non-negative integer representing the cost of traversing the edge.
    *   `risk` is a non-negative integer representing the risk of traversing the edge.
*   `start`: An integer representing the starting node.
*   `destination`: An integer representing the destination node.
*   `maxRisk`: An integer representing the maximum allowable total risk for the path.

**Output:**

*   An integer representing the minimum total cost of a path from `start` to `destination` with a total risk no greater than `maxRisk`. If no such path exists, return `-1`.

**Constraints:**

1.  `1 <= n <= 500`
2.  `0 <= len(edges) <= n * (n - 1)` (dense graph)
3.  `0 <= source, destination < n`
4.  `0 <= cost <= 1000`
5.  `0 <= risk <= 100`
6.  `0 <= start, destination < n`
7.  `0 <= maxRisk <= 5000`
8.  The graph can contain cycles.
9.  There can be multiple edges between two nodes.
10. The solution must have reasonable time complexity (e.g. avoid brute-force approaches, aim for something better than O(n!)).

**Example:**

```
n = 5
edges = [[0, 1, 5, 2], [0, 2, 3, 1], [1, 3, 6, 3], [2, 3, 2, 2], [3, 4, 4, 1], [0, 4, 15, 5]]
start = 0
destination = 4
maxRisk = 8

Output: 11 (Path: 0 -> 2 -> 3 -> 4, Cost: 3 + 2 + 4 = 9, Risk: 1 + 2 + 1 = 4. Path: 0->1->3->4, Cost: 5+6+4=15, Risk: 2+3+1=6. Path: 0->4, Cost:15, Risk:5. Shortest path within maxRisk is 0->2->3->4 with cost 9)

```

**Considerations for Difficulty:**

*   **Graph Representation:** The problem requires efficiently representing a potentially dense directed graph.
*   **Pathfinding with Constraints:**  It's not a simple shortest path problem; the risk constraint adds complexity.  Standard algorithms like Dijkstra or Bellman-Ford need adaptation.
*   **Optimization:**  A naive solution might explore many invalid paths exceeding `maxRisk`.  Efficiently pruning the search space is crucial.
*   **Edge Cases:** The problem might have edge cases with disconnected graphs, start = destination, or no possible path.
*   **Multiple Valid Approaches:** A* search with heuristics, modified Dijkstra, or dynamic programming could be considered, each with different performance characteristics depending on the graph structure.  The best approach must carefully balance cost and risk.
*   **Go Specifics:**  Leveraging Go's features for concurrency (if applicable and beneficial) could be explored for performance improvements.
