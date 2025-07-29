## Project Name

`Distributed Load Balancer with Adaptive Routing`

## Question Description

You are tasked with building a simplified, distributed load balancer that can dynamically adapt to the performance of backend servers. This load balancer must efficiently distribute incoming requests across a cluster of servers, taking into account server capacity, latency, and potential failures.

**System Architecture:**

The system consists of:

1.  **Load Balancer Nodes:** Multiple load balancer instances that receive incoming requests and forward them to backend servers. These nodes should communicate with each other to maintain a consistent view of the backend server state.
2.  **Backend Servers:** A set of servers that process the actual requests. Each server has a limited capacity (requests it can handle concurrently) and variable latency.
3.  **Monitoring System (Simulated):** A mechanism (simulated within your code) that periodically provides load balancer nodes with information about the backend server's current load (number of active requests) and average latency.

**Functional Requirements:**

1.  **Request Distribution:** The load balancer should distribute incoming requests to the backend servers.
2.  **Server Selection:** The load balancer should select a backend server for each request based on the following criteria, prioritized in order:
    *   **Availability:** Servers that are considered "failed" should not be selected. A server is considered failed if it has not reported its status for a certain timeout period.
    *   **Capacity:** Servers should not be overloaded. The number of active requests on a server should not exceed its maximum capacity.
    *   **Latency:** Among available servers with sufficient capacity, the load balancer should prefer servers with lower average latency.
3.  **Adaptive Routing:** The load balancer should dynamically adjust its routing decisions based on the feedback from the monitoring system. When a server's latency increases or its load reaches capacity, the load balancer should shift traffic to other servers.
4.  **Heartbeat/Status Reporting:** Each backend server periodically sends its current load and average latency to the load balancers. Load balancers use this information for server selection and failure detection. If a load balancer doesn't receive a heartbeat from a server within a specified timeout, it should mark the server as "failed" and stop sending requests to it.
5.  **Distributed State Management:** Load balancer nodes should maintain a reasonably consistent view of the backend server state (availability, capacity, latency). You should describe how the load balancers share/maintain states.

**Technical Requirements:**

1.  Implement this system in Python.
2.  Use appropriate data structures to efficiently store and update the backend server state.
3.  Implement a strategy for load balancer nodes to share/maintain states.
4.  Implement a simple simulation of incoming requests, backend server processing, and the monitoring system.
5.  Consider edge cases such as:
    *   All servers are overloaded or have failed.
    *   New servers are added to the cluster.
    *   A server recovers from a failure.
    *   Inconsistent status reports from backend servers.

**Constraints:**

1.  **Efficiency:** Your solution should be reasonably efficient in terms of both time and space complexity. Consider the impact of your data structures and algorithms on performance, especially as the number of servers and load balancer nodes increases.
2.  **Scalability:** While you don't need to implement a fully scalable distributed system, consider the design choices that would support scalability in a real-world scenario. Discuss the potential bottlenecks and how they could be addressed.
3.  **Fault Tolerance:** The load balancer should be resilient to failures of backend servers and, to a lesser extent, load balancer nodes.
4.  **Concurrency:**  The load balancer should handle concurrent requests efficiently.
5.  **State Consistency:**  Strive for eventual consistency across load balancer nodes regarding backend server state. Discuss the trade-offs between consistency and performance in your chosen approach.

**Bonus Points:**

1.  Implement a mechanism for load balancer nodes to discover each other and form a cluster.
2.  Implement a basic health check for backend servers.
3.  Provide a clear explanation of your design choices, including the trade-offs you considered.

This problem requires you to think about system design, concurrency, data structures, and algorithms. It's a challenging problem that requires a good understanding of distributed systems principles. Good luck!
