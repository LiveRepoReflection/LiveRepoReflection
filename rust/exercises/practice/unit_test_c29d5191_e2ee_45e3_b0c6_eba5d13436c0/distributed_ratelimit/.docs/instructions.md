## Project Name

**Distributed Rate Limiter**

## Question Description

Design and implement a distributed rate limiter in Rust. The rate limiter should control the rate at which clients can access a shared resource. The system consists of multiple rate limiter instances distributed across different servers and a central data store (e.g., Redis) to maintain a global view of request counts.

**Functionality:**

*   **`is_allowed(client_id: &str, api_endpoint: &str, capacity: usize, rate_per_second: usize) -> bool`:** This function is the core of the rate limiter. It determines whether a client, identified by `client_id`, is allowed to access a specific `api_endpoint`.
    *   `client_id`: A unique identifier for the client making the request (e.g., a user ID or API key).
    *   `api_endpoint`: The specific API endpoint being accessed (e.g., "/users", "/products").
    *   `capacity`: The maximum number of requests allowed from a single client_id on a single API end point.
    *   `rate_per_second`: The number of requests each client is allowed to make per second.

*   The function should return `true` if the client is allowed to make the request and `false` otherwise.

**Requirements & Constraints:**

1.  **Distributed Consensus:** Ensure that the rate limiting is consistent across all rate limiter instances.  Use the central data store to coordinate request counts.

2.  **Atomic Operations:**  Use atomic operations (e.g., Redis's `INCR` with expiration) to prevent race conditions when updating request counts in the central data store.

3.  **Time-Based Rate Limiting:** Implement rate limiting based on a sliding window of one second. This means that the rate limit should be enforced based on the number of requests made in the last second.

4.  **Granularity:** The rate limiter should be able to apply rate limits to specific API endpoints on a per-client basis.

5.  **Fault Tolerance:** Consider the case where a rate limiter instance might fail. The system should continue to function correctly with the remaining instances.

6.  **Efficiency:** Optimize the implementation for speed and minimize latency.  Accessing the central data store should be as efficient as possible.

7.  **Scalability:**  Design the system to be scalable horizontally. Adding more rate limiter instances should increase the system's capacity to handle requests.

8.  **Central Data Store:** You can assume the existence of a Redis client.  You do not need to implement Redis itself or a mock.  You can use a suitable Redis crate (e.g., `redis`) for your implementation.

9.  **Error Handling:** Implement proper error handling and logging.  The `is_allowed` function should return an appropriate error if it encounters any issues (e.g., connection errors to the central data store).

10. **Contention:** The central data store will be under a lot of contention. Ensure that the data structure and operations in your solution are as efficient as possible.

11. **Expiration:** Keys in the central data store must have an expiry of 2 seconds (or slightly more than the rate limit window) to handle edge cases where a client might send requests close to the end of a second.

**Edge Cases to Consider:**

*   Client making requests at the exact boundary of the rate limit window.
*   Central data store being temporarily unavailable.
*   Multiple rate limiter instances receiving requests from the same client concurrently.
*   The rate limit is extremely low/high and the contention on Redis is very high.

**Bonus:**

*   Implement a mechanism to dynamically update the rate limit parameters (e.g., `rate_per_second`) without restarting the rate limiter instances.
*   Add support for different rate limiting algorithms (e.g., token bucket, leaky bucket).
*   Consider using a more sophisticated data structure in Redis (e.g., sorted sets) for more efficient sliding window implementation.

This problem requires a good understanding of distributed systems, concurrency, data structures, and optimization techniques. Good luck!
