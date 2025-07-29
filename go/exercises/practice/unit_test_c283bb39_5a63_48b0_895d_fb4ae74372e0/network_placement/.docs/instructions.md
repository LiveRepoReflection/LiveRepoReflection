## Question: Optimal Network Placement

### Question Description

You are tasked with designing the core network infrastructure for a rapidly expanding cloud service provider, "NimbusCloud". NimbusCloud offers various services, including virtual machines, databases, and object storage, to its clients across a geographically distributed set of data centers.

NimbusCloud aims to provide the lowest possible latency and highest possible bandwidth for its clients accessing these services. To achieve this, you must optimally place a limited number of high-bandwidth network devices (routers) within the existing data center network.

**Input:**

1.  **Data Centers (Nodes):** A list of `n` data centers (nodes) represented by their unique IDs (integers from 0 to n-1).

2.  **Network Topology (Edges):** A list of undirected edges representing the existing network connections between data centers. Each edge is represented as a tuple `(u, v, latency)`, where `u` and `v` are the IDs of the connected data centers, and `latency` is a positive integer representing the network latency between them. The graph is guaranteed to be connected.

3.  **Service Demand (Traffic Matrix):** A matrix `demand[i][j]` representing the amount of traffic (in units) flowing between data center `i` and data center `j`.

4.  **Number of Routers (k):** The number of high-bandwidth routers you can place in the network. You can place at most one router per data center.

5.  **Router Capacity (capacity):** Each router can handle a maximum amount of traffic.

**Objective:**

Determine the optimal placement of `k` routers among the `n` data centers to minimize the **total weighted latency**. The total weighted latency is calculated as the sum of the product of traffic demand and shortest path latency for all pairs of data centers.

`Total Weighted Latency = Σ (demand[i][j] * shortestPathLatency(i, j))`

where `shortestPathLatency(i, j)` is the shortest path latency between data center `i` and data center `j` after placing the routers. The traffic must flow within the router capacity limits.

**Router Impact:**

Placing a router at a data center significantly reduces the latency for traffic passing *through* that data center. Specifically, for any path that includes a data center with a router, the latency of *each edge* along that path is considered to be reduced by a factor of `reductionFactor`.

**Constraints:**

*   `1 <= n <= 200` (Number of data centers)
*   `0 <= k <= min(n, 20)` (Number of routers)
*   `1 <= latency <= 100` (Latency between data centers)
*   `0 <= demand[i][j] <= 100` (Traffic demand between data centers)
*   `1000 <= capacity <= 5000` (Router capacity)
*   `0.1 <= reductionFactor <= 0.5` (Latency reduction factor)
*   The traffic flowing through each router cannot exceed its `capacity`.

**Assumptions:**

*   You can use any standard graph algorithm library available in Go.
*   The input graph is guaranteed to be connected.
*   You do not need to implement the shortest path algorithm yourself, you can use existing library.
*   The `reductionFactor` is applied to the original `latency` value of each edge along the path (not the already-reduced latency).
*   The traffic between node `i` and node `j` must go through only one single path. You need to find the shortest path between `i` and `j`, and all the traffic `demand[i][j]` must go through that shortest path.

**Output:**

A list of data center IDs (integers from 0 to n-1) representing the optimal placement of the `k` routers. If there are multiple solutions that minimize the total weighted latency, return any one of them. If no solution can satisfy all the constrains, return an empty list.

**Judging:**

Your solution will be judged based on its ability to minimize the total weighted latency across a set of hidden test cases. Test cases will vary in size, network topology, demand patterns, and router constraints. Efficiency and correctness are crucial. Suboptimal solutions will receive partial credit, and solutions exceeding the time limit will receive no credit.

**Example:**

Let's say, `n` = 4, `k` = 1, graph has edges (0,1,10), (1,2,10), (2,3,10), and `demand[0][3]` is high. Placing the router at node 1 or 2 is likely to give a better result than placing it at 0 or 3. You need to consider all traffic and the limited router capacity when making the decision.
