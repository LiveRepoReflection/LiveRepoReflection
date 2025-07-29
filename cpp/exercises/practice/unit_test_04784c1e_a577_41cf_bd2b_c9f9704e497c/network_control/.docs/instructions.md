## Project Name

```
network_congestion
```

## Question Description

You are tasked with designing a congestion control mechanism for a large-scale distributed system. The system consists of `N` nodes (numbered from 0 to N-1) connected by a network. Data packets are routed between these nodes. Due to varying network conditions and traffic patterns, congestion can occur, leading to packet loss and increased latency.

Your goal is to implement a rate-limiting algorithm on each node to mitigate congestion and ensure fair bandwidth allocation among different flows. The rate limiter must dynamically adjust the sending rate of packets based on feedback signals from the network.

Specifically, you need to implement the following functionalities:

1.  **Network Representation:** The network topology is represented by a weighted, directed graph. The weight of each edge (u, v) represents the capacity of the link between node `u` and node `v` in packets per second. Assume the graph is provided as an adjacency list where each node `u` stores a list of pairs `(v, capacity)`, indicating a directed edge from `u` to `v` with the specified capacity.

2.  **Packet Sending:** Each node `u` can send packets to any other node `v`. The sending rate of node `u` to node `v` is denoted as `rate(u, v)`. Initially, all `rate(u, v)` values are set to a small initial value (e.g., 1 packet/second).

3.  **Congestion Detection:** A central monitoring system periodically measures the utilization of each link in the network. The utilization of a link (u, v) is defined as the ratio of the actual traffic flowing through the link to its capacity. The monitoring system provides feedback signals to each node in the form of a congestion factor `c(u, v)` for each outgoing link (u, v). This congestion factor is a real number between 0 and 1, where 0 indicates no congestion and 1 indicates full congestion. A value greater than 1 is possible and indicates severe congestion where the traffic exceeds the capacity.

4.  **Rate Adjustment Algorithm:** Implement a distributed rate adjustment algorithm that dynamically adjusts the sending rate of each node based on the congestion feedback. Each node `u` should independently update its sending rate `rate(u, v)` for each outgoing link (u, v) according to the following rules:

    *   **Additive Increase:** If `c(u, v) < threshold1` (e.g., 0.7), increase `rate(u, v)` by a small additive increment `alpha` (e.g., 0.1 packets/second).
    *   **Multiplicative Decrease:** If `c(u, v) > threshold2` (e.g., 0.9), decrease `rate(u, v)` by a multiplicative factor `beta` (e.g., 0.5).
    *   **No Change:** If `threshold1 <= c(u, v) <= threshold2`, maintain the current `rate(u, v)`.

5.  **Constraints and Edge Cases:**

    *   The sending rate `rate(u, v)` must always be non-negative. If the multiplicative decrease results in a negative rate, set it to 0.
    *   The sending rate `rate(u, v)` should not exceed a maximum allowed rate `max_rate` (e.g., 1000 packets/second).
    *   Handle the case where a link (u, v) does not exist in the network topology.  In this case, `c(u, v)` will not be provided, and `rate(u, v)` should remain at 0.
    *   The algorithm must be efficient to handle a large number of nodes and links.

6.  **System Design Considerations:**

    *   Assume that each node has limited knowledge about the overall network topology and relies primarily on the congestion feedback signals for its outgoing links.
    *   The rate adjustment algorithm should be distributed, meaning each node can make decisions independently without requiring global coordination.
    *   Consider the trade-offs between responsiveness to congestion and stability of the network. A too-aggressive rate adjustment algorithm can lead to oscillations and instability.

## Requirements

Implement a `NetworkNode` class with the following methods:

*   `NetworkNode(int node_id, int num_nodes, std::vector<std::pair<int, int>> outgoing_links)`: Constructor that initializes the node with its ID, the total number of nodes in the network, and a list of its outgoing links and their capacities.
*   `void update_rates(std::unordered_map<int, double> congestion_factors)`: Updates the sending rates based on the provided congestion factors for the outgoing links. The `congestion_factors` map contains entries of the form `{destination_node_id: congestion_factor}`. Only destination nodes present in the node's outgoing links will have a congestion factor.
*   `double get_rate(int destination_node_id)`: Returns the current sending rate for packets destined to the specified node. If there is no direct link to the destination node, return 0.

**Note:** You are free to add any helper methods or data structures to the `NetworkNode` class as needed.

**Example:**

Assume a network with 3 nodes (0, 1, 2). Node 0 has two outgoing links: (0, 1) with capacity 100 and (0, 2) with capacity 200.

```cpp
NetworkNode node0(0, 3, {{1, 100}, {2, 200}});

// Initial rates: rate(0, 1) = 1, rate(0, 2) = 1

// Congestion feedback: c(0, 1) = 0.5, c(0, 2) = 0.95
std::unordered_map<int, double> congestion_factors = {{1, 0.5}, {2, 0.95}};
node0.update_rates(congestion_factors);

// After update: rate(0, 1) = 1.1, rate(0, 2) = 0.5 (approx.)

double rate_to_1 = node0.get_rate(1); // rate_to_1 == 1.1 (approx.)
double rate_to_2 = node0.get_rate(2); // rate_to_2 == 0.5 (approx.)
double rate_to_0 = node0.get_rate(0); // rate_to_0 == 0 (no direct link)
```

**Constraints:**

*   1 <= N <= 1000 (Number of nodes)
*   0 <= node\_id < N
*   1 <= capacity <= 10000
*   0 <= congestion\_factor <= 10.0
*   0 < alpha <= 1.0
*   0 < beta <= 1.0
*   0 < threshold1 < threshold2 < 1.0
*   0 < max\_rate <= 10000

**Evaluation:**

Your solution will be evaluated based on correctness, efficiency, and adherence to the problem constraints.  The efficiency of your algorithm will be crucial for handling large-scale networks.  Consider using appropriate data structures and algorithms to minimize the time complexity of your solution. Special attention will be given to handling edge cases and maintaining network stability.
