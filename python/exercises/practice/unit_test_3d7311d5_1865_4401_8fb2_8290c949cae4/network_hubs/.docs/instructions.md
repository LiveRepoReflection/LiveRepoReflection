## Project Name:

`OptimalNetworkPlacement`

## Question Description:

You are tasked with designing a robust and efficient communication network across a sprawling city. The city can be represented as a graph where intersections are nodes and roads connecting intersections are edges. Each road has an associated latency (delay) value. Your goal is to strategically place a limited number of network hubs within the city to minimize the maximum latency experienced by any intersection when communicating with its nearest hub.

**Specifically:**

*   **Input:** You are given a graph represented as an adjacency list: `graph = {node: [(neighbor, latency), ...]}`. Nodes are represented by integers from 0 to N-1, where N is the number of intersections in the city. Latency is a positive integer.
*   You are also given an integer `num_hubs`, representing the maximum number of network hubs you can place.
*   **Placement Constraints:** Hubs can only be placed at existing intersections (nodes in the graph).
*   **Latency Calculation:** For each intersection (node), the latency to its nearest hub is the shortest path distance (sum of latencies along the edges) to the closest hub. If an intersection has no path to any hub, its latency is considered infinite.
*   **Objective:** Minimize the *maximum* latency experienced by any intersection to its nearest hub. This is often called the "min-max" problem.

**Your task is to write a function `min_max_latency(graph, num_hubs)` that returns the minimum possible value of the maximum latency among all intersections, given the graph and the number of hubs. If it is impossible to place the specified number of hubs such that all nodes are reachable, return -1.**

**Constraints:**

*   1 <= N (number of intersections) <= 500
*   1 <= M (number of roads) <= N * (N - 1) / 2
*   1 <= latency <= 100
*   1 <= `num_hubs` <= N
*   The graph is undirected (if (a, b, latency) exists, then (b, a, latency) also exists with the same latency).
*   The graph may not be fully connected.
*   You need to return the result within a reasonable time limit. Brute-force approaches will likely time out.

**Example:**

```python
graph = {
    0: [(1, 10), (2, 15)],
    1: [(0, 10), (3, 20)],
    2: [(0, 15), (4, 25)],
    3: [(1, 20), (5, 30)],
    4: [(2, 25), (5, 35)],
    5: [(3, 30), (4, 35)]
}
num_hubs = 2

result = min_max_latency(graph, num_hubs)
# Expected Output: 30 (Placing hubs at nodes 0 and 5 gives a max latency of 30)
```

**Considerations:**

*   Think about efficient algorithms for finding shortest paths (e.g., Dijkstra's algorithm or Floyd-Warshall).
*   Consider using Binary Search to efficiently find the optimal maximum latency.
*   You will need to carefully handle disconnected graphs.
*   The solution should be optimized for time complexity.

This problem requires a combination of graph algorithms, optimization techniques, and careful handling of edge cases. A well-structured, efficient solution is essential to pass the time constraints.
