## Question: Optimized Network Routing with Congestion Control

### Question Description

You are tasked with designing an efficient routing algorithm for a large-scale communication network. The network consists of `N` nodes (numbered 0 to N-1) and `M` bidirectional links connecting these nodes. Each link has a *capacity* representing the maximum amount of data it can handle at any given time.

Due to fluctuating network conditions, each link also experiences *congestion*. The congestion on a link at any given time affects the latency of data transmission along that link. Higher congestion implies higher latency.

Specifically, the latency of a link `L` is defined as `latency(L) = base_latency(L) * (1 + congestion(L)^2)`. You are given the `base_latency` for each link, and the `congestion` on each link is dynamically updated based on the amount of data flowing through it.

The amount of congestion on a link `L` is defined as the `flow(L) / capacity(L)`, where `flow(L)` is the current data flow on link `L` and `capacity(L)` is the capacity of the link.

You are given a series of `Q` routing requests. Each request consists of a source node `src`, a destination node `dest`, and a data amount `data`.

Your goal is to design an algorithm that, for each routing request, finds the *minimum latency path* from `src` to `dest` and routes the `data` along this path.

**Important Considerations:**

1.  **Dynamic Congestion:** After routing data along a path, the congestion on each link in the path **must be updated** before processing the next routing request. The flow on a link increases by the amount of data routed through it.
2.  **Capacity Constraint:** The data flow on any link at any time cannot exceed its capacity. If there is no path from `src` to `dest` with sufficient capacity to route the `data`, return -1.
3.  **Real-World Application:** Minimize the overall latency across all routing requests. The algorithm should be efficient enough to handle a large number of nodes, links, and routing requests.
4.  **Optimality vs. Efficiency:** Finding the absolute optimal path for each request might be computationally expensive. You need to balance the optimality of the path with the efficiency of your algorithm.  Consider heuristics or approximations if necessary.
5.  **Tie Breaking:** If there are multiple paths with the same minimum latency, choose the path with the fewest number of hops (links). If there's still a tie, any of the paths are acceptable.

**Input Format:**

*   `N`: Number of nodes (0 to N-1).
*   `M`: Number of links.
*   `links`: A vector of tuples, where each tuple `(u, v, capacity, base_latency)` represents a bidirectional link between node `u` and node `v` with the given `capacity` and `base_latency`.
*   `Q`: Number of routing requests.
*   `requests`: A vector of tuples, where each tuple `(src, dest, data)` represents a routing request from node `src` to node `dest` with the given amount of `data`.

**Output Format:**

*   A vector of `Q` floating-point numbers, where each number represents the minimum latency for the corresponding routing request. If no path exists with sufficient capacity, output -1.

**Constraints:**

*   1 <= N <= 1000
*   1 <= M <= N * (N - 1) / 2
*   1 <= Q <= 1000
*   0 <= src, dest < N
*   1 <= capacity <= 1000
*   1 <= base\_latency <= 100
*   1 <= data <= 1000
*   All inputs are integers except for the output which contains floating point numbers.

**Example:**

Let's say your program receives the following inputs:

```
N = 4
M = 5
links = [(0, 1, 10, 5), (0, 2, 5, 2), (1, 2, 8, 3), (1, 3, 12, 4), (2, 3, 6, 1)]
Q = 2
requests = [(0, 3, 4), (0, 3, 3)]
```

The algorithm should:

1.  For the first request (0, 3, 4), find the minimum latency path from node 0 to node 3, considering the initial congestion (which is 0 for all links initially).
2.  Route the data (4) along this path, updating the flow and congestion of each link in the path.
3.  For the second request (0, 3, 3), find the minimum latency path from node 0 to node 3, considering the updated congestion from the previous request.
4.  Route the data (3) along this path, updating the flow and congestion of each link in the path.
5. Return the minimum latency for each path.

Good luck!
