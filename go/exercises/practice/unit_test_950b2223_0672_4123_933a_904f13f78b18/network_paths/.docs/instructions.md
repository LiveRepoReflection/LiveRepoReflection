Okay, here's a challenging Go coding problem designed to be at the LeetCode hard level, focusing on algorithmic efficiency, advanced data structures, and practical considerations.

**Project Name:** `NetworkPathOptimization`

**Question Description:**

A large telecommunications company, "GlobalConnect," manages a vast network of interconnected routers.  Each router has a unique identifier (an integer), and connections between routers have associated costs representing latency (also an integer). GlobalConnect needs a system to efficiently determine the lowest latency path between any two routers in their network, subject to some dynamically changing constraints.

Specifically, you are tasked with implementing a `NetworkPathOptimizer` that supports the following operations:

1.  **`NewNetworkPathOptimizer(edges [][]int)`:**  Constructor. Takes a list of edges representing the initial network topology. Each edge is represented as a slice of three integers: `[router1, router2, latency]`.  Assume the router IDs are non-negative.  The graph is undirected (an edge `[A, B, C]` implies an edge `[B, A, C]`). There may be multiple edges between the same pair of routers with different latencies.

2.  **`FindLowestLatencyPath(startRouter, endRouter int) (int, []int)`:** Finds the path with the lowest total latency between `startRouter` and `endRouter`.
    *   Returns the total latency (integer) of the optimal path and an array of router IDs representing that path, in order, including the start and end routers.
    *   If no path exists, return `-1` as the latency and an empty slice (`[]int`) as the path.
    *   The path should be the shortest by latency, not necessarily by hop count.
    *   If multiple paths exist with the same lowest latency, return any one of them.

3.  **`AddEdge(router1, router2, latency int)`:** Adds a new edge to the network. This operation should update the internal data structures to efficiently handle subsequent pathfinding queries.  If an edge already exists between `router1` and `router2`, the *lowest* latency edge between them should be kept.

4.  **`RemoveEdge(router1, router2 int)`:** Removes *all* edges between `router1` and `router2`.  This operation should also update internal data structures.

5.  **`DisableRouter(router int)`**: Disables a router. No paths can traverse a disabled router. Disabling a router should update the internal data structures for efficient pathfinding. If a router is already disabled, calling this method should have no effect.

6.  **`EnableRouter(router int)`**: Enables a disabled router. Enabling a router should update the internal data structures for efficient pathfinding. If a router is already enabled, calling this method should have no effect.

**Constraints:**

*   The number of routers can be very large (up to 10<sup>5</sup>). Router IDs are integers.
*   The number of edges can also be large (up to 10<sup>6</sup>).
*   Latency values are non-negative integers.
*   The `FindLowestLatencyPath` method should be optimized for frequent queries after initial network setup and subsequent edge additions/removals. It should perform significantly better than a naive brute-force search on each call.
*   `AddEdge` and `RemoveEdge` operations should also be reasonably efficient, as network topology can change frequently.
*   You need to consider memory usage. Storing the entire adjacency matrix might not be feasible for large networks.

**Efficiency Requirements:**

*   The `FindLowestLatencyPath` operation should ideally have an average time complexity better than O(V<sup>2</sup>) where V is the number of routers.  Dijkstra's algorithm or A* search with appropriate data structures (e.g., a heap) are likely candidates.
*   `AddEdge` and `RemoveEdge` should be efficient enough to not cause significant performance degradation for subsequent pathfinding.  Aim for complexities better than O(V) on average, if possible, where V is the number of routers.
*   The solution must handle large networks within reasonable time and memory constraints (e.g., under 10 seconds and 2GB of memory for test cases with 10<sup>5</sup> routers and 10<sup>6</sup> edges).

**Judging Criteria:**

*   Correctness: Your solution must correctly find the lowest latency path according to the problem description.
*   Efficiency: Your solution must meet the specified time and memory constraints. Solutions that are too slow or consume excessive memory will be penalized or rejected.
*   Code Quality: Your code should be well-structured, readable, and maintainable. Use appropriate data structures and algorithms.
*   Handling Edge Cases: Your solution should gracefully handle edge cases such as disconnected graphs, non-existent paths, and invalid input.

This problem requires careful consideration of data structures, algorithms, and optimization techniques to achieve the required performance. Good luck!
