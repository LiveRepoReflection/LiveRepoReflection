Okay, here's a challenging Rust coding problem:

## Project Name

Network Congestion Control

## Question Description

You are tasked with simulating a network congestion control algorithm for a simplified network. The network consists of `n` nodes (numbered 0 to n-1) and `m` unidirectional links connecting them. Each link has a capacity, representing the maximum data it can transmit per time unit.

The goal is to implement a rate-limiting mechanism at each node to prevent network congestion.  Nodes send data to other nodes based on a predefined traffic pattern.  However, the sending rate must be dynamically adjusted based on network conditions to avoid exceeding link capacities.

**Specifics:**

1.  **Network Representation:** The network is represented by a graph where nodes are vertices and links are directed edges. The input will be given as an adjacency list where each node `i` has a list of tuples `(j, capacity)` representing a link from node `i` to node `j` with a given `capacity`.

2.  **Traffic Demand:** The traffic demand is given as a list of tuples `(source, destination, initial_rate)`.  This means that node `source` wants to send data to node `destination` at a rate of `initial_rate` per time unit.

3.  **Congestion Control Algorithm:** Implement a simplified version of the Additive Increase Multiplicative Decrease (AIMD) algorithm.

    *   **Additive Increase (AI):**  At each time unit, if all links used by the data flow (from source to destination) have available capacity, increase the sending rate by a constant value `alpha`.

    *   **Multiplicative Decrease (MD):** If any link used by the data flow becomes congested (i.e., its total traffic exceeds its capacity), reduce the sending rate by a factor `beta`.

4.  **Simulation:** Simulate the network for `t` time units. At each time unit:

    *   For each data flow, determine the path from the source to the destination.  If there's no path, the data flow is dropped.
    *   Calculate the actual traffic on each link based on the sending rates of all data flows using that link.
    *   Check for congestion on each link (total traffic exceeds capacity).
    *   Apply the AIMD algorithm to adjust the sending rates of the data flows.

5.  **Output:** Return a vector of the final sending rates for each data flow after `t` time units.  The order of the rates in the vector must match the order of the traffic demands in the input.

**Constraints:**

*   `1 <= n <= 100` (Number of nodes)
*   `1 <= m <= 500` (Number of links)
*   `1 <= len(traffic_demand) <= 20` (Number of traffic demands)
*   `1 <= capacity <= 1000` (Capacity of each link)
*   `1 <= initial_rate <= 100` (Initial sending rate)
*   `1 <= t <= 100` (Number of time units to simulate)
*   `0.1 <= alpha <= 1.0` (Additive increase constant)
*   `0.1 <= beta <= 0.9` (Multiplicative decrease factor)
*   There may be multiple paths from source to destination, select the path with fewest hops (you may implement BFS). If there are multiple such paths, select the one with the lowest node index sum.
*   If a node wants to send data to itself, the flow is dropped.
*   Rates cannot be negative.

**Assumptions:**

*   The network topology remains constant throughout the simulation.
*   Packet loss is not explicitly modeled; congestion is handled solely through rate adjustments.

**Example Input (Conceptual):**

```
n = 4 (Nodes: 0, 1, 2, 3)
adj_list = {
    0: [(1, 500), (2, 300)],
    1: [(3, 400)],
    2: [(3, 600)],
    3: []
}
traffic_demand = [(0, 3, 50), (1, 3, 70)]  // (source, destination, initial_rate)
t = 50
alpha = 1.0
beta = 0.5
```

**Difficulty:**

This problem is designed to be challenging due to:

*   The need to implement a graph algorithm (BFS or similar) to find paths.
*   The dynamic nature of the simulation, requiring careful tracking of link capacities and sending rates.
*   The optimization aspect of finding the shortest path with minimal node index sum in case of multiple shortest paths.
*   The number of edge cases to consider (no path, self-loop, etc.).
*   The potential for subtle errors in the AIMD implementation.

This problem tests a strong understanding of graph algorithms, simulation techniques, and congestion control concepts, along with the ability to write efficient and robust Rust code. Good luck!
