## Question: Distributed Load Balancer with Adaptive Routing

### Project Name: `adaptive-load-balancer`

### Question Description:

You are tasked with designing and implementing a distributed load balancer that intelligently routes incoming requests to a cluster of backend servers. The load balancer should adapt to varying server loads and network conditions to minimize latency and ensure high availability.

**Scenario:**

Imagine you are building a global content delivery network (CDN). Users from all over the world are requesting content (e.g., images, videos, documents) from your service. These requests need to be distributed across a set of geographically distributed backend servers. Each backend server has limited capacity and varying network latency to different regions. The goal is to design a load balancer that can efficiently distribute requests while minimizing response times and preventing any single server from becoming overloaded.

**System Design Requirements:**

1.  **Distributed Architecture:** The load balancer should be composed of multiple instances, distributed across different regions, to handle a large volume of requests and provide redundancy.
2.  **Adaptive Routing:** The load balancer must dynamically adjust its routing decisions based on real-time server load (CPU utilization, memory usage, active connections) and network latency.
3.  **Health Checks:** Implement a mechanism to continuously monitor the health of backend servers. Unhealthy servers should be automatically removed from the routing pool.
4.  **Session Persistence (Optional):** For certain types of requests (e.g., user authentication), it may be necessary to route subsequent requests from the same client to the same backend server (session affinity).

**Specific Implementation Requirements:**

1.  **Backend Server Abstraction:** Assume you have a function `ServeRequest(serverID string, request Request) Response` which simulates a backend server processing a request.  The `Request` and `Response` types can be simple structs. The serverID is a unique identifier for each server.
2.  **Load Balancing Algorithm:** Implement an adaptive routing algorithm that considers both server load and network latency. A simplified version of a weighted least connections algorithm is acceptable. You can use a simple ping to measure latency or assume pre-computed latency values.
3.  **Concurrency:** The load balancer must be able to handle a high volume of concurrent requests efficiently using Go's concurrency features (goroutines, channels, mutexes).
4.  **Configuration:** The load balancer should be configurable with the list of backend servers, their initial capacities, and health check intervals.
5.  **Metrics:** Implement basic metrics tracking, such as the number of requests routed to each server, average response time, and number of failed requests.

**Constraints:**

1.  **Scalability:** The load balancer should be designed to handle a large number of backend servers and a high volume of requests.
2.  **Fault Tolerance:** The system should be resilient to server failures and network outages.
3.  **Efficiency:** The routing algorithm should be computationally efficient to minimize latency.
4.  **Real-time Updates:** Load and latency information should be updated frequently to ensure accurate routing decisions.
5.  **Resource Limits:** Be mindful of resource consumption (CPU, memory) and avoid unnecessary overhead.

**Input/Output:**

The load balancer should expose an API to register backend servers, update their load, and handle incoming client requests.

*   `RegisterServer(serverID string, capacity int, initialLatency map[string]time.Duration)`: Registers a backend server with the load balancer.  `initialLatency` is a map of region to latency.
*   `UpdateServerLoad(serverID string, load float64)`: Updates the load of a backend server. The load is a value between 0.0 and 1.0, where 1.0 indicates full capacity.
*   `HandleRequest(request Request, clientRegion string) Response`: Routes an incoming request to the most suitable backend server based on server load, network latency, and health status.

**Judging Criteria:**

1.  **Correctness:** The load balancer correctly routes requests based on server load and network latency.
2.  **Scalability:** The load balancer can handle a large number of requests and backend servers without significant performance degradation.
3.  **Fault Tolerance:** The load balancer gracefully handles server failures and network outages.
4.  **Efficiency:** The routing algorithm is computationally efficient and minimizes latency.
5.  **Code Quality:** The code is well-structured, readable, and maintainable.  Use appropriate data structures and algorithms.  Proper error handling is important.
6.  **Concurrency Safety:** The code is thread-safe and avoids race conditions.
7.  **Design:** The system architecture is well-designed and addresses the requirements of a distributed load balancer.

This problem requires a strong understanding of concurrency, distributed systems, and algorithm design. The solution will need to balance multiple factors to achieve optimal performance and reliability. Good luck!
