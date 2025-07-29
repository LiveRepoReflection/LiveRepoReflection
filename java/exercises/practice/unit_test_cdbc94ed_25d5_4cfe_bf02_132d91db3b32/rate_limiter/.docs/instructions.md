## Project Name

```
distributed-rate-limiter
```

## Question Description

Design and implement a distributed rate limiter. This rate limiter will be used to protect a set of backend services from being overwhelmed by excessive requests. The system must meet the following requirements:

*   **Functionality:** The rate limiter must allow a configurable number of requests from a specific client (identified by a unique client ID) within a given time window. If a client exceeds its allowed request limit, further requests within that time window should be rejected.

*   **Distributed Operation:** The rate limiter must be able to operate across multiple instances (servers) to handle a high volume of requests. The state (request counts) for each client should be synchronized across these instances.

*   **Configurable Limits:** The rate limit (number of requests allowed per time window) and the time window duration must be configurable and adjustable at runtime, ideally without service interruption. These configurations should be specific to individual clients.

*   **Concurrency:** The rate limiter must handle concurrent requests from multiple clients efficiently.

*   **Persistence:** The rate limiter must persist the state of the request counts to avoid losing data in case of server restarts or failures. Choose a suitable persistent storage mechanism that supports atomic operations.

*   **Fault Tolerance:** The system should be designed to tolerate node failures. Consider how the data is replicated and how a new node can join the cluster and synchronize its state.

*   **Efficiency:** The solution should strive for low latency and high throughput. Minimize the overhead of rate limiting to avoid impacting the performance of the backend services.
*   **Scalability:** Consider how the system could scale to handle a very large number of clients and requests.

**Specific Requirements:**

1.  **Client Identification:** Assume each request includes a unique `client_id` string for identification.

2.  **Configuration:** The configuration (rate limit, time window duration) should be retrievable via a provided `ConfigurationService` (assume this service exists and is accessible). The service returns a `RateLimitConfiguration` object for a given `client_id`.

3.  **Storage:** Choose a suitable distributed data store for persisting request counts. Consider the trade-offs between consistency, availability, and performance. Justify your choice. Redis with Lua scripting is a strong possibility due to its speed and atomicity, but other solutions such as Cassandra or ZooKeeper could also work depending on the scale and consistency requirements.

4.  **Implementation:** Your implementation should include a `RateLimiter` class with a method `allowRequest(String client_id)` that returns a boolean: `true` if the request is allowed, `false` if the request is rejected.

5.  **Concurrency:** Ensure that your `RateLimiter` class is thread-safe.

6.  **Edge Cases:** Handle edge cases such as:

    *   Client ID not found in the `ConfigurationService`.
    *   Time windows that span multiple time units (e.g., a 5-minute window).
    *   Clock skew between different servers.

**Bonus (Optional):**

*   Implement a mechanism for dynamically adjusting the rate limits without restarting the rate limiter instances.
*   Implement circuit breaker functionality for backend services that are consistently being rate-limited.
*   Provide metrics for monitoring the rate limiter's performance (e.g., request throughput, rejection rate, latency).

This problem requires careful consideration of distributed systems concepts, data structures, and concurrency. The solution should be well-reasoned, documented, and optimized for performance. Good luck!
