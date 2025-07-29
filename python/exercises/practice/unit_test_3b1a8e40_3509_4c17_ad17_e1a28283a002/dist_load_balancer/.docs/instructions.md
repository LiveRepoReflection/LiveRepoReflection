## Project Name

```
DistributedLoadBalancer
```

## Question Description

You are tasked with designing a distributed load balancer that can handle a massive number of incoming requests and distribute them efficiently across a cluster of backend servers. The system must be highly available, scalable, and fault-tolerant.

**Specific Requirements:**

1.  **Request Distribution:** Implement a consistent hashing algorithm to distribute requests across backend servers. Consistent hashing ensures that when servers are added or removed, only a minimal number of keys need to be remapped, minimizing disruption.

2.  **Dynamic Server Discovery:** The load balancer should automatically discover and monitor the health of backend servers. If a server becomes unhealthy (e.g., due to a crash or overload), the load balancer should automatically stop routing traffic to it. When a server recovers or a new server is added, the load balancer should incorporate it into the routing scheme.

3.  **Health Checks:** Implement a mechanism for performing periodic health checks on backend servers. These health checks should be configurable (e.g., HTTP status code checks, TCP connection checks).

4.  **Load Balancing Strategies:** Implement at least two load balancing strategies:
    *   **Weighted Round Robin:** Distribute requests to servers based on a configurable weight assigned to each server. Servers with higher weights should receive a proportionally larger share of the traffic.
    *   **Least Connections:** Route requests to the server with the fewest active connections at the time of the request.

5.  **Concurrency and Throughput:** The load balancer must be able to handle a high volume of concurrent requests with minimal latency. Optimize the code for performance and scalability.

6.  **Fault Tolerance:** The load balancer itself should be distributed and fault-tolerant. If one load balancer instance fails, other instances should be able to take over its responsibilities without significant service interruption. For simplicity, you can simulate multiple load balancer instances within a single program.

7.  **API Endpoints:** Provide the following API endpoints:
    *   `add_server(server_id, address, weight)`: Adds a new backend server to the load balancer.  `server_id` is a unique identifier, `address` is the server's network address, and `weight` is an optional parameter for weighted round robin (default to 1 if not given).
    *   `remove_server(server_id)`: Removes a backend server from the load balancer.
    *   `health_check_passed(server_id)`: Notifies the load balancer that a health check passed for a specific server.
    *   `health_check_failed(server_id)`: Notifies the load balancer that a health check failed for a specific server.
    *   `get_next_server()`: Returns the address of the next server to handle a request, based on the configured load balancing strategy.

**Constraints:**

*   **Scalability:** The solution should scale to handle a large number of backend servers (e.g., hundreds or thousands).
*   **Performance:**  `get_next_server()` should have minimal latency (ideally O(1) or O(log n) where n is the number of servers).
*   **Availability:** The system should minimize downtime in the event of server failures or load balancer instance failures.
*   **Concurrency:**  All operations (adding/removing servers, health checks, request routing) must be thread-safe.
*   **Resource Management:**  Efficiently manage resources (CPU, memory) to avoid bottlenecks.

**Bonus Challenges:**

*   Implement a circuit breaker pattern to prevent cascading failures.
*   Add support for session persistence (sticky sessions) to route requests from the same client to the same server.
*   Implement advanced health check strategies (e.g., adaptive health checks based on server response times).
*   Provide metrics and monitoring capabilities (e.g., request rate, error rate, server utilization).

This problem requires a strong understanding of distributed systems concepts, data structures, and concurrency. It encourages the use of efficient algorithms and careful design to meet the performance, scalability, and availability requirements.
