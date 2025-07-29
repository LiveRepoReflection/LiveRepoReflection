## Project Name

`DistributedRateLimiter`

## Question Description

Design and implement a distributed rate limiter service. This service should limit the number of requests a user can make to a specific API within a given time window. The system must be scalable, fault-tolerant, and able to handle a large number of concurrent requests from numerous users across multiple servers.

**Specific Requirements:**

1.  **Rate Limiting Logic:** Implement a token bucket algorithm or a leaky bucket algorithm for rate limiting. You should allow for different rate limits per user and API endpoint.

2.  **Distributed Architecture:** The rate limiter must be distributed across multiple servers to handle high request volumes. Consider using a distributed cache (e.g., Redis, Memcached) or a distributed key-value store (e.g., etcd, Consul) to share rate limit information across servers. Ensure data consistency across all servers.

3.  **Concurrency:** Handle concurrent requests efficiently. Use appropriate synchronization mechanisms to prevent race conditions when updating the rate limit state.

4.  **Fault Tolerance:** Design the system to be fault-tolerant. If one or more rate limiter servers fail, the system should continue to operate correctly with minimal impact on performance. Consider replication and failover mechanisms.

5.  **Scalability:** The system should be able to scale horizontally to handle increasing request volumes. Consider sharding or consistent hashing to distribute the rate limit data across multiple servers.

6.  **API Definition:** Provide a simple API for clients to check if a request should be allowed or rate-limited. The API should accept the user ID, API endpoint, and request timestamp as input.

7.  **Configuration:** The rate limits (e.g., requests per minute, requests per hour) should be configurable without requiring code changes. Consider using a configuration file or a database to store the rate limit settings.

8.  **Real-time Updates:** Provide a mechanism to update the rate limits in real-time. This could involve a push-based system or a polling mechanism.

9. **Multiple Rate Limit Tiers:** Support different tiers of users with different rate limits. Tiers can be changed at runtime.

10. **Endpoint Prioritization:** Allow certain endpoints to be prioritized over others, so that in times of high load, these endpoints are less likely to be rate limited.

**Constraints:**

*   The system must be implemented in Java.
*   Minimize latency.
*   Optimize for memory usage.
*   Ensure data consistency in a distributed environment.
*   Assume a large number of users and API endpoints.

**Evaluation Criteria:**

*   Correctness: The rate limiter must accurately enforce the configured rate limits.
*   Performance: The system must handle a large number of concurrent requests with low latency.
*   Scalability: The system must be able to scale horizontally to handle increasing request volumes.
*   Fault Tolerance: The system must be fault-tolerant and continue to operate correctly even if some servers fail.
*   Code Quality: The code must be well-structured, readable, and maintainable.
*   Design: The system design must be appropriate for a distributed environment and meet the specified requirements.
*   Handling edge cases and boundary conditions. For example, consider what happens when the clock skews across distributed instances.
