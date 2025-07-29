Okay, here's a challenging Go coding problem designed with the elements you requested:

## Project Name

`go-network-routing`

## Question Description

You are tasked with designing a highly scalable and efficient network routing system.  Imagine you're building the core of a large Content Delivery Network (CDN) or a distributed database system. The network consists of interconnected nodes, each with a unique ID.  Nodes can directly communicate with their immediate neighbors.

Your system must handle the following:

1.  **Node Discovery:**  Given a set of nodes and their connections, construct a routing table for each node.  The routing table should allow a node to determine the shortest path (minimum number of hops) to any other node in the network.

2.  **Dynamic Network Changes:** The network topology can change dynamically.  Nodes can be added, removed, or connections between nodes can be established or broken. Your system must efficiently update the routing tables to reflect these changes.  Minimize the amount of recomputation needed after each change.

3.  **Latency Optimization:**  Each connection between nodes has a latency associated with it (expressed as an integer). When multiple shortest paths exist (in terms of hop count), the system should prefer the path with the lowest total latency.

4.  **Fault Tolerance:**  The system must be resilient to node failures. If a node becomes unavailable, the routing tables should be updated to route traffic around the failed node.

5.  **Scalability:** The system should be able to handle a large number of nodes and connections.  Consider the memory footprint and algorithmic complexity of your solution.

**Input:**

*   **Initial Network Configuration:**  A list of nodes and their connections.  Each connection is represented by a tuple: `(node1_id, node2_id, latency)`.
*   **Dynamic Changes:**  A sequence of operations that modify the network topology.  These operations can be:
    *   `AddNode(node_id)`: Adds a new node to the network.
    *   `RemoveNode(node_id)`: Removes a node from the network.
    *   `AddConnection(node1_id, node2_id, latency)`: Adds a connection between two nodes.
    *   `RemoveConnection(node1_id, node2_id)`: Removes the connection between two nodes.

**Output:**

*   A function/method that returns the shortest path (node IDs in order) and total latency between any two given nodes after each network change. If no path exists, return an empty path and a large integer value (e.g., `math.MaxInt32`) for the latency.

**Constraints:**

*   Node IDs are unique integers.
*   Latency values are non-negative integers.
*   The network is undirected (if A is connected to B, then B is connected to A with the same latency).
*   The system should be optimized for frequent network changes and path queries.  Pre-computation is allowed, but should be balanced against the cost of recomputation after changes.
*   Consider using appropriate data structures to achieve optimal performance (e.g., adjacency lists/matrices, priority queues, etc.).
*   Write clear and concise code, with comments explaining your design choices.

**Bonus Challenges:**

*   Implement a visualization tool to display the network topology and routing paths.
*   Add support for weighted nodes (nodes with different processing capabilities or priorities).
*   Implement a mechanism for detecting and handling network congestion.

**Judging Criteria:**

*   Correctness of the routing paths.
*   Efficiency of the pathfinding algorithm (especially for large networks).
*   Performance of the system under dynamic network changes.
*   Code clarity and maintainability.
*   Handling of edge cases and error conditions.
*   Scalability of the solution.
