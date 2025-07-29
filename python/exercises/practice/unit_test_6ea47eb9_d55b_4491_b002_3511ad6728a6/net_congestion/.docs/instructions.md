## Project Name

```
network-congestion-control
```

## Question Description

You are tasked with simulating a simplified network congestion control algorithm. Imagine a network with multiple nodes connected by links. Each link has a capacity, representing the maximum amount of data it can transmit per unit time. Nodes send data packets across these links to reach their destinations. Congestion occurs when the demand for a link's capacity exceeds its limit, leading to packet loss or delays.

Your goal is to implement a congestion control mechanism that adjusts the sending rate of nodes to avoid overloading the network. The network is modeled as a directed graph where nodes are integers from 0 to N-1. Links are represented by tuples (u, v, capacity), meaning a link from node u to node v with a given capacity. Each node `i` has a rate limit `r_i`.

**Specifics:**

1.  **Network Representation:** The network is provided as a list of `(u, v, capacity)` tuples and the total number of nodes `N`.

2.  **Node Sending Rates:** You are given a list of initial sending rates, `initial_rates`, for each node (node `i` has rate `initial_rates[i]`).

3.  **Routing:** Assume a fixed routing scheme: For each node i, you are given a list of routes `routes[i]`. Each route is a list of nodes representing a path from node `i` to a destination. A packet sent from node i will follow the routes in `routes[i]` until they reach their destination.

4.  **Congestion Detection:** For each link (u, v), calculate the total flow (sum of sending rates of all nodes using that link). If the total flow exceeds the link's capacity, congestion is detected on that link.

5.  **Rate Adjustment:** When congestion is detected on any link, implement a **multiplicative decrease** for all sending nodes that use the congested link. Multiply their sending rate by a factor `beta` (0 < `beta` < 1). Also, implement an **additive increase** to the sending rate of each node (increase by `alpha`) if they haven't used any congested link.

6.  **Rate Boundaries:** The sending rate of a node cannot be negative and cannot exceed a maximum rate of `max_rate`.

7.  **Simulation:** Simulate the network for `T` time steps. In each time step, calculate the flow on each link, detect congestion, and adjust sending rates accordingly.

8.  **Objective:** Return the final sending rates of each node after `T` time steps.

**Input:**

*   `N`: The number of nodes in the network (integer).
*   `links`: A list of tuples `(u, v, capacity)` representing the network links (list of tuples of integers).
*   `initial_rates`: A list of initial sending rates for each node (list of floats).
*   `routes`: A list of lists, where `routes[i]` is a list of possible paths node `i` can send data to. Each path is a list of node integers.
*   `T`: The number of simulation time steps (integer).
*   `alpha`: The additive increase factor (float).
*   `beta`: The multiplicative decrease factor (float between 0 and 1).
*   `max_rate`: The maximum allowed sending rate for any node (float).

**Output:**

*   A list of floats representing the final sending rates of each node after `T` time steps.

**Constraints:**

*   1 <= N <= 100
*   1 <= len(links) <= 200
*   0 <= u, v < N for each link (u, v, capacity)
*   1 <= capacity <= 1000 for each link (u, v, capacity)
*   0 <= initial\_rates[i] <= max\_rate for all i
*   1 <= T <= 100
*   0 < alpha <= 10
*   0 < beta < 1
*   1 <= max\_rate <= 100

**Example:**

Let's simplify with N = 2, links = [(0, 1, 10)], initial\_rates = \[5, 5], routes = \[\[\[0, 1]], \[\[1]]], T = 1, alpha = 1, beta = 0.5, max\_rate = 10.

In this case, node 0 sends to node 1, using the link (0, 1). Node 1 sends to itself.
The total flow on link (0, 1) is 5, which is below the capacity of 10. No congestion occurs on this link.
Node 0 rate will be increased by alpha=1, node 1 rate will be increased by alpha = 1.
So final\_rates = \[6, 6].

**Challenge:**

*   Handle overlapping routes and shared links efficiently.
*   Optimize the congestion detection and rate adjustment steps for large networks.
*   Consider the impact of different `alpha` and `beta` values on network stability and fairness.
*   Implement the simulation to run within reasonable time constraints for the given input sizes.

This problem requires careful consideration of data structures, algorithmic efficiency, and real-world network behavior. Good luck!
