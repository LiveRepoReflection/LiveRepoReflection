## Problem Title: Optimal Network Partitioning for Service Resilience

### Question Description:

You are tasked with designing a resilient network architecture for a critical microservice application. The application consists of `N` microservices, represented as nodes in a graph. The connections between these services represent network dependencies and are represented as edges in the graph.  Each microservice `i` has a *resilience score* `R[i]`, indicating its ability to withstand failures. Each network link (edge) `(u, v)` has a *latency* `L[u, v]`, representing the time it takes for services `u` and `v` to communicate.

Due to budget constraints and physical limitations, you must partition the network into exactly `K` independent zones (subgraphs). Services within the same zone can communicate freely without incurring inter-zone latency. Communication *between* zones is significantly less reliable and has to go through an alternative channel with a high-latency overhead.

Your goal is to partition the network such that:

1.  **Connectivity:** Each of the `K` zones must be a connected subgraph of the original network.
2.  **Resilience:** Maximize the *minimum* resilience score across all zones.  Let `min_resilience[j]` be the minimum resilience score of any microservice in zone `j`.  Your primary goal is to maximize `min(min_resilience[1], min_resilience[2], ..., min_resilience[K])`. This ensures that even the weakest zone has a high resilience.
3.  **Latency Constraint:**  The total *inter-zone latency* should be minimized. The inter-zone latency is calculated as the sum of latencies of all edges that connect nodes belonging to different zones.  This is your tie-breaker. Among all partitions that maximize the minimum resilience score, you want to choose the one with the lowest inter-zone latency.

Write a function that takes the graph representation (adjacency list), the resilience scores of each microservice, the number of zones `K`, and the latencies of each connection as input, and returns a list representing the zone assignment for each microservice. The result should be a list of length `N`, where the `i`-th element is an integer in the range `[0, K-1]` representing the zone to which microservice `i` belongs.

**Input Format:**

*   `graph`: A list of lists representing the adjacency list of the graph. `graph[i]` contains a list of integers representing the indices of microservices connected to microservice `i`. Indices are 0-based.
*   `resilience`: A list of integers representing the resilience scores of each microservice. `resilience[i]` is the resilience score of microservice `i`.
*   `K`: An integer representing the number of zones to partition the network into. `1 <= K <= N`.
*   `latencies`: A dictionary where keys are tuples `(u, v)` representing an edge between microservices `u` and `v`, and values are the latencies `L[u, v]` for that edge.  Assume the graph is undirected; if `(u, v)` exists, `(v, u)` also exists with the same latency.

**Output Format:**

*   A list of integers representing the zone assignments for each microservice.  The `i`-th element of the list is an integer in the range `[0, K-1]` representing the zone to which microservice `i` belongs.

**Constraints:**

*   `1 <= N <= 1000` (Number of microservices)
*   `1 <= K <= N` (Number of zones)
*   `1 <= resilience[i] <= 1000` for all `i` (Resilience scores)
*   `1 <= L[u, v] <= 100` for all edges `(u, v)` (Latencies)
*   The graph is guaranteed to be connected.

**Example:**

```python
graph = [[1, 2], [0, 2, 3], [0, 1, 4], [1, 4], [2, 3]]
resilience = [5, 3, 8, 2, 7]
K = 2
latencies = {(0, 1): 10, (0, 2): 5, (1, 2): 2, (1, 3): 7, (2, 4): 1, (3, 4): 3, (1,0): 10, (2,0): 5, (2,1): 2, (3,1): 7, (4,2): 1, (4,3): 3}

# One possible optimal solution:
#  Zone 0: [0, 1, 3] (Resilience scores: 5, 3, 2. Min resilience: 2)
#  Zone 1: [2, 4] (Resilience scores: 8, 7. Min resilience: 7)
# min(2, 7) = 2

# Another possible solution could have the same min-resilience (5), but different inter-zone latency.

# Desired output format:
# [0, 0, 1, 0, 1]  # Microservice 0, 1, and 3 are in zone 0, and 2 and 4 are in zone 1
```
