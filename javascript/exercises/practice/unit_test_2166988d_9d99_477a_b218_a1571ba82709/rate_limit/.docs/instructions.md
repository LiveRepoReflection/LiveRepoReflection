## Project Name

```
distributed-rate-limiter
```

## Question Description

You are tasked with designing and implementing a distributed rate limiter in JavaScript. This rate limiter will be used to protect a critical API endpoint from abuse by limiting the number of requests a user can make within a given time window.

**Requirements:**

1.  **Distributed Environment:** The rate limiter should function correctly even when deployed across multiple servers or processes. Assume a shared data store (e.g., Redis) is available for coordination.

2.  **Sliding Window Algorithm:** Implement a sliding window rate limiting algorithm. This means that the rate limit is based on the number of requests made within a rolling time window (e.g., 100 requests per minute), rather than fixed time intervals.

3.  **Granularity:** The rate limiter should be able to limit requests on a per-user basis, identified by a unique user ID.

4.  **Configuration:** The rate limiter should be configurable with the following parameters:

    *   `limit`: The maximum number of requests allowed within the time window.
    *   `window`: The length of the time window in milliseconds.
    *   `redisClient`: A Redis client instance for accessing the shared data store.

5.  **Concurrency:** The implementation must handle concurrent requests from multiple users and servers correctly.

6.  **Efficiency:** The implementation should be optimized for performance and minimize the number of Redis operations required for each request.  Consider trade-offs between accuracy and performance (e.g., approximate vs. exact counting).

7.  **Atomicity:** Ensure that the rate limiting logic is atomic to prevent race conditions when multiple servers are processing requests for the same user concurrently. Leverage Redis transactions or Lua scripting to achieve atomicity.

8.  **Error Handling:** Implement robust error handling to gracefully handle Redis connection errors or other unexpected issues.

9.  **Extendable:** The rate limiter should be designed in a way that it is easy to extend or modify in the future, for example, to support different rate limiting algorithms or data stores.

**API:**

Implement a class `RateLimiter` with the following API:

```javascript
class RateLimiter {
  constructor(options) {
    // options: { limit, window, redisClient }
  }

  async isAllowed(userId) {
    // Returns true if the request is allowed, false otherwise.
    // Should also update the rate limit state in Redis.
  }
}
```

**Constraints:**

*   The solution must be written in JavaScript.
*   The solution must be efficient and scalable.
*   The solution must be robust and handle errors gracefully.
*   Assume that the Redis client is already configured and connected.
*   Consider using a Redis Lua script to increment the counter and check the rate limit atomically.

**Bonus Challenges:**

*   Implement a mechanism to automatically expire old request timestamps from Redis to prevent unbounded memory growth.
*   Add support for burst allowance (e.g., allowing a user to exceed the rate limit by a small amount for a short period).
*   Implement a more sophisticated rate limiting algorithm, such as leaky bucket or token bucket.
*   Design the system to be resilient to Redis failures (e.g., by implementing a fallback mechanism).
*   Provide metrics and monitoring capabilities to track the rate limiter's performance.
