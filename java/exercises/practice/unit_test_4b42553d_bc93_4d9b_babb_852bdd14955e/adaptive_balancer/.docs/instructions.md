## Distributed Load Balancer with Adaptive Routing

**Question Description:**

You are tasked with designing and implementing a distributed load balancer for a system handling a high volume of incoming requests. The system consists of `N` servers, each with varying processing capabilities and current load. The load balancer must distribute incoming requests to these servers in a way that minimizes the overall response time and prevents any single server from being overloaded.

Each server has a capacity represented by an integer value from 1 to 10. A server with capacity of 10 can take 10 times as much load as capacity 1.

Specifically, you need to implement the following features:

1.  **Dynamic Server Discovery:** The load balancer should be able to dynamically discover available servers and their capacities. Servers can join or leave the system at any time.

2.  **Adaptive Routing:** The load balancer should intelligently route incoming requests based on the following factors:
    *   **Server Capacity:** Higher capacity servers should receive a proportionally larger share of the incoming requests.
    *   **Current Load:** The load balancer should track the number of requests currently being processed by each server. Servers with higher current load should receive fewer new requests.
    *   **Network Latency:** The load balancer should consider the network latency between itself and each server. Servers with lower latency should be preferred.

3.  **Health Checks:** The load balancer should periodically perform health checks on each server to ensure that it is still functioning correctly. If a server fails a health check, it should be removed from the pool of available servers until it recovers.

4.  **Request Prioritization:** The load balancer should support request prioritization, where some requests are considered more important than others. High-priority requests should be routed to servers with lower current load and lower network latency.

5.  **Overload Protection:** The load balancer should implement mechanisms to prevent any single server from being overloaded. This may involve temporarily rejecting new requests or redirecting them to other servers.

**Input:**

*   A stream of incoming requests, each with a priority level (high, medium, or low) and a unique request ID.
*   A dynamic list of available servers, each with a capacity and network latency. Server capacity will be an integer between 1 and 10. Network latency will be measured with an arbitrary integer.
*   Health check results for each server (pass or fail).

**Output:**

For each incoming request, the load balancer should output the ID of the server to which the request is routed. If no server is available, the load balancer should output "REJECTED".
Your output must be printed to the standard output.

**Constraints:**

*   The number of servers `N` can vary from 1 to 1000.
*   The request rate can be very high (up to 100,000 requests per second).
*   Servers can join, leave, or fail at any time.
*   The load balancer must be highly available and fault-tolerant.
*   The solution must be efficient and scalable.
*   The time complexity of request routing should be optimized.

**Evaluation Criteria:**

Your solution will be evaluated based on the following criteria:

*   **Correctness:** The load balancer must correctly route requests to available servers, taking into account server capacity, current load, network latency, and request priority.
*   **Performance:** The load balancer must be able to handle a high volume of incoming requests with minimal latency.
*   **Scalability:** The load balancer must be able to scale to handle a large number of servers and requests.
*   **Robustness:** The load balancer must be able to handle server failures and other unexpected events.
*   **Code Quality:** The code must be well-structured, documented, and easy to understand.

**Bonus:**

*   Implement a mechanism for automatically scaling the number of servers based on the current load.
*   Implement a distributed consensus algorithm to ensure that all load balancer instances have a consistent view of the system state.
*   Use machine learning techniques to predict server load and optimize request routing.
