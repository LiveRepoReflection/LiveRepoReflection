Okay, here's a challenging Go coding problem designed with the specified criteria in mind:

**Project Name:** `consistent-hashing-load-balancer`

**Question Description:**

You are tasked with designing and implementing a highly available and scalable load balancer using consistent hashing. This load balancer will distribute incoming requests across a cluster of backend servers.  The goal is to minimize disruption (i.e., request re-routing) when servers are added or removed from the cluster.

**Core Requirements:**

1.  **Consistent Hashing Implementation:** Implement a consistent hashing algorithm using a hash ring.  You can use any suitable hashing function (e.g., MD5, SHA-256) to map both servers and requests to the ring.  The ring should be implemented using a data structure that efficiently supports searching for the next server in the ring.  Consider using a tree-based structure to optimize search.

2.  **Virtual Nodes:**  Implement the concept of "virtual nodes" (also known as vnodes or replicas) for each backend server.  Each physical server should be represented by multiple virtual nodes on the hash ring. This helps to improve load distribution and fault tolerance. The number of virtual nodes per server should be configurable.

3.  **Dynamic Server Management:**  Implement functionality to add and remove backend servers from the cluster dynamically.  When a server is added, its virtual nodes should be placed on the hash ring. When a server is removed, its virtual nodes should be removed from the ring.  Ensure minimal disruption to existing requests during server additions and removals.

4.  **Request Routing:** Implement the core routing logic. Given an incoming request (represented by a string key), the load balancer should:

    *   Hash the request key.
    *   Find the nearest virtual node on the hash ring (clockwise direction).
    *   Route the request to the corresponding physical server associated with that virtual node.

5.  **Load Balancing Metrics:** Implement basic load monitoring. Track the number of requests being handled by each backend server.

**Constraints and Edge Cases:**

*   **Concurrency:** The load balancer must be thread-safe and handle concurrent incoming requests efficiently. Use appropriate locking mechanisms (e.g., mutexes, read-write mutexes) to protect shared data structures.
*   **Server Failures:**  Simulate server failures (e.g., by removing a server from the cluster). The load balancer should automatically redistribute requests that were previously routed to the failed server to other available servers.
*   **Hash Ring Size:** The hash ring size should be configurable. A larger ring typically leads to better distribution but potentially increases memory overhead.
*   **Uneven Server Capacity:** Design your solution to handle scenarios where backend servers have different capacities (e.g., some servers can handle more requests than others). You can model this by assigning more virtual nodes to servers with higher capacity.
*   **Zero Servers:** Handle the edge case where there are no backend servers in the cluster gracefully.  The load balancer should not crash and should return an appropriate error.
*   **Invalid Server Addresses:** Implement validation to ensure that server addresses are valid before adding them to the cluster.

**Optimization Requirements:**

*   **Minimize Request Re-routing:** The primary optimization goal is to minimize the number of requests that need to be re-routed when servers are added or removed. Consistent hashing inherently addresses this, but the efficiency of your implementation (e.g., the choice of data structures for the ring) will impact performance.
*   **Low Latency:** The request routing logic should be as fast as possible.  Optimize the search algorithm for finding the nearest virtual node on the hash ring.
*   **Memory Efficiency:**  Use memory efficiently, especially when dealing with a large number of servers and virtual nodes.
*   **Avoid contention:** Reduce lock contention as much as possible.

**Real-World Considerations:**

*   **Service Discovery:** (Optional, but highly recommended for bonus points) Integrate with a simple service discovery mechanism (e.g., a key-value store like etcd or Consul) to automatically discover and track available backend servers. You don't need to implement a full-fledged integration, but demonstrate how your load balancer could be extended to work with service discovery. Consider implementing a mock of the discovery service for testing purposes.

**Multiple Valid Approaches:**

Several data structures can be used to implement the hash ring (e.g., sorted arrays, balanced trees). Each approach has different trade-offs in terms of search performance, memory usage, and implementation complexity. You are encouraged to explore different approaches and justify your design choices.

**Grading Criteria:**

*   **Correctness:** The load balancer must correctly route requests to backend servers, even under dynamic server additions and removals.
*   **Efficiency:** The load balancer must be efficient in terms of request routing latency and memory usage.
*   **Concurrency:** The load balancer must be thread-safe and handle concurrent requests efficiently.
*   **Robustness:** The load balancer must handle edge cases and error conditions gracefully.
*   **Design:** The code should be well-structured, modular, and easy to understand.
*   **Testing:**  Include comprehensive unit tests to verify the correctness and performance of your implementation.
*   **Documentation:** Provide clear and concise documentation for your code.

This problem requires a strong understanding of data structures, algorithms, concurrency, and system design principles. Good luck!
