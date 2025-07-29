## Question: Distributed Load Balancer with Consistent Hashing

**Description:**

You are tasked with designing and implementing a simplified distributed load balancer. This load balancer distributes incoming requests across a cluster of backend servers. To ensure even distribution and minimize disruption during server additions or removals, you will employ consistent hashing.

**Scenario:**

Imagine you're building a content delivery network (CDN). Users request content (e.g., images, videos) identified by a unique content ID. Your load balancer needs to route each request to one of the available cache servers in the CDN cluster.

**Requirements:**

1.  **Consistent Hashing Implementation:** Implement a consistent hashing algorithm. You can use a simple hash function for mapping content IDs and server IDs to the hash ring.  The hash ring should be large enough to allow for good distribution.

2.  **Server Management:**
    *   Implement functionality to add new backend servers to the load balancer.
    *   Implement functionality to remove existing backend servers from the load balancer.

3.  **Request Routing:**
    *   Given a content ID, the load balancer must determine the appropriate backend server to which the request should be routed.  The chosen server should be the next server in the hash ring in a clockwise direction from the hashed content ID.

4.  **Handling Server Failures:** The load balancer should gracefully handle server failures. If the server to which a request is mapped is unavailable, the request should be routed to the next available server in the ring (clockwise). This failover mechanism should be transparent to the client.

5.  **Virtual Nodes (Shards):** To improve distribution, especially with a small number of physical servers, implement virtual nodes (also known as shards). Each physical server should be represented by multiple virtual nodes on the hash ring.  The number of virtual nodes per physical server should be configurable.

6.  **Optimization:**  The routing function (finding the appropriate server for a content ID) should be as efficient as possible.  Consider the data structures you use to represent the hash ring and server mappings.

**Constraints:**

*   The number of backend servers can vary dynamically.
*   Content IDs are strings. Server IDs are strings.
*   The hash function should be relatively fast (no cryptographic hashes are needed).  A simple modulo-based hash is acceptable for this problem, but be mindful of its limitations in real-world scenarios.
*   Minimize the amount of re-routing required when servers are added or removed.
*   Assume that the load balancer itself is highly available (you don't need to worry about its failure).

**Edge Cases:**

*   Empty server list.
*   All servers are temporarily unavailable.
*   Adding/removing the same server multiple times.
*   Content IDs that hash to the same value.
*   Large number of servers and content IDs.

**Evaluation Criteria:**

*   Correctness: The load balancer must correctly route requests according to the consistent hashing algorithm.
*   Efficiency: The routing function must be efficient, especially for a large number of servers and content IDs.
*   Robustness: The load balancer must handle server failures gracefully and recover automatically.
*   Scalability: The design should be scalable to handle a large number of servers and requests.
*   Code Quality: The code should be well-structured, readable, and maintainable.

This problem emphasizes the understanding of consistent hashing, its implementation details, and practical considerations for building a distributed system. It requires careful design choices to balance correctness, efficiency, and scalability. Good luck!
