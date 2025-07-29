## Project Name

```
distributed-rate-limiter
```

## Question Description

Design and implement a distributed rate limiter in Javascript. This rate limiter should be able to handle a high volume of requests across multiple servers and prevent abuse of an API.

**Scenario:**

Imagine you are building a popular API that is accessed by numerous clients. To protect your infrastructure from overload and prevent abuse, you need to implement a rate limiter. A single-server rate limiter is insufficient due to the distributed nature of your application. Therefore, you need a distributed rate limiter.

**Requirements:**

1.  **Functionality:** Implement a `isAllowed(clientId, action, limit, timeWindow)` function that determines whether a given client is allowed to perform a specific action based on the defined rate limit.

    *   `clientId`: A unique identifier for the client making the request (e.g., API key, user ID).
    *   `action`: The specific action the client is attempting to perform (e.g., "create_post", "download_report").
    *   `limit`: The maximum number of times the client can perform the action within the specified time window.
    *   `timeWindow`: The time window (in seconds) during which the `limit` applies.

    The function should return `true` if the client is allowed to perform the action; otherwise, it should return `false`.

2.  **Distributed Implementation:** The rate limiter must be able to function correctly across multiple independent servers. This implies that the state (request counts) needs to be shared and synchronized across these servers. Consider using an external data store (e.g., Redis, Memcached, a distributed key-value store) to persist this state.

3.  **Atomic Operations:**  Ensure that all operations related to incrementing request counts and checking limits are atomic to prevent race conditions and ensure data consistency. The system should be thread-safe.

4.  **Efficiency:**  The rate limiter should be highly efficient, minimizing latency for request processing. Aim for O(1) or O(log n) time complexity for the `isAllowed` function, where n is the number of clients.

5.  **Scalability:** The system should be designed to handle a large number of clients and requests per second.  Consider sharding or partitioning strategies if necessary.

6.  **Time-Based Expiry:** Implement a mechanism to automatically expire the request counts for each client/action combination after the `timeWindow` has passed. This prevents the data store from growing indefinitely.

7.  **Edge Cases & Constraints:**

    *   Handle cases where the `clientId` or `action` is invalid or not present.
    *   Ensure that the `limit` and `timeWindow` values are valid positive integers.
    *   Consider the potential for clock skew across different servers.
    *   Minimize the impact of data store failures on the rate limiter's availability.  Think about graceful degradation (e.g., temporarily disabling rate limiting in extreme cases).

8. **Optimization:**
    * Optimize the usage of external datastore (e.g. Redis).
    * Minimize the number of calls to external datastore.

**Considerations:**

*   Choose a suitable data structure in your chosen data store to efficiently store and retrieve request counts (e.g., sorted sets, hashes).
*   Explore different rate limiting algorithms (e.g., token bucket, leaky bucket, fixed window counter, sliding window log, sliding window counter) and choose the most appropriate one for the given requirements. Justify your choice.
*   Address how to handle potential issues with clock synchronization across servers.
*   Consider the trade-offs between accuracy and performance. Is it acceptable to allow a small number of requests over the limit in rare cases to improve performance?
*   Think about how to monitor and alert on rate limiting events (e.g., exceeding limits, data store failures).
*   Assume you have access to a suitable external data store client library for Javascript (e.g., `ioredis` for Redis). You don't need to implement the data store integration from scratch.

This problem requires a solid understanding of distributed systems, concurrency, data structures, and algorithms.  A well-designed solution will be efficient, scalable, and robust. Good luck!
