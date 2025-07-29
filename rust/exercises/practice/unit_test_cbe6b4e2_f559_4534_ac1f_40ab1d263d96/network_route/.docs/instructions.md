Okay, here's a challenging Rust coding problem designed to be similar to a LeetCode Hard problem.

**Project:** `OptimalNetworkRouting`

**Problem Description:**

You are tasked with designing and implementing an efficient routing algorithm for a large-scale distributed network. The network consists of `N` nodes, numbered from `0` to `N-1`. Each node represents a server and can communicate with other nodes directly through network links.

The network topology is dynamic.  At any given time, new links can be established, and existing links can be removed. Each link has a latency associated with it, representing the time it takes for data to travel between the connected nodes. Latency values are non-negative integers.

Your goal is to implement a system that can efficiently answer routing queries.  A routing query consists of a source node `src` and a destination node `dest`. The system should return the *minimum total latency* required to send data from `src` to `dest`. If there is no path from `src` to `dest`, return `-1`.

The system must also support the following operations:

1.  **`add_link(node1: usize, node2: usize, latency: u32)`**: Adds a new link between `node1` and `node2` with the specified `latency`.  The link is bidirectional. If a link already exists between the nodes, update its latency to the new value.
2.  **`remove_link(node1: usize, node2: usize)`**: Removes the link between `node1` and `node2`. If no link exists, do nothing.
3.  **`get_shortest_path(src: usize, dest: usize) -> i32`**: Returns the minimum total latency to send data from `src` to `dest`. Return `-1` if no path exists.

**Constraints and Edge Cases:**

*   `1 <= N <= 100,000` (Number of nodes)
*   `0 <= node1, node2, src, dest < N`
*   `0 <= latency <= 1,000`
*   The number of `add_link`, `remove_link`, and `get_shortest_path` operations can be up to `100,000`.
*   The graph may not be connected.
*   The graph may contain cycles.
*   Consider potential integer overflow if summing latencies along a path.
*   The system should be optimized for a large number of queries after a relatively small number of network topology changes.

**Efficiency Requirements:**

*   The `get_shortest_path` operation should be as efficient as possible, ideally with an average-case time complexity better than naive implementations (e.g., repeated Dijkstra/Bellman-Ford). Aim for something close to O(log N) on average for query after the initial graph construction.
*   The `add_link` and `remove_link` operations should also be reasonably efficient.

**System Design Aspects:**

*   Consider the choice of data structures used to represent the network topology. The data structure should allow for efficient addition, removal, and querying of links.
*   Think about how to optimize the shortest path calculations for repeated queries on the same network topology.  Caching or precomputation techniques might be useful.
*   Consider the trade-offs between memory usage and query performance.

This problem requires a strong understanding of graph algorithms, data structures, and optimization techniques. It challenges the solver to design a system that is both correct and efficient, particularly when dealing with a large number of nodes and queries. Good luck!
