## Project Name

`DistributedLoadBalancer`

## Question Description

You are tasked with designing and implementing a distributed load balancer. This load balancer sits in front of a cluster of servers (workers) and distributes incoming client requests across them. The goal is to ensure even distribution of load, handle server failures gracefully, and provide a consistent hashing mechanism to maintain session affinity where required.

**System Architecture:**

Imagine a system where clients send requests to a single entry point, the load balancer. The load balancer then forwards these requests to one of the available worker servers.

**Specific Requirements:**

1.  **Server Pool Management:** The load balancer must maintain a dynamic pool of worker servers. Servers can be added or removed from the pool at any time. The load balancer should be able to discover these changes automatically (e.g., through a health check mechanism, though you don't need to implement the health check itself; assume you receive notifications of server availability).

2.  **Load Balancing Algorithms:** Implement two distinct load balancing algorithms:
    *   **Round Robin:** Distribute requests sequentially to each server in the pool.
    *   **Consistent Hashing:** Use consistent hashing to map requests to servers based on a client identifier (e.g., client IP address). This ensures that requests from the same client are consistently routed to the same server, maintaining session affinity.  Use SHA-256 for hashing. The server pool should be modeled as a consistent hash ring.

3.  **Server Failure Handling:** If a server fails (is removed from the pool), the load balancer must automatically redistribute the load to the remaining available servers. For consistent hashing, the requests that were previously routed to the failed server should be re-routed to the next available server in the hash ring.

4.  **Concurrency:** The load balancer must be able to handle multiple concurrent requests efficiently.

5.  **API:** Implement the following methods:

    *   `add_server(server_id)`: Adds a server with the given `server_id` to the server pool. `server_id` is a string.
    *   `remove_server(server_id)`: Removes a server with the given `server_id` from the server pool.
    *   `get_server(client_id, algorithm)`: Returns the `server_id` of the server to which the request from the client with `client_id` (a string) should be routed. `algorithm` is an enum or string indicating the load balancing algorithm to use ("round_robin" or "consistent_hashing").

**Constraints and Considerations:**

*   **Server ID Uniqueness:**  Each server in the pool will have a unique `server_id`.
*   **Scalability:**  Consider how your design would scale to handle a large number of servers and requests. While you don't need to implement distributed data structures, think about the potential bottlenecks in your design.
*   **Thread Safety:**  Ensure your implementation is thread-safe, as multiple clients might be accessing the load balancer concurrently.
*   **Performance:**  Optimize for low latency in request routing.
*   **Hashing Collisions:** In consistent hashing, handle potential hash collisions gracefully.
*   **Empty Server Pool:**  Handle the case where the server pool is empty.  In this case, `get_server` should return `None`.
*   **Invalid Algorithm:** If an invalid `algorithm` is passed to `get_server`, raise a `ValueError`.

**Bonus Challenges:**

*   Implement a weighted round robin algorithm, where servers have different weights indicating their capacity.
*   Implement a mechanism to dynamically adjust the number of servers based on the overall system load.
*   Add support for different hashing algorithms in consistent hashing.

This problem requires a good understanding of data structures, algorithms, concurrency, and system design principles. It also demands careful consideration of edge cases and performance optimization.
