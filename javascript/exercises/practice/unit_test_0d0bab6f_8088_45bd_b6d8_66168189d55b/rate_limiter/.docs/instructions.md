## Project Name

`distributed-rate-limiter`

## Question Description

Design and implement a distributed rate limiter service. This service should be able to limit the number of requests that a user (identified by a unique user ID) can make to a specific API endpoint within a given time window. The system must be highly scalable, fault-tolerant, and efficient.

**Detailed Requirements:**

1.  **Rate Limiting Logic:** Implement a token bucket algorithm. Each user starts with a certain number of tokens (bucket capacity). Each request consumes one token. Tokens are refilled at a specific rate. If a user's token bucket is empty, the request is rejected.

2.  **Distributed Architecture:** The rate limiter must be distributed across multiple servers to handle high traffic volume and ensure availability. Consider using a distributed cache (e.g., Redis, Memcached) to store the token counts.

3.  **Scalability:** The system must be able to scale horizontally by adding more rate limiter instances. The rate limiting logic should remain consistent regardless of the number of instances.

4.  **Fault Tolerance:** The system should be resilient to server failures. If one rate limiter instance fails, the others should continue to operate correctly.

5.  **Concurrency:** The rate limiter must handle concurrent requests from multiple users efficiently without introducing race conditions or inconsistencies in the token counts.

6.  **Persistence (Optional but Recommended):** Consider persisting the token counts to a durable storage system (e.g., database) to handle restarts and prevent token loss.  If chosen, explain the consistency model you're employing.

7.  **API:**  Implement a simple API endpoint that accepts a user ID and API endpoint identifier as input and returns whether the request is allowed or rejected.

    ```
    function allowRequest(userId: string, endpoint: string): boolean
    ```

8.  **Configuration:** The following parameters should be configurable:

    *   Token bucket capacity (maximum number of tokens)
    *   Token refill rate (tokens per second)
    *   Time window (duration for rate limiting)
    *   Number of rate limiter instances
    *   Distributed cache connection details
    *   Persistence store connection details (if applicable)

**Constraints:**

*   **Strict Time Limit:** The `allowRequest` function must execute very quickly (sub-millisecond latency) to avoid impacting the performance of the protected APIs.
*   **Memory Limit:**  Each rate limiter instance has a limited amount of memory. Avoid storing large amounts of data in memory.
*   **Consistency:** The rate limiting logic must be as consistent as possible across all instances, even in the presence of network delays and server failures. Strive for eventual consistency, but consider strategies to mitigate inconsistencies in critical scenarios.
*   **Edge Cases:** Handle edge cases such as:
    *   Invalid user IDs or endpoint identifiers
    *   Requests arriving simultaneously from the same user.
    *   Clock skew between rate limiter instances.
    *   Distributed cache unavailability.

**Optimization Requirements:**

*   Minimize latency for the `allowRequest` function.
*   Minimize the load on the distributed cache and/or persistence layer.
*   Optimize the system for high throughput and low resource consumption.

**Multiple Valid Approaches:**

There are several valid approaches to solving this problem, each with different trade-offs. Consider different strategies for:

*   **Token storage:**  In-memory vs. distributed cache vs. persistent storage.
*   **Concurrency control:**  Locks, atomic operations, optimistic locking.
*   **Data partitioning:**  How to distribute user data across rate limiter instances.
*   **Communication between instances:**  Gossip protocol, consistent hashing, etc.
*   **Failure handling:**  How to handle distributed cache failures, server failures, and network partitions.
*   **Consistency Model**: Strive for eventual consistency, document why this model is chosen and how to mitigate its negative impact in specific scenarios.

**Bonus Challenges:**

*   Implement dynamic rate limiting policies based on factors such as user tier or API usage patterns.
*   Add monitoring and alerting to track the performance of the rate limiter.
*   Implement a mechanism to handle burst traffic spikes gracefully.
*   Consider implementing a circuit breaker pattern to prevent cascading failures.

This problem requires a good understanding of distributed systems, concurrency, and data structures. The goal is to design a practical and efficient rate limiter that can handle real-world traffic patterns. Good luck!
