## Project Name

`Autonomous Network Routing`

## Question Description

You are tasked with designing an autonomous routing system for a dynamic network. The network consists of nodes that can represent servers, routers, or other network devices. The connections between these nodes can appear, disappear, or change their bandwidth dynamically. Your goal is to implement an algorithm that allows each node to independently learn and maintain optimal routing tables for sending data packets to any other node in the network, minimizing latency and maximizing throughput.

**Network Representation:**

The network is represented as a directed graph. Each node in the network is identified by a unique integer ID. The connections (edges) between nodes are characterized by the following properties:

*   **Source Node:** The ID of the node where the connection originates.
*   **Destination Node:** The ID of the node where the connection terminates.
*   **Latency:** A numerical value representing the time (in milliseconds) it takes for a packet to travel from the source to the destination node. This value can change over time.
*   **Bandwidth:** A numerical value representing the maximum data transfer rate (in Mbps) allowed on this connection. This value can also change over time.

**Routing Table Requirements:**

Each node must maintain a routing table. This table should contain the following information for every possible destination node in the network:

*   **Destination Node:** The ID of the target node.
*   **Next Hop:** The ID of the next node to forward the packet to in order to reach the destination.
*   **Estimated Latency:** The estimated total latency to reach the destination node through the chosen path.
*   **Available Bandwidth:** The minimum bandwidth available along the chosen path to the destination node.
*   **Path:** List of nodes along the path to destination.

**Algorithm Requirements:**

Implement a distributed algorithm that satisfies the following constraints:

1.  **Decentralized Learning:** Each node must independently learn its routing table based on local information and communication with its immediate neighbors. No central controller is allowed.
2.  **Adaptive Routing:** The algorithm must dynamically adapt to changes in network topology (node failures, new connections) and link characteristics (latency, bandwidth).
3.  **Optimal Path Selection:** The algorithm should prioritize paths with the lowest latency and highest bandwidth, balancing these two factors appropriately. You need to implement a cost function that take these two factors into consideration.
4.  **Scalability:** The algorithm must be able to handle a large number of nodes (up to 10,000) and connections efficiently.
5.  **Convergence:** The routing tables should converge to a stable state within a reasonable amount of time.

**Constraints and Edge Cases:**

*   **Network Dynamics:** The network topology and link characteristics can change frequently and unpredictably.
*   **Node Failures:** Nodes can fail without prior notice.
*   **Link Failures:** Connections between nodes can fail without prior notice.
*   **Loop Prevention:** The algorithm must prevent routing loops, where packets circulate endlessly between nodes.
*   **Dead Ends:** The algorithm must handle cases where a destination node is unreachable.
*   **Memory Constraints:** Each node has limited memory to store its routing table.
*   **Processing Power Constraints:** Each node has limited processing power to perform routing calculations.
*   **Communication Overhead:** Minimize the amount of communication required between nodes to maintain routing tables.
*   **Tie-Breaking:** Provide a deterministic method for breaking ties between multiple equally optimal paths.

**Specific Tasks:**

1.  Implement the core routing algorithm.
2.  Implement appropriate data structures to represent the network topology and routing tables.
3.  Implement mechanisms for nodes to exchange routing information with their neighbors.
4.  Implement a mechanism for detecting node and link failures.
5.  Design a cost function that balances latency and bandwidth in path selection.
6.  Implement a loop prevention mechanism.
7.  Implement a mechanism to prevent routing table oscillations (flapping).
8.  Implement a deterministic tie-breaking strategy.
9.  Handle edge cases such as unreachable destinations, memory limitations, and processing power constraints.

**Evaluation Criteria:**

The solution will be evaluated based on the following criteria:

*   **Correctness:** The routing tables must accurately reflect the optimal paths in the network.
*   **Efficiency:** The algorithm must converge quickly and minimize communication overhead.
*   **Robustness:** The algorithm must be able to handle network dynamics, node failures, and link failures gracefully.
*   **Scalability:** The algorithm must be able to handle a large number of nodes and connections.
*   **Optimality:** The algorithm must select paths that minimize latency and maximize bandwidth.
*   **Clarity:** The code must be well-structured, well-documented, and easy to understand.

This problem requires a deep understanding of networking concepts, distributed algorithms, and data structures. It challenges the solver to design a robust and efficient routing system that can adapt to the complexities of a dynamic network environment. Good luck!
