## Project Name

```
NetworkRouting
```

## Question Description

You are tasked with designing a highly efficient and scalable routing system for a large-scale data center network. The network consists of `n` servers and `m` bidirectional links between them. Each link has a latency associated with it, representing the time it takes for data to travel across the link.

Due to the dynamic nature of the data center, servers frequently request data from each other. Your goal is to implement a routing algorithm that can quickly find the optimal path (i.e., the path with the lowest total latency) between any two servers in the network, subject to the following constraints:

*   **Real-time Updates:** The network topology and link latencies can change dynamically. Your routing system must be able to efficiently update its routing information in response to these changes. Updates can include adding or removing links, or modifying the latency of existing links.

*   **Scalability:** The data center network is very large. Your algorithm should scale efficiently to handle a large number of servers and links.

*   **Fault Tolerance:** The network must be resilient to link failures. If a link fails, the routing system should automatically re-route traffic along alternative paths.

*   **Congestion Awareness (Optional, but highly encouraged):** While latency is the primary optimization goal, you are encouraged to consider network congestion. Some links may be experiencing high traffic volume, which can increase latency. Your routing algorithm should ideally take congestion into account and route traffic away from congested links.

**Input:**

1.  **Initial Network Topology:** A list of `m` bidirectional links, where each link is represented by a tuple `(server1, server2, latency)`. Server IDs are integers from `0` to `n-1`.

2.  **Routing Requests:** A stream of routing requests, where each request is represented by a tuple `(source_server, destination_server)`.

3.  **Network Updates:** A stream of network updates, where each update can be one of the following types:

    *   `add_link(server1, server2, latency)`: Adds a new bidirectional link between `server1` and `server2` with the given `latency`.
    *   `remove_link(server1, server2)`: Removes the bidirectional link between `server1` and `server2`.
    *   `update_latency(server1, server2, new_latency)`: Updates the latency of the existing bidirectional link between `server1` and `server2` to `new_latency`.

**Output:**

For each routing request, your algorithm should return the optimal path (a list of server IDs representing the path) and its total latency. If no path exists between the source and destination, return `null` for the path and `Infinity` for the latency.

**Constraints:**

*   `1 <= n <= 100,000` (Number of servers)
*   `1 <= m <= 500,000` (Number of links)
*   `1 <= latency <= 1000` (Link latency)
*   The number of routing requests and network updates can be very large (up to 1,000,000).
*   Updates must be processed and reflected in the routing system in a timely manner.
*   Your algorithm should be as efficient as possible in terms of both time and space complexity.

**Bonus Challenges:**

*   Implement a mechanism to detect and handle network partitions (i.e., when the network becomes disconnected).
*   Implement a more sophisticated congestion-aware routing algorithm that takes into account real-time traffic conditions.
*   Design a distributed routing system that can handle even larger networks and higher traffic volumes.

This problem requires a good understanding of graph algorithms, data structures, and system design principles.  Consider the trade-offs between different routing algorithms (e.g., Dijkstra's algorithm, A\* search) and data structures (e.g., adjacency lists, adjacency matrices) in terms of performance, scalability, and memory usage. Good luck!
