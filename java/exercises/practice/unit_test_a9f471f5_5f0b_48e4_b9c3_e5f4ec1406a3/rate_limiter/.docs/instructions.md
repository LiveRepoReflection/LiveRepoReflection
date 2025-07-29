## Project Name

`DistributedRateLimiter`

## Question Description

Design and implement a distributed rate limiter. This system must handle requests from multiple clients across a distributed environment, ensuring that no client exceeds its allocated rate limit.

**Functionality:**

The rate limiter should provide a `shouldAllow(clientId: String)` method. This method determines whether a request from a given `clientId` should be allowed based on its configured rate limit. The rate limiter needs to persist and update the request counts for each client.

**Requirements and Constraints:**

*   **Scalability:** The system must scale to handle a large number of clients and high request volumes.
*   **Concurrency:** The system must be thread-safe and handle concurrent requests from multiple clients.
*   **Accuracy:** The rate limiting should be as accurate as possible, minimizing the chance of clients exceeding their limits, although perfect accuracy in a distributed environment is not always achievable.
*   **Persistence:** Request counts must be persisted to a durable storage system to survive restarts and ensure consistency across multiple rate limiter instances.
*   **Configuration:** Each client should have its own rate limit, defined as `requestsPerSecond: Int`.  These rate limits can be updated dynamically.
*   **Fault Tolerance:** The system should be resilient to failures of individual rate limiter instances and storage nodes. If a storage node fails, the system must continue to operate, potentially with slightly reduced accuracy.
*   **Efficiency:** The `shouldAllow` method should have low latency to avoid impacting application performance.
*   **Distribution:** The rate limiter will be deployed on multiple servers, meaning that the state (request counts) needs to be shared between these servers.
*   **Dynamic Rate Limits:** The rate limits for clients can change during runtime. The system needs to handle these changes efficiently.
*   **Client Identification:** Assume a client is uniquely identified by a string `clientId`.
*   **Time Window:** The rate limit is defined per second. The system needs to track the requests within the current second.
*   **No External Libraries (mostly):** You are allowed to use basic Java libraries (Collections, etc.), but you are highly encouraged to implement the core logic yourself without relying on external rate limiting libraries. The goal is to evaluate your system design and implementation skills. The use of a caching library like Caffeine is permissible for optimizing performance.
*   **Assume a Simple Key-Value Store:** For persistence, you can assume a simple key-value store interface. It should support `get(key: String): Integer` and `put(key: String, value: Integer)`. You can mock this for testing purposes, but you should describe how you would use a real distributed key-value store like Redis or Cassandra.

**Considerations (Trade-offs):**

*   **Data Consistency vs. Availability:** In a distributed system, strong consistency can impact performance.  Consider the trade-offs between consistency and availability when designing your persistence and synchronization strategy. Explore eventual consistency.
*   **Memory Usage:** Efficiently manage memory usage, especially when dealing with a large number of clients.
*   **Synchronization Overhead:** Minimize synchronization overhead between rate limiter instances to avoid performance bottlenecks.
*   **Rate Limit Update Propagation:** How quickly are rate limit changes propagated across the distributed instances?

**Bonus Challenges:**

*   Implement different rate limiting algorithms, such as token bucket or leaky bucket.
*   Add support for rate limiting based on different criteria (e.g., IP address, user role).
*   Implement metrics and monitoring to track the performance of the rate limiter.

This problem requires a careful consideration of distributed systems principles, data structures, and algorithms. You'll need to demonstrate your ability to design a scalable, reliable, and efficient rate limiting solution. Good luck!
