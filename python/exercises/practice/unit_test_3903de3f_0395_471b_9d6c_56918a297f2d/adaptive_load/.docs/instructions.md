## Question: Distributed Load Balancing with Adaptive Resource Allocation

### Problem Description

You are tasked with designing a distributed load balancing system for a cloud service provider. The system needs to efficiently distribute incoming client requests across a cluster of servers (nodes), while dynamically adjusting resource allocation based on the observed load and server capabilities.

The system receives a stream of client requests, each with a specific resource requirement (CPU, Memory, Network bandwidth). Each server in the cluster has a limited capacity for these resources. The goal is to minimize the overall response time for clients, prevent server overload, and maximize resource utilization across the cluster.

**Specifics:**

1.  **Server Nodes:** The cluster consists of `N` server nodes, each with a fixed capacity for CPU, Memory, and Network bandwidth. Server nodes may have different resource capacities.

2.  **Client Requests:** Client requests arrive sequentially. Each request specifies the amount of CPU, Memory, and Network bandwidth it requires.

3.  **Load Balancer:** You need to implement a load balancer that decides which server node should handle each incoming request. The load balancer must consider:
    *   The current resource utilization of each server node.
    *   The resource requirements of the incoming request.
    *   A cost function that estimates the response time if the request is assigned to a particular server node. This cost function should consider the current load on the server and the new load introduced by the request.

4.  **Adaptive Resource Allocation:** The system needs to adapt to changing load patterns. If a server node becomes overloaded, the load balancer should avoid assigning new requests to it until its load decreases. Conversely, if a server node is underutilized, the load balancer should prioritize assigning requests to it.

5.  **Server Heterogeneity:** Server nodes might have varying performance characteristics. The load balancer should account for this by assigning weights to each server node based on its relative performance.

**Input:**

*   `N`: The number of server nodes in the cluster.
*   `server_capacities`: A list of tuples, where each tuple `(cpu_capacity, memory_capacity, network_capacity)` represents the resource capacities of a server node. The list has `N` elements.
*   `server_weights`: A list of floats representing the relative performance weights of each server node. The list has `N` elements. Higher weights indicate better performance.
*   `requests`: A list of tuples, where each tuple `(cpu_usage, memory_usage, network_usage)` represents the resource requirements of a client request.

**Output:**

*   A list of integers representing the server node assigned to each request in the `requests` list. The i-th element in the output list should be the index (0-indexed) of the server node assigned to the i-th request.
*   If a request cannot be fulfilled by any server node without exceeding its capacity, assign it to `-1`.

**Constraints:**

*   `1 <= N <= 1000`
*   `1 <= len(requests) <= 10000`
*   CPU, Memory, and Network bandwidth capacities and usages are non-negative integers.
*   Server weights are positive floats.
*   Minimize the overall response time for all requests. Response time is estimated using the cost function.
*   Avoid server overload.
*   Maximize resource utilization across the cluster.
*   The solution must be efficient enough to handle a large number of requests in a reasonable time (e.g., under 1 minute).

**Cost Function:**

You need to define a cost function that estimates the response time for a request assigned to a server node. A possible cost function could be based on the percentage of resource utilization after assigning the request. For example:

```
Cost = weight * (cpu_utilization_percentage + memory_utilization_percentage + network_utilization_percentage) / 3
```

Where `weight` is inversely proportional to the server's performance weight (i.e., higher server weights lead to lower cost).

**Example:**

```python
N = 3
server_capacities = [(100, 100, 100), (50, 50, 50), (75, 75, 75)]
server_weights = [1.0, 0.5, 0.75]
requests = [(10, 10, 10), (20, 20, 20), (30, 30, 30), (10, 10, 10), (40, 40, 40)]

# Expected Output (an example - the actual optimal assignment might differ):
# [0, 2, 0, 1, -1] # -1 since server 2 is full
```

**Judging Criteria:**

*   Correctness: The solution must correctly assign requests to server nodes without exceeding their capacity.
*   Efficiency: The solution must be efficient enough to handle a large number of requests in a reasonable time.
*   Optimization: The solution should minimize the overall response time for clients by making intelligent assignment decisions based on the cost function and server weights.
*   Handling Edge Cases: The solution must handle edge cases gracefully, such as requests that cannot be fulfilled by any server node.

This problem requires a combination of data structure knowledge, algorithmic thinking, and optimization techniques. Good luck!
