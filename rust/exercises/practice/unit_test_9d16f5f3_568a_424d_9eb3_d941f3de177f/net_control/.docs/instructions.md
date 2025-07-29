Okay, here's a challenging Rust coding problem designed to push the limits of algorithmic thinking, data structure mastery, and optimization skills.

## Project Name

`network-congestion-control`

## Question Description

You are tasked with simulating a simplified network congestion control mechanism. Imagine a network of interconnected routers. Data packets need to be routed from a source to a destination. The network is prone to congestion, which can lead to packet loss and increased latency.

You are given a directed graph representing the network topology. Each node in the graph represents a router, and each edge represents a network link between two routers. Each link has a capacity, representing the maximum number of packets it can handle per unit of time.

The network operates in discrete time steps. At each time step, a source router wants to send a certain number of packets to a destination router. Your goal is to implement a congestion control algorithm that determines how many packets should actually be sent along each link in the network at each time step, while minimizing congestion and ensuring fairness.

**Specific Requirements:**

1.  **Network Representation:** The network topology is represented as a directed graph where each edge has a capacity. You should implement a data structure to efficiently represent this graph. The graph can be large (up to 10,000 routers and 50,000 links).

2.  **Congestion Metric:** Define a congestion metric for each link. A simple metric could be the utilization rate (packets sent / link capacity). You need to manage congestion levels on each link.

3.  **Routing:** Implement a mechanism to find paths from the source to the destination. You can use a shortest path algorithm like Dijkstra's or a more sophisticated routing algorithm that considers congestion levels. Multiple paths may exist, and your algorithm should be able to choose among them.

4.  **Congestion Control Algorithm:** Implement a congestion control algorithm. Consider implementing a variant of TCP congestion control (e.g., AIMD - Additive Increase, Multiplicative Decrease) or a more advanced scheme.

5.  **Fairness:** Implement a mechanism to ensure fairness among different source-destination pairs. If multiple source-destination pairs are trying to use the same links, your algorithm should allocate bandwidth in a fair manner.

6.  **Dynamic Network Conditions:** The network conditions (link capacities, packet arrival rates) may change over time. Your algorithm should be able to adapt to these changes.

7.  **Packet Loss Simulation:** Implement a simplified packet loss simulation. If the number of packets sent along a link exceeds its capacity at a given time step, a certain percentage of packets are lost (e.g., randomly drop packets until the link utilization is below 100%).

8.  **Latency Calculation:** Estimate the latency for packets traveling from the source to the destination. Latency should increase as links become more congested.

9.  **Input:** Your program should take as input:
    *   The network topology (list of routers and links with capacities).
    *   A list of source-destination pairs.
    *   The number of time steps to simulate.
    *   The packet arrival rate for each source-destination pair at each time step (this can be a randomly generated number or read from a file).

10. **Output:** Your program should output:
    *   The number of packets successfully delivered for each source-destination pair.
    *   The average latency for packets delivered for each source-destination pair.
    *   The maximum link utilization observed in the network.
    *   The total number of packets dropped due to congestion.

**Constraints and Edge Cases:**

*   The network topology can be sparse or dense.
*   Link capacities can vary significantly.
*   Packet arrival rates can be bursty (i.e., high traffic at certain times).
*   The shortest path may not always be the best path due to congestion.
*   The network may become partitioned (i.e., no path exists between some source-destination pairs).
*   The simulation should be efficient enough to run for a large number of time steps (e.g., 10,000) on a moderately sized network within a reasonable time limit (e.g., 1 minute).

**Optimization Requirements:**

*   Minimize packet loss.
*   Minimize average latency.
*   Maximize network utilization while avoiding congestion collapse.
*   Ensure fairness among source-destination pairs.
*   Optimize the runtime performance of your algorithm, especially pathfinding and congestion control logic.

**Judging Criteria:**

The submissions will be judged based on a combination of the following factors:

*   **Correctness:** The algorithm should correctly simulate network congestion control and produce accurate results.
*   **Efficiency:** The algorithm should be efficient enough to handle large networks and long simulation times.
*   **Effectiveness:** The algorithm should minimize packet loss, minimize latency, and maximize network utilization.
*   **Fairness:** The algorithm should ensure fairness among different source-destination pairs.
*   **Code Quality:** The code should be well-structured, readable, and well-documented.

This problem requires a deep understanding of networking concepts, graph algorithms, and optimization techniques. It also requires careful consideration of data structures and algorithm design to achieve the required performance. Good luck!
