## Question: Efficient Network Routing with Congestion Awareness

**Project Name:** `congestion-aware-routing`

**Question Description:**

You are tasked with designing an efficient and congestion-aware routing algorithm for a large-scale network. The network consists of `n` nodes (numbered from 0 to n-1) and `m` directed edges. Each edge has a capacity representing the maximum data flow it can handle.  The network's topology and edge capacities are provided as input.

The network is susceptible to congestion.  To model this, each edge also has a congestion factor, which dynamically changes based on the current load on that edge. Specifically, the *effective capacity* of an edge is its original capacity divided by the *congestion factor*. Higher congestion factors mean lower effective capacity.  The congestion factor for each edge is calculated as `1 + (current_flow / capacity)^2`.

Given a source node `s`, a destination node `t`, and a set of `k` data packets, your goal is to route these packets from `s` to `t` in a way that minimizes the *maximum congestion factor* across all edges used in the routing.  You cannot split packets – each packet must follow a single path. You must route all `k` packets.

**Input:**

*   `n`: The number of nodes in the network (1 <= `n` <= 1000).
*   `m`: The number of directed edges in the network (1 <= `m` <= 5000).
*   `edges`: A list of `m` tuples, where each tuple `(u, v, capacity)` represents a directed edge from node `u` to node `v` with the given `capacity` (1 <= `u`, `v` < `n`, 1 <= `capacity` <= 100).  There can be multiple edges between two nodes.
*   `s`: The source node (0 <= `s` < `n`).
*   `t`: The destination node (0 <= `t` < `n`).
*   `k`: The number of data packets to route from `s` to `t` (1 <= `k` <= 100).

**Output:**

A list of `k` paths, where each path is a list of node indices representing the route a packet takes from `s` to `t`. If it's impossible to route all `k` packets from `s` to `t`, return an empty list.

**Constraints and Requirements:**

1.  **Minimization Objective:** The primary objective is to minimize the maximum congestion factor among all edges used in the solution. This means finding a routing that distributes the load as evenly as possible across the network.

2.  **No Packet Splitting:** Each packet must be routed along a single, continuous path from `s` to `t`.

3.  **Capacity Constraints:** The flow on any edge at any time cannot exceed its effective capacity.

4.  **All Packets Must Be Routed:** You must find a valid path for all `k` packets. If a solution exists where all `k` packets can be routed, you must find it. If no such solution exists, return an empty list.

5.  **Efficiency:** Your solution must be reasonably efficient.  A brute-force approach that explores all possible path combinations is unlikely to pass all test cases. Consider using efficient algorithms for pathfinding and optimization.

6.  **Edge Cases:** Consider cases where there are no paths between `s` and `t`, or where the network is highly congested, making it difficult to find valid routes.

7.  **Dynamic Congestion:** The congestion factor changes with the current flow. This means that finding the initial paths changes the available routes that can be taken later.

8.  **Multiple Valid Solutions:** If multiple solutions exist that minimize the maximum congestion factor, any of these solutions is acceptable.

**Example:**

```
n = 4
m = 5
edges = [(0, 1, 10), (0, 2, 5), (1, 3, 5), (2, 3, 10), (0,3,2)]
s = 0
t = 3
k = 3

Possible Output (one of many possible valid solutions):

[[0, 1, 3], [0, 2, 3], [0, 2, 3]]  // Two packets take path 0->2->3 and one packet takes path 0->1->3
```

**Reasoning for Difficulty:**

This problem is difficult because:

*   It combines graph traversal (finding paths) with optimization (minimizing the maximum congestion factor).
*   The congestion model introduces a dynamic element, making it harder to find optimal paths.
*   The "all packets must be routed" constraint adds complexity, as you need to ensure that a solution exists before attempting to find the optimal one.
*   The scale of the network (up to 1000 nodes and 5000 edges) requires an efficient algorithm. A naive brute-force approach won't work.
*   The non-splitting packet constraint eliminates several simpler solutions involving flow networks.
