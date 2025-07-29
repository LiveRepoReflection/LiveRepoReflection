Okay, here's a challenging C++ coding problem designed to test a wide range of skills.

**Problem Title:** Network Capacity Optimization

**Problem Description:**

You are tasked with designing a resilient and efficient communication network for a large-scale distributed system. The system consists of `N` nodes, each representing a server in a data center. These nodes are interconnected via a network of bidirectional communication channels.

Each communication channel between two nodes has a certain capacity, representing the maximum amount of data that can be transmitted between those nodes per unit of time. The network is represented as an undirected graph, where nodes are vertices and communication channels are edges.

Unfortunately, some of the communication channels are unreliable and prone to failure. You are given a set of `M` channels that have a non-zero probability of failing at any given time. Each of these channels has an associated failure probability `p_i` (0 < `p_i` < 1).

Your goal is to design an algorithm that determines the maximum guaranteed bandwidth between two specific nodes, a source node `S` and a destination node `D`, even in the face of potential channel failures. The guaranteed bandwidth is defined as the minimum bandwidth that can be sustained between `S` and `D` across all possible combinations of channel failures, multiplied by the probability of that channel state.

**Input:**

*   `N`: The number of nodes in the network (1 <= `N` <= 1000). Nodes are numbered from 0 to `N-1`.
*   `M`: The number of unreliable channels (0 <= `M` <= `N*(N-1)/2`).
*   `edges`: A vector of tuples `(u, v, capacity, failure_probability)`.
    *   `u` and `v` are the node indices (0 <= `u`, `v` < `N`, `u` != `v`) representing the endpoints of the channel.
    *   `capacity` is the maximum bandwidth of the channel (1 <= `capacity` <= 1000).  If `failure_probability` is 0, the channel is reliable.
    *   `failure_probability` is the probability that the channel fails (0 < `failure_probability` < 1) and is 0 if the channel is reliable.  Reliable channels are not included in `M`.
*   `S`: The index of the source node (0 <= `S` < `N`).
*   `D`: The index of the destination node (0 <= `D` < `N`, `S` != `D`).

**Output:**

*   A double representing the maximum guaranteed bandwidth between `S` and `D`.

**Constraints and Considerations:**

*   The graph may not be fully connected.
*   Multiple edges between the same pair of nodes are not allowed.
*   The network should be treated as undirected, meaning data can flow in both directions through a channel.
*   The failure of channels are independent events.
*   The solution should be computationally efficient, as the number of possible channel failure combinations can be exponential in `M`.  Naive brute-force solutions will likely time out.
*   Due to the nature of floating point arithmetic, your solution should be accurate to at least 6 decimal places.
*   Consider the case where the max flow is 0, and there are no paths between S and D when all nodes are working.

**Example:**

```
N = 4
M = 2
edges = {
  (0, 1, 10, 0.1),
  (1, 2, 5, 0.2),
  (0, 3, 7, 0.0),
  (3, 2, 8, 0.0),
  (1,3, 20, 0.0)
}
S = 0
D = 2

Output: (Calculated Guaranteed Bandwidth)
```

**Clarifications:**

* What should happen if there are no paths from the source to the destination? Return 0.0.
* Can I assume that S != D? Yes.
* Can the graph be disconnected? Yes.
* How are edge capacities handled if an edge fails? Capacity becomes 0.
* Is it possible for the graph to have cycles? Yes.

This problem requires a good understanding of graph algorithms, probability, and optimization techniques.  Good luck!
