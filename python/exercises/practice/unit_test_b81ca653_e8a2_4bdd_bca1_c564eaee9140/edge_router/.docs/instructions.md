## Question: Optimal Edge Router Placement

### Question Description

You are tasked with designing the network infrastructure for a rapidly expanding data center. The data center is represented as an undirected graph where nodes represent servers and edges represent potential network connections. Due to budget constraints and physical limitations, you can only install a limited number of high-capacity edge routers.

The goal is to find the optimal placement of these edge routers to minimize the average latency for data transmission between any two servers in the data center. Latency is defined as the number of hops (edges) in the shortest path between two servers. If a server is directly connected to an edge router, its latency to an edge router is 1. Servers not directly connected to any edge router must connect through other servers, increasing latency.

**Specifically:**

1.  **Input:**
    *   `n`: The number of servers in the data center (numbered from 0 to n-1).
    *   `edges`: A list of tuples, where each tuple `(u, v)` represents an undirected edge between servers `u` and `v`.
    *   `k`: The maximum number of edge routers you can install.
    *   `server_weights`: A list of integers representing the importance weight of each server (server importance influences the weighted average latency).

2.  **Output:**
    *   A list of server indices representing the optimal locations to place the `k` edge routers.

**Objective Function:**

Minimize the *weighted average latency* of all servers to their nearest edge router.  The weighted average latency is calculated as follows:

*   For each server `i`, find the shortest path (minimum number of hops) to the nearest server that has an edge router. Let this shortest path length be `latency(i)`.

*   Calculate the total weighted latency:  `sum(latency(i) * server_weights[i] for i in range(n))`

*   Divide the total weighted latency by the sum of all server weights to get the weighted average latency.

**Constraints:**

*   `1 <= n <= 1000` (Number of servers)
*   `0 <= len(edges) <= n * (n - 1) / 2` (Number of edges; the graph can be dense)
*   `1 <= k <= min(n, 10)` (Number of edge routers; limited number of routers)
*   `1 <= server_weights[i] <= 100` for all `i` (Server weights)
*   The graph represented by `edges` is guaranteed to be connected.

**Optimization Requirements:**

*   The solution must minimize the weighted average latency.  Since finding the absolute optimal solution might be computationally expensive, aim for a solution that significantly reduces the latency compared to a random placement of edge routers.

**Considerations:**

*   The placement of edge routers significantly impacts the overall network performance.  Placing them strategically to cover critical servers and minimize the overall hop count is crucial.
*   The server weights indicate the importance of minimizing latency for specific servers. High-weight servers should be prioritized when placing edge routers.
*   The constraint on the number of edge routers `k` forces you to make strategic choices about their placement.

**Example:**

```
n = 5
edges = [(0, 1), (0, 2), (1, 2), (1, 3), (2, 4), (3, 4)]
k = 2
server_weights = [1, 1, 1, 1, 1]

# One possible optimal solution:
# [1, 2]  (Place edge routers at servers 1 and 2)
```

**Challenge:**

Develop an efficient algorithm to determine the best locations for the edge routers, considering the graph structure, the limited number of routers, and the server weights. The complexity of the problem stems from the need to explore different combinations of router placements while efficiently calculating the resulting average latency. Consider the trade-offs between solution accuracy and runtime.
