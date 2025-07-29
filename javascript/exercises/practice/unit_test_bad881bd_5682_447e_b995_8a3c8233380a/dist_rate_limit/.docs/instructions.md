## Question: Distributed Rate Limiter

### Question Description:

You are tasked with designing and implementing a distributed rate limiter in Javascript. This rate limiter needs to be highly scalable and resilient to failures. It will be used to protect a critical API endpoint from abuse.

**Specifics:**

Imagine you are building a system to protect a popular API endpoint. This endpoint is called frequently by many different clients, and you need to prevent any single client from overwhelming the system. You must implement a distributed rate limiter with the following constraints:

1.  **Global Rate Limiting:** The rate limiter should enforce a global limit on the number of requests a client can make within a given time window, regardless of which server in the distributed system handles the request.

2.  **Client Identification:** Clients are identified by a unique `clientId` (string).

3.  **Configurable Rate Limits:** The rate limit should be configurable, specified as a maximum number of requests (`maxRequests`) per time window (`timeWindowMs`).

4.  **Distributed Operation:** The rate limiter must function correctly across multiple servers in a distributed environment.  Assume you have access to a distributed cache (like Redis) for shared state. You need to implement the logic to leverage this distributed cache.

5.  **Atomic Operations:** Use atomic operations within the distributed cache to ensure data consistency and prevent race conditions. Avoid naive increment/decrement patterns which are prone to failure.

6.  **Time Window Accuracy:** The time window should be as accurate as possible, without adding excessive overhead. Consider the trade-offs between perfect accuracy and performance.

7.  **Scalability:** The rate limiter should be designed to handle a large number of clients and a high volume of requests.

8.  **Resilience:** The rate limiter should be resilient to failures in the distributed cache. Implement a fallback mechanism (e.g., local in-memory rate limiting with a more lenient limit) in case the cache is unavailable. When the cache is available again, it should resume with correct rate limiting.

9.  **Efficient Memory Usage:** Be mindful of memory usage, especially when dealing with a large number of clients. Implement a mechanism to expire client rate limit data after a period of inactivity.

10. **Asynchronous Implementation:** The rate limiter should be implemented using asynchronous JavaScript (async/await) to avoid blocking the main thread.

**API:**

You need to implement a class named `DistributedRateLimiter` with the following method:

```javascript
/**
 * Checks if a client is allowed to make a request.
 * @param {string} clientId The unique identifier of the client.
 * @returns {Promise<boolean>} A promise that resolves to true if the client is allowed, false otherwise.
 */
async isAllowed(clientId) { ... }
```

**Constructor:**

The `DistributedRateLimiter` constructor should accept the following parameters:

```javascript
/**
 * @param {object} options
 * @param {number} options.maxRequests The maximum number of requests allowed within the time window.
 * @param {number} options.timeWindowMs The length of the time window in milliseconds.
 * @param {object} options.cacheClient An object representing the distributed cache client (e.g., a Redis client).  It should have `get`, `set`, and atomic increment/decrement functions (see below).
 * @param {number} [options.fallbackMaxRequests] Optional: The maximum number of requests allowed in the fallback mechanism. Defaults to a reasonable value.
 * @param {number} [options.fallbackTimeWindowMs] Optional: The length of the fallback time window in milliseconds. Defaults to a reasonable value.
 */
constructor(options) { ... }
```

**Cache Client Requirements:**

The `cacheClient` object passed to the constructor should implement the following asynchronous methods:

*   `get(key)`:  Retrieves the value associated with the given key. Returns `null` if the key does not exist.
*   `set(key, value, expiryMs)`: Sets the value associated with the given key, with an optional expiry time in milliseconds.
*   `incrementAndGet(key, expiryMs)`: Atomically increments the integer value stored at key and returns the new value. If the key does not exist, it is initialized to 1. Sets the expiry time in milliseconds.
*   `decrementAndGet(key)`: Atomically decrements the integer value stored at key and returns the new value.

**Constraints:**

*   Your solution must be implemented in JavaScript using async/await.
*   You should strive for optimal performance and minimal overhead.
*   Handle potential errors and edge cases gracefully.
*   Consider thread safety implications when updating shared state, especially in the fallback mechanism.
*   Assume the distributed cache is the single source of truth, but implement the fallback to ensure availability.
*   Clients can make requests at any time.

This problem requires a deep understanding of distributed systems, caching strategies, and concurrency. Good luck!
