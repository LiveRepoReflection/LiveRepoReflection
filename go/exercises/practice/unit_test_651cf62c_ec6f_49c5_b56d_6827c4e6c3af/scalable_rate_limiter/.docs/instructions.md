## Question: Scalable Rate Limiter

**Problem Statement:**

Design and implement a scalable rate limiter in Go. The rate limiter should control the number of requests a client can make to a service within a given time window.

**Detailed Requirements:**

1.  **Basic Functionality:** Implement a rate limiter that allows a configurable number of requests (the `limit`) within a specific duration (the `window`). If a client exceeds the limit, subsequent requests should be rejected until the window resets.

2.  **Concurrency:** The rate limiter must be thread-safe and handle concurrent requests efficiently.  Multiple goroutines should be able to access and update the rate limiter without data races or performance bottlenecks.

3.  **Scalability:** The rate limiter should scale horizontally to handle a large number of clients.  Consider how your design could be distributed across multiple servers or instances.

4.  **Client Identification:** The rate limiter must be able to identify clients uniquely (e.g., by IP address, user ID, or API key).  The rate limiting should be applied on a per-client basis.

5.  **Configurable Limit and Window:** The `limit` (maximum number of requests) and `window` (duration in seconds) should be configurable at runtime, preferably without requiring a restart of the service.

6.  **Granularity:** Implement the rate limiter in such a way that `limit` can be set differently for different endpoints (API).

7.  **Data Storage:** You can either use in-memory data structures or external databases (Redis, Memcached) based on the requirements. The choice of data store should be justified based on the expected scale and persistence requirements. If using an external datastore, provide clear instructions on how to set it up.

8.  **Efficiency:**  The rate limiter should have minimal impact on the overall performance of the service. Strive for O(1) or O(log n) complexity for the rate limiting logic, where n is number of clients.

9.  **Edge Cases:**  Consider edge cases such as:

    *   Clock skew across multiple servers.
    *   Clients sending a burst of requests at the end of a window.
    *   How to handle requests when the rate limiter is temporarily unavailable (e.g., due to a database outage).
    *   Integer overflows when counting requests.

10. **Extensibility:** The rate limiter should be designed in a way that allows for easy extension to support more advanced features in the future.

**Constraints:**

*   The solution must be written in Go.
*   The solution must be well-documented, with clear explanations of the design choices and trade-offs.
*   The solution must include unit tests to verify the correctness of the rate limiting logic.
*   Explain your choice of data structure.
*   Assume a high volume of requests (millions per second) from a large number of clients (millions).
*   You are not allowed to use external rate limiting libraries (e.g., `golang.org/x/time/rate`).
*   Assume that you can use at most `4GB` of memory.

**Bonus (Optional):**

*   Implement a tiered rate limiting system where different clients have different limits based on their subscription level.
*   Implement a mechanism for dynamically adjusting the rate limits based on the overall load on the service.
*   Add metrics and monitoring capabilities to track the rate limiter's performance and effectiveness.
*   Implement request queuing for requests exceeding the rate limit, with configurable queue size and timeout.
