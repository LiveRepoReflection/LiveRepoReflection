## Question: Distributed Load Balancing with Adaptive Routing

**Problem Description:**

You are designing a distributed load balancing system for a high-traffic web service. The system consists of `N` backend servers and `M` load balancer nodes. Each backend server has a capacity, representing the maximum number of requests it can handle concurrently. Each load balancer node receives incoming requests and must distribute them to the backend servers in a way that maximizes throughput while respecting server capacities and minimizing latency.

The challenge lies in adapting the routing strategy based on real-time feedback from the backend servers. Each backend server periodically reports its current load (number of active requests) and its average response time (latency). The load balancers must use this information to dynamically adjust their routing decisions.

**Specifics:**

*   **Input:**

    *   `N`: Number of backend servers (1 <= N <= 10^5).
    *   `M`: Number of load balancer nodes (1 <= M <= 10^3).
    *   `server_capacities`: A list of N integers, where `server_capacities[i]` represents the maximum number of concurrent requests that server `i` can handle (1 <= `server_capacities[i]` <= 10^4).
    *   `initial_loads`: A list of N integers, where `initial_loads[i]` represents the initial number of concurrent requests that server `i` are handling (0 <= `initial_loads[i]` <= `server_capacities[i]`).
    *    `latency_matrix`: A M x N matrix of floats, where `latency_matrix[j][i]` represents the latency between the load balancer node `j` and the backend server `i`. (0 <= `latency_matrix[j][i]` <= 10).
    *   `requests`: An integer, the number of incoming requests to route (1 <= requests <= 10^7).

*   **Output:**

    *   A list of integers of length `N`, where the `i`-th element represents the number of requests assigned to server `i`. The routing must obey the server capacities.
    *   If the total requests exceeds the total capacity of all servers, assign as many requests as possible while adhering to the capacity constraints and return the number of requests assigned to each server.

*   **Constraints:**

    *   **Capacity Constraint:** The number of requests assigned to each server must not exceed its capacity.
    *   **Load Balancing Goal:** The requests should be distributed to backend servers in a way to minimize the total latency.  Consider both server load and network latency in your routing decisions.  A server that is less loaded, but has a very high network latency, might not be the best choice.
    *   **Adaptive Routing:** You are provided with initial load information, but the load balancers can not get any real-time feedback during assignment. The solution should be designed to perform well with the given initial load and latency.
    *   **Scalability:** Your solution must be efficient enough to handle a large number of requests and servers. Aim for a time complexity that scales reasonably with `N`, `M`, and `requests`. Specifically, naive O(N \* M \* requests) solutions are likely to time out.
    *   **Optimization Metric:** While there is no single "correct" answer, your solution will be evaluated based on how effectively it balances the load across servers while minimizing total latency.
    *   **Tie-breaking:** In cases where multiple routing strategies achieve similar load balancing and latency, prioritize strategies that distribute requests more evenly across the *available* capacity (capacity - current load).

*   **Example:**

    Let's say you have the following inputs:

    *   `N = 2` (2 backend servers)
    *   `M = 1` (1 load balancer node)
    *   `server_capacities = [100, 150]`
    *   `initial_loads = [20, 30]`
    *   `latency_matrix = [[0.5, 1.0]]` (latency from LB to server 0 is 0.5, to server 1 is 1.0)
    *   `requests = 200`

    A possible (and good) output might be:

    *   `[80, 120]`

    Explanation: Server 0 gets 80 requests, bringing its total load to 100 (its capacity). Server 1 gets 120 requests, bringing its total load to 150 (its capacity). The total requests assigned is 200 (80+120), which is equal to the number of requests. The distribution also favors the server with lower latency.
