## Project Name

`DistributedCacheInvalidation`

## Question Description

You are tasked with designing and implementing a distributed cache invalidation system. Imagine a large-scale application (e.g., a social media platform or an e-commerce site) that relies heavily on caching to improve performance and reduce database load. Data is cached across multiple geographically distributed cache servers.

When data changes in the primary data store (e.g., a database), the corresponding entries in the cache must be invalidated to ensure that users always see the most up-to-date information.  Directly updating the cache on every data change is often too slow and resource-intensive, especially for high-write applications. We need a mechanism to efficiently and reliably propagate invalidation messages across the distributed caching layer.

Your system must meet the following requirements:

*   **Scalability:** The system must handle a large number of cache servers and a high volume of invalidation requests.
*   **Low Latency:** Invalidation messages should be propagated as quickly as possible to minimize the time window during which users might see stale data.
*   **Reliability:** Invalidation messages must be delivered reliably, even in the presence of network partitions or server failures.  Messages should not be lost, and duplicate invalidations should be handled gracefully (idempotency).
*   **Eventual Consistency:** While immediate consistency is ideal, it is often impractical in a distributed system. The system should strive for eventual consistency, meaning that all cache servers will eventually receive the invalidation messages.
*   **Ordered Invalidation (Optional but highly desirable):** For certain data structures, the order of invalidations may matter. Implement a mechanism to guarantee the order of invalidation messages for a given cache key.
*   **Resource Efficiency:** The system should minimize resource consumption (CPU, memory, network bandwidth) to avoid impacting the performance of other services.

**Specific Requirements:**

1.  **Invalidation Message Format:** Define a clear and concise message format for invalidation requests. This format should include at least the cache key to invalidate and optionally a version/timestamp information for ordered invalidation.
2.  **Message Propagation Mechanism:** Implement a robust and scalable mechanism for propagating invalidation messages to all cache servers. Consider using a publish-subscribe (pub-sub) pattern, a gossip protocol, or a combination of techniques.
3.  **Cache Server Implementation:** Implement a basic cache server that can receive and process invalidation messages. The cache server should be able to store and retrieve data, and invalidate entries based on the received messages.
4.  **Failure Handling:** Design the system to handle common failure scenarios, such as network partitions, server crashes, and message loss. Implement mechanisms for detecting and recovering from these failures.
5.  **Optimization:** Identify and implement optimizations to improve the performance and scalability of the system. Consider techniques such as message batching, compression, and filtering.

**Constraints:**

*   The number of cache servers can be very large (hundreds or thousands).
*   Network latency between cache servers can vary significantly.
*   The system must be able to handle a high volume of invalidation requests (thousands or millions per second).
*   You are free to choose any suitable libraries or frameworks.

**Bonus Points:**

*   Implement a mechanism for monitoring and reporting on the performance of the invalidation system (e.g., message latency, failure rate).
*   Provide a way to configure the system dynamically (e.g., to add or remove cache servers).
*   Implement a mechanism for handling "poison pill" messages (e.g., messages that cause a cache server to crash).

This problem requires a good understanding of distributed systems concepts, caching strategies, and networking protocols. It also requires strong programming skills and the ability to design and implement a complex system from scratch.  The solution should be well-structured, modular, and easy to understand.  The efficiency of the solution will be a key factor in the evaluation. The trade-offs between different approaches should be clearly articulated.
