## Project Name

```
distributed-rate-limiter
```

## Question Description

Design and implement a distributed rate limiter in Go.

**Scenario:** You are building a high-traffic API gateway that needs to protect its backend services from being overwhelmed. You need to implement a rate limiter that can:

*   Limit the number of requests from a given user (identified by a unique user ID) within a specific time window.
*   Operate correctly even when the API gateway is deployed across multiple servers (distributed environment).
*   Handle a large number of concurrent requests efficiently.

**Requirements:**

1.  **Rate Limiting Logic:** The rate limiter should enforce a limit of `N` requests per user within a time window of `T` seconds.  If a user exceeds this limit, subsequent requests within the time window should be rejected.

2.  **Distributed Operation:** The rate limiter must work correctly when deployed across multiple servers.  This means that the request counts for each user must be shared and synchronized across all servers.

3.  **Concurrency:** The rate limiter must be thread-safe and handle a high volume of concurrent requests without data races or performance bottlenecks.

4.  **Persistence:** Request counts should be persisted to Redis, allowing the rate limiter to maintain state across server restarts. Use Redis for both persisting the state and implementing the distributed locking. Assume that the key expiration feature in Redis is available.

5.  **Optimization:**  Optimize for both memory usage and request processing latency. Consider different data structures and algorithms to achieve the best performance.  Avoid unnecessary network calls to Redis.

6.  **Edge Cases and Constraints:**
    *   Handle cases where the Redis server is temporarily unavailable.
    *   Ensure that the rate limiter remains functional even if some servers in the distributed environment fail.
    *   Consider the potential for clock skew between servers in the distributed environment.
    *   Assume user IDs are strings.
    *   Assume N and T are positive integers.

7.  **API:** Implement the following function:

    ```go
    // AllowRequest checks if a request from the given user ID should be allowed.
    // It returns true if the request is allowed, false otherwise.
    // It also returns an error if there was a problem communicating with Redis.
    func AllowRequest(userID string, N int, T int) (bool, error)
    ```

8.  **Testing:** Provide thorough unit tests to demonstrate the correctness and performance of your rate limiter.  Include tests for:
    *   Single-server rate limiting.
    *   Distributed rate limiting across multiple simulated servers.
    *   Concurrency.
    *   Redis failure scenarios.
    *   Edge cases (e.g., invalid user IDs, zero rate limits).

9.  **Bonus:** Implement a mechanism to prevent race conditions during the incrementing of the request count. Use Redis's atomic operations (e.g., `INCR` with `EXPIRE`) to achieve this.

10. **Error Handling:** Implement robust error handling. Return meaningful errors when something goes wrong (e.g., Redis connection errors).

**Constraints:**

*   You must use the Go programming language.
*   You must use Redis as the persistence layer.
*   You can use any necessary Go libraries, but minimize external dependencies.
*   Strive for clean, well-documented, and maintainable code.
*   Assume that the Redis server is already running and accessible.

This problem challenges the solver to combine knowledge of distributed systems, concurrency, data structures, and Redis to build a robust and performant rate limiter.  The edge cases and optimization requirements add to the difficulty, making it a suitable problem for a high-level programming competition.
