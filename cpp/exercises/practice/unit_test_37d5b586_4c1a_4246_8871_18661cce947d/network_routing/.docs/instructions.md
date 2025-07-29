## Project Name

```
OptimalNetworkRouting
```

## Question Description

You are tasked with designing an optimal routing algorithm for a large-scale communication network. The network consists of `N` nodes, uniquely numbered from `0` to `N-1`. The connections between nodes are represented by a set of bidirectional edges, where each edge has a specific latency.

Your goal is to implement a function that, given the network topology, a source node `src`, and a destination node `dest`, finds the path with the minimum *worst-case latency*.  The worst-case latency of a path is defined as the maximum latency of any single edge within that path.

**Input:**

*   `N`: An integer representing the number of nodes in the network (1 <= N <= 10<sup>5</sup>).
*   `edges`: A vector of tuples `(u, v, latency)`, where `u` and `v` are the node numbers connected by an edge, and `latency` is the latency of that edge (0 <= u, v < N, 1 <= latency <= 10<sup>9</sup>). Assume there are no duplicate edges.
*   `src`: An integer representing the source node (0 <= src < N).
*   `dest`: An integer representing the destination node (0 <= dest < N).

**Output:**

The minimum possible worst-case latency among all possible paths from `src` to `dest`. If no path exists between `src` and `dest`, return `-1`.

**Constraints and Considerations:**

1.  **Large Input:** The network can be very large (up to 10<sup>5</sup> nodes and edges). Efficient algorithms are crucial.
2.  **Disconnected Graphs:** The network might not be fully connected. Ensure your algorithm handles disconnected components correctly.
3.  **Multiple Paths:** There can be multiple paths between the source and destination. You need to find the path with the *minimum* worst-case latency.
4.  **Edge Case:** The latency can be up to 10<sup>9</sup>, consider integer overflow issue.
5.  **Memory Usage:** Be mindful of memory usage. Avoid creating excessively large data structures.
6.  **Efficiency:** The solution should be efficient in terms of time complexity. Solutions with high time complexity are unlikely to pass all test cases. Aim for a solution better than O(N<sup>2</sup>) time complexity.
7.  **Monotonicity:** The problem has a monotonic property: if a worst-case latency of `x` allows you to reach the destination, then any worst-case latency greater than `x` will also allow you to reach the destination. Leverage this property for optimization.

**Example:**

```
N = 5
edges = [(0, 1, 5), (0, 2, 3), (1, 3, 6), (2, 3, 4), (3, 4, 2)]
src = 0
dest = 4

Output: 4

Explanation:
Possible paths from 0 to 4:
- 0 -> 1 -> 3 -> 4 (worst-case latency: 6)
- 0 -> 2 -> 3 -> 4 (worst-case latency: 4)

The minimum worst-case latency is 4.
```
Good luck designing the optimal routing algorithm!
