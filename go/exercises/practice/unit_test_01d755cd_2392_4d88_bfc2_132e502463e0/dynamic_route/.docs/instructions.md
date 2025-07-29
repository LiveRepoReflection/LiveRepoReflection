## Question: Optimal Multi-Hop Route Planning in a Dynamic Network

**Problem Description:**

You are tasked with designing an optimal route planning system for data packets in a dynamic network. The network consists of `N` nodes, numbered from `0` to `N-1`. The connectivity between nodes changes over time. You are given a series of network snapshots. Each snapshot represents the active connections between nodes at a specific timestamp.

Specifically, you are given:

*   `N`: The number of nodes in the network (1 <= N <= 1000).
*   `T`: The number of network snapshots (1 <= T <= 100).
*   `snapshots`: A 2D array of `T` snapshots. Each snapshot `snapshots[i]` is a list of edges, represented as tuples `(u, v, w)`, where `u` and `v` are the node indices (0-indexed) connected by the edge at timestamp `i`, and `w` is the latency of that edge (1 <= w <= 1000). The graph is undirected, meaning an edge `(u, v, w)` implies there is also an edge `(v, u, w)`.
*   `queries`: A list of queries. Each query is a tuple `(start_node, end_node, start_time, end_time)`.  `start_node` and `end_node` are the source and destination node indices, respectively. `start_time` and `end_time` represent the inclusive time window within which the route must be planned (0 <= start_time <= end_time < T).

The goal is to find the path with the *minimum total latency* from `start_node` to `end_node` for each query, considering the dynamic network connectivity within the specified time window. You can only traverse an edge that exists at the timestamp when you are at the starting node of the edge.

**Constraints:**

*   You can only move to a neighboring node at each timestamp. You cannot stay at the same node for multiple timestamps.
*   The latency of a path is the sum of the latencies of the edges used in the path.
*   If no path exists between `start_node` and `end_node` within the given time window, return -1.
*   The number of edges in each snapshot can vary. It is guaranteed that there are no duplicate edges within a single snapshot.
*   The graph represented by each snapshot may not be fully connected.
*   The time taken to traverse an edge is assumed to be instantaneous. You "arrive" at the destination node of an edge at the same timestamp you "left" the origin node.
*   You must arrive at the `end_node` at or before `end_time`.
*   If multiple paths with the same minimum latency exist, any of those paths will be considered correct.

**Efficiency Requirements:**

The solution must be efficient enough to handle large networks and a significant number of queries within a reasonable time limit. Consider algorithmic complexity when designing your solution. Solutions that result in TLE (Time Limit Exceeded) will not be accepted.

**Example:**

Let's say:

```
N = 4
T = 3
snapshots = [
    [(0, 1, 2), (1, 2, 3)],  // Timestamp 0
    [(0, 2, 1), (2, 3, 4)],  // Timestamp 1
    [(0, 3, 5)]              // Timestamp 2
]
queries = [(0, 3, 0, 2)]
```

For the query `(0, 3, 0, 2)`, a possible optimal path is:

1.  At timestamp 0, take edge `(0, 1, 2)` to node 1.
2.  At timestamp 1, no edges directly connect from node 1 to node 3.
3.  At timestamp 2, no edges directly connect from node 1 to node 3.

Another possible optimal path is:

1. At timestamp 0, there is no direct path from node 0 to node 3.
2. At timestamp 1, take edge (0,2,1) to node 2.
3. At timestamp 2, there is no direct edge from node 2 to node 3

Let's consider another route:

1. At timestamp 0, there is no direct path from node 0 to node 3.
2. At timestamp 1, take edge (0,2,1) to node 2.
3. At timestamp 2, take edge (2,3,x) to node 3. However, this edge (2,3,x) does not exists.

However, at timestamp 2, take edge (0,3,5) to node 3.

Therefore, the optimal path from node 0 to node 3 is 5, which is starting at node 0, and traverse the edge (0,3,5) at timestamp 2, and end at node 3.

**Clarification:**

The "optimal path" refers to the path with the minimum total latency. You must consider all possible paths within the specified time window and return the latency of the best path. If no path exists, return -1. The path doesn't have to use all the time within the time window.
