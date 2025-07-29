## Problem: Distributed Rate Limiter with Dynamic Throttling

### Question Description

Design and implement a distributed rate limiter service in Go that enforces rate limits across multiple instances of an application. The service must support dynamic throttling, allowing rate limits to be adjusted in real-time based on system load and other factors.

**Core Functionality:**

Your rate limiter service should provide the following functionality:

1.  **`Allow(clientID string, requestCost int) bool`:** This function determines whether a client, identified by `clientID`, is allowed to make a request.  `requestCost` represents the "cost" of the request.  A client's accumulated request cost within a time window must not exceed its assigned rate limit.  The function should return `true` if the request is allowed and `false` otherwise. If allowed, the accumulated cost should be updated atomically.

2.  **`SetRateLimit(clientID string, limit int, window int) error`:**  This function sets the rate limit for a specific client.  `limit` defines the maximum accumulated request cost allowed within a `window` specified in seconds. The rate limit should be applied immediately to all subsequent requests from the client.  Return an error if `limit` or `window` are invalid (e.g., negative or zero).

3.  **`GetRateLimit(clientID string) (limit int, window int, error error)`:** This function retrieves the current rate limit and window size for a given client. If the client has no rate limit assigned, return a default rate limit with the limit being 0 and the window being 0.

**Constraints and Requirements:**

*   **Distributed Operation:**  The rate limiter must be designed to function correctly across multiple instances of the service. Client rate limit data must be consistent regardless of which instance handles a request. Consider using a distributed cache or database (e.g., Redis, Cassandra, etcd) for storing rate limit information. You can use the local memory if you can ensure the rate limit can be consistent across different instances.
*   **Concurrency:** The `Allow` and `SetRateLimit` functions must be thread-safe and handle concurrent requests efficiently.
*   **Dynamic Throttling:** The rate limits should be adjustable in real-time without service interruption.  Changes to rate limits should be propagated quickly to all instances.
*   **Optimized Performance:** The `Allow` function must have minimal latency. Aim for an average latency of under 1ms, even under high load.
*   **Scalability:**  The service should be designed to handle a large number of clients (millions) and a high request rate (thousands of requests per second).
*   **Fault Tolerance:**  The service should be resilient to failures of individual instances.
*   **Edge Cases:**
    *   Handle cases where the `clientID` is empty or invalid.
    *   Handle cases where the `requestCost` is zero or negative.
    *   Handle integer overflow when calculating accumulated request cost.
    *   Consider what happens when the distributed cache/database is temporarily unavailable.

**Considerations:**

*   **Data Structures:** Choose appropriate data structures for storing rate limit information and managing request counts. Consider trade-offs between memory usage and performance.
*   **Algorithms:** Select efficient algorithms for determining whether a request should be allowed. Common techniques include token bucket, leaky bucket, and fixed window counters.
*   **Error Handling:** Implement robust error handling and logging.
*   **Testing:** Write thorough unit tests and integration tests to ensure the correctness and performance of the service.

**Bonus Challenges:**

*   Implement a mechanism for automatically adjusting rate limits based on system load.
*   Add support for different rate limiting algorithms (e.g., token bucket, leaky bucket).
*   Provide metrics and monitoring capabilities (e.g., request rate, latency, error rate).
*   Implement a graceful degradation strategy in case the distributed cache/database becomes unavailable.

This problem requires a strong understanding of concurrency, distributed systems, data structures, and algorithms. The emphasis is on designing a robust, scalable, and high-performance rate limiter service. Good luck!
