## Project Name

```
DistributedRateLimiter
```

## Question Description

Design and implement a distributed rate limiter service. This service will be used to protect backend systems from being overwhelmed by excessive requests. The rate limiter should be highly available, scalable, and performant.

**Specific Requirements:**

1.  **API**: The rate limiter should expose a simple API: `bool allowRequest(string clientID, string resourceID)`. This API should return `true` if the request from `clientID` to `resourceID` is allowed based on the configured rate limits, and `false` otherwise.
2.  **Rate Limit Configuration**: The rate limits should be configurable and flexible.  Rate limits are defined per `(clientID, resourceID)` pair.  The configuration should support multiple rate limits (e.g., 10 requests per second, 100 requests per minute, 1000 requests per hour). Think about how these different rate limits interact.
3.  **Distributed Operation**: The rate limiter service must be able to run across multiple machines/nodes to handle a high volume of requests. Data consistency across all nodes is crucial.
4.  **Data Consistency**:  Ensure that rate limiting decisions are consistent across the distributed system. A request that is allowed on one node should not be blocked on another (within a reasonable time window).  Consider the trade-offs between strong consistency and performance.
5.  **Scalability**: The service should be horizontally scalable to handle increasing request volumes. Adding more nodes should increase the overall throughput of the system.
6.  **Fault Tolerance**: The system should be resilient to node failures.  A single node failure should not disrupt the overall rate limiting functionality.
7.  **Performance**: The `allowRequest` API should have low latency (ideally in the single-digit milliseconds).  Minimize the overhead introduced by the rate limiter.
8.  **Concurrency**: The rate limiter must handle concurrent requests efficiently.
9.  **Client Identification**: The clientID is a string uniquely identifying a client.
10. **Resource Identification**: The resourceID is a string uniquely identifying the resource being accessed.
11. **Edge Cases**: Handle edge cases such as:
    *   A client suddenly disappearing (e.g., client application crashes).
    *   Clock skew between different nodes in the distributed system.
    *   Configuration changes to the rate limits while the system is running.
12. **Optimizations**: Consider optimizations such as:
    *   Caching frequently accessed rate limits.
    *   Batching operations to reduce communication overhead.
    *   Using efficient data structures to track request counts.

**Constraints:**

*   You are free to choose any data store (e.g., Redis, Cassandra, ZooKeeper) or in-memory data structures for storing rate limit information. Justify your choice.
*   Assume the system will handle a very high number of requests per second.
*   Configuration updates should propagate quickly but eventual consistency is acceptable.
*   Focus on algorithmic efficiency and system design aspects.

**Deliverables:**

1.  A high-level design document outlining the architecture of your distributed rate limiter service.  Include diagrams to illustrate the key components and interactions.
2.  Implement the `allowRequest` API in C++.
3.  Describe how you would handle configuration management and deployment.
4.  Explain your approach to testing the rate limiter service, including unit tests and integration tests.  Consider how you would simulate a high-load environment.
5.  Discuss the trade-offs you made in your design and implementation.

This problem requires a solid understanding of distributed systems principles, concurrency, data structures, and algorithms. Be prepared to discuss your design choices and justify your implementation. Good luck!
