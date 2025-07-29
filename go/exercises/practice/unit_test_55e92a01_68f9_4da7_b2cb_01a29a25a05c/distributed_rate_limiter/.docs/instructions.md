## Question: Distributed Rate Limiter

### Question Description

Design and implement a distributed rate limiter. This rate limiter should control the number of requests allowed from individual users across a cluster of servers.

**Functionality:**

The rate limiter should expose a single function: `Allow(userID string, limit int, window time.Duration) bool`.

*   `userID`: A unique identifier for the user making the request.
*   `limit`: The maximum number of requests allowed within the specified time window.
*   `window`: The time duration in which the `limit` applies.
*   Returns `true` if the request is allowed (i.e., the user hasn't exceeded their rate limit), and `false` otherwise.

**Constraints and Requirements:**

1.  **Distributed Environment:** The rate limiter will be deployed across multiple servers.  The solution must ensure accurate rate limiting even with concurrent requests arriving at different servers for the same user.

2.  **Concurrency:** The rate limiter must handle concurrent requests efficiently.

3.  **Persistence:** The rate limiter needs to persist state across server restarts. You should use a durable storage solution (e.g., Redis, Cassandra, or a similar key-value store).  Consider the trade-offs of different storage options regarding latency, consistency, and scalability.

4.  **Time Accuracy:**  The accuracy of the time window is crucial. Consider potential clock drift between servers.

5.  **Scalability:** The system should be able to handle a large number of users and requests per second.  Think about horizontal scalability and potential bottlenecks.

6.  **Efficiency:** Minimize the latency of the `Allow` function.  Each request should be processed as quickly as possible.

7.  **Fault Tolerance:**  The rate limiter should be resilient to failures of individual servers or storage nodes.

8.  **Eviction Policy:** Design an efficient eviction policy for old or inactive users to prevent unbounded memory usage.

9.  **Optimizations:**  Explore various optimization techniques to improve performance, such as caching, batching, or probabilistic data structures (e.g., Bloom filters).  Clearly justify the choices made and discuss their trade-offs.

10. **Testing:** Consider how you would thoroughly test this system, focusing on concurrency, accuracy, and performance. What kinds of tests would you write?

11. **Edge Cases:** Consider potential edge cases like:

    *   Very short time windows (e.g., milliseconds).
    *   Extremely high request rates.
    *   Users with very long periods of inactivity followed by sudden bursts of requests.
    *   Server clock synchronization issues.

The solution should provide a clear explanation of the design choices, the data structures used, the algorithms implemented, and the reasoning behind the chosen trade-offs. Also, discuss how the system handles the constraints and requirements mentioned above.
