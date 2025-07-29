## Question: Distributed Load Balancer Simulation

**Description:**

You are tasked with simulating a simplified distributed load balancer. The load balancer manages a cluster of servers, distributing incoming requests to optimize performance and resilience.

The system consists of the following components:

*   **Servers:** Each server has a unique ID, a processing capacity (measured in "units"), and a current load (also in "units"). Servers can fail (become unavailable) and recover (become available again).

*   **Requests:** Each request has a unique ID and a processing requirement (in "units").

*   **Load Balancer:** The load balancer receives requests and distributes them to available servers. The goal is to minimize the maximum load on any single server while ensuring requests are processed.

**Constraints & Requirements:**

1.  **Dynamic Server Pool:** The set of available servers changes dynamically. Servers can be added, removed (due to failure), or recovered at any time.
2.  **Request Queue:** Implement a request queue that holds requests waiting to be processed. The queue should support prioritization, where requests with smaller processing requirements have higher priority.
3.  **Load Balancing Algorithm:** Implement a "Least Loaded" strategy. When a server becomes available or a new request arrives, the load balancer should assign the request to the available server with the least current load, as long as the server has sufficient capacity.
4.  **Fault Tolerance:** If a server fails while processing a request, the request should be requeued and eventually reassigned to another available server. The system should continue operating even with server failures.
5.  **Scalability:** The system should be able to handle a large number of servers and requests efficiently. Consider data structures and algorithms that scale well.
6.  **Real-time Updates:** The system should provide real-time updates on server loads and request processing status.
7.  **Optimization:** Your solution should aim to minimize the maximum load on any server at any given time. The load balancer should strive for even distribution of load across available servers.
8.  **Concurrency:** The load balancer should handle multiple requests and server status updates concurrently. Use appropriate synchronization primitives to avoid race conditions and data corruption.
9.  **Edge Cases:** Handle cases where no servers are available, requests with processing requirements exceeding the capacity of any single server, and sudden bursts of requests.

**Input:**

The system receives events in the following format:

*   `AddServer(server_id: u32, capacity: u32)`: Adds a new server to the pool.
*   `RemoveServer(server_id: u32)`: Removes a server from the pool (due to failure). Any requests being processed by this server are requeued.
*   `RecoverServer(server_id: u32)`: Marks a server as available again.
*   `NewRequest(request_id: u32, processing_units: u32)`: Adds a new request to the queue.
*   `GetServerLoads() -> Vec<(u32, u32)>`: Returns a vector of (server\_id, current\_load) tuples for all available servers.
*   `GetRequestStatus(request_id: u32) -> RequestStatus`: Returns the status of the specified request, where `RequestStatus` can be `Queued`, `Processing(server_id: u32)`, or `Completed`.

**Output:**

The `GetServerLoads()` and `GetRequestStatus()` functions should return accurate information reflecting the current state of the system. The primary goal is to implement the load balancing logic efficiently and correctly.

**Evaluation:**

Your solution will be evaluated based on the following criteria:

*   **Correctness:** The load balancer distributes requests correctly and handles server failures gracefully.
*   **Efficiency:** The load balancing algorithm minimizes the maximum server load.
*   **Scalability:** The system can handle a large number of servers and requests.
*   **Concurrency:** The system handles concurrent operations safely and efficiently.
*   **Code Quality:** The code is well-structured, readable, and maintainable.

This problem requires careful consideration of data structures, algorithms, and concurrency. A well-designed solution should be able to handle a wide range of scenarios and perform efficiently under load. Good luck!
