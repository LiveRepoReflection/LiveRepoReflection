Okay, here's a challenging Go coding problem designed to be LeetCode Hard level, incorporating elements of advanced data structures, edge cases, optimization, and real-world considerations.

### Project Name

```
NetworkTopology
```

### Question Description

You are tasked with designing and implementing a system for analyzing and optimizing network topology in a large-scale distributed system. The system consists of `n` nodes, uniquely identified by integer IDs from `0` to `n-1`. The network topology is represented by a set of directed edges, where each edge represents a communication channel between two nodes.

The goal is to implement several key functionalities:

1.  **Network Representation:** Efficiently store and manage the network topology. The network is dynamic; edges can be added or removed.

2.  **Connectivity Analysis:** Determine if a path exists between any two given nodes. Consider that the network can be disconnected. The path finding should be performant.

3.  **Critical Edge Identification:** Identify "critical edges" in the network. A critical edge is defined as an edge whose removal would disconnect at least two nodes that were previously connected (meaning a path existed between them before the removal of the edge).

4.  **Latency Estimation:** Each edge has an associated latency value (a non-negative integer). Implement a function to estimate the minimum latency between any two given nodes. This should consider all possible paths and find the path with the lowest total latency. If no path exists, return -1.

5.  **Topology Optimization (Optional, but highly encouraged):** Given a limit on the number of edges that can be added, suggest a set of new edges to add to the network that would minimize the average latency between all pairs of nodes. This is a bonus challenge with significant complexity.

## Requirements

1.  **Efficiency:** The system must handle a large number of nodes (up to 10<sup>5</sup>) and edges (up to 5 * 10<sup>5</sup>). Operations such as adding/removing edges, connectivity checks, and latency estimation must be optimized for performance.

2.  **Scalability:** The data structures and algorithms used should be scalable to accommodate future growth of the network.

3.  **Edge Cases:** Handle edge cases such as:
    *   Disconnected graphs
    *   Cycles in the graph
    *   Self-loops (edges from a node to itself)
    *   Parallel edges (multiple edges between the same two nodes) - should consider the edge with the smallest latency if parallel edges exist.
    *   Non-existent nodes (attempting to add an edge with an invalid node ID)

4.  **Memory Usage:** Minimize memory footprint where possible.

5.  **Real-World Considerations:** Consider that network latency can change over time. While you don't need to implement real-time updates, think about how your design could accommodate dynamic latency values.

6.  **Modularity:** Your code should be well-structured and modular, making it easy to add new features or modify existing ones.

7.  **Concurrency (Bonus):**  If possible, consider how you can leverage concurrency to speed up operations such as connectivity analysis and latency estimation, especially when dealing with a large number of nodes.

Good luck! This problem requires a strong understanding of graph algorithms, data structures, and optimization techniques.
