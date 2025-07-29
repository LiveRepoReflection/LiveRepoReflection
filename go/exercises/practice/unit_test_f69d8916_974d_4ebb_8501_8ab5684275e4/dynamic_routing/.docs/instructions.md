Okay, here's a challenging coding problem designed for a high-level programming competition, focusing on algorithmic efficiency and leveraging advanced data structures.

### Project Name

```
dynamic-network-routing
```

### Question Description

You are tasked with designing a dynamic network routing system. The network consists of `N` nodes (numbered 1 to `N`) and `M` bidirectional edges. Each edge has a latency associated with it, which can change dynamically. Your system needs to efficiently handle route queries and latency updates.

Initially, you are given the network topology as a list of edges, where each edge is represented by a tuple `(u, v, latency)`, indicating an edge between node `u` and node `v` with initial latency `latency`.

Your system must support the following two operations:

1.  **`Route(start_node, end_node)`:** Find the path with the minimum total latency between `start_node` and `end_node`. Return the total latency of this path. If no path exists, return `-1`.

2.  **`UpdateLatency(u, v, new_latency)`:** Update the latency of the edge between node `u` and node `v` to `new_latency`.  Note that since the graph is undirected, this update applies to both `(u, v)` and `(v, u)`.

**Constraints:**

*   `1 <= N <= 10^4` (Number of nodes)
*   `1 <= M <= 10^5` (Number of edges)
*   `1 <= u, v, start_node, end_node <= N`
*   `1 <= latency, new_latency <= 10^4`
*   The graph can be disconnected.
*   There can be multiple edges between two nodes. When `UpdateLatency` is called, update **all** edges between the two nodes to the new latency.
*   The number of `Route` and `UpdateLatency` operations will be up to `10^4`.
*   The system should be optimized for frequent `UpdateLatency` calls followed by `Route` calls.  A naive shortest-path algorithm recomputing everything from scratch for each `Route` call will likely timeout.

**Efficiency Requirements:**

*   The `Route` operation must be reasonably efficient (e.g., Dijkstra's algorithm or A\* search with appropriate data structures).
*   The `UpdateLatency` operation must be highly efficient, ideally without requiring a complete recalculation of shortest paths for all node pairs. Consider data structures and algorithms that allow for incremental updates to shortest path information.

**Example:**

```python
# Initial network:
edges = [(1, 2, 5), (2, 3, 2), (1, 3, 10)]

# Create the routing system
routing_system = RoutingSystem(edges, N)

# Route from node 1 to node 3 (initial latency: 7)
latency = routing_system.Route(1, 3)  # Returns 7 (path 1 -> 2 -> 3)

# Update latency between node 2 and node 3
routing_system.UpdateLatency(2, 3, 1)

# Route from node 1 to node 3 (updated latency: 6)
latency = routing_system.Route(1, 3)  # Returns 6 (path 1 -> 2 -> 3)

#Update latency between node 1 and node 2
routing_system.UpdateLatency(1, 2, 1)

#Route from node 1 to node 3 (updated latency: 2)
latency = routing_system.Route(1, 3) #Returns 10(path 1->3)
```

**Hint:**  Consider techniques like caching shortest paths, using efficient priority queues for shortest path algorithms, and exploring algorithms that can incrementally update shortest path information after edge weight changes. Explore the use of Adjacency Matrix.

This problem requires a good understanding of graph algorithms, data structures, and optimization techniques. The key challenge lies in balancing the efficiency of the `Route` and `UpdateLatency` operations, especially given the constraint on the number of operations. Good luck!
