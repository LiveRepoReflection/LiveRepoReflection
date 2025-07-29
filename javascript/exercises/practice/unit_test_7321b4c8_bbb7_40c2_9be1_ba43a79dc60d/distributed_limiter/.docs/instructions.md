Okay, here's a challenging and sophisticated Javascript coding problem designed to be LeetCode Hard difficulty.

## Question: Distributed Rate Limiter

### Question Description

You are tasked with designing and implementing a distributed rate limiter. This rate limiter should control the number of requests a user can make to a system within a given time window, even when the system is scaled across multiple servers.

Specifically, you need to implement the following functionalities:

1.  **`isAllowed(userId, apiEndpoint, timestamp)`:**  This function should determine whether a given user is allowed to make a request to a specific API endpoint at a given timestamp.  It should return `true` if the request is allowed and `false` otherwise.

2.  **Rate Limit Configuration:** The rate limits should be configurable. You should be able to define different rate limits for different API endpoints and/or different user segments.  For example:
    *   User A can make 10 requests per minute to API endpoint `/users`.
    *   User B can make 5 requests per minute to API endpoint `/users`.
    *   All users can make 100 requests per hour to API endpoint `/products`.

3.  **Distributed Operation:**  The rate limiter must function correctly across multiple server instances.  This implies that you need to consider data consistency and synchronization across these instances.

4.  **Concurrency:** The rate limiter must handle concurrent requests efficiently.

5.  **Persistence:** The rate limiter state (e.g., request counts) should be persistent.  If a server restarts, the rate limiting should continue to function correctly based on the historical request data.

6.  **Scalability:** The rate limiter should be designed to handle a large number of users and API endpoints efficiently.

7.  **Fault Tolerance:** The rate limiter should be resilient to failures of individual server instances.

**Constraints:**

*   You can use external libraries or services to assist in the implementation, but you must justify your choices and explain how they contribute to meeting the requirements.  Consider options like Redis, Memcached, or a distributed database.
*   Focus on correctness, efficiency, and scalability.  Your solution should be able to handle a large volume of requests with minimal latency.
*   Assume the `timestamp` is provided in milliseconds since the Unix epoch.
*   Rate limits are defined per user and API endpoint combination.
*   Assume the system has access to a configuration service that provides the rate limits for each user and API endpoint combination. You do not need to implement the configuration service itself, but you should design your rate limiter to be compatible with such a service. You can assume a function `getRateLimit(userId, apiEndpoint)` exists that returns an object `{limit: number, window: number}` where `limit` is the maximum number of requests allowed and `window` is the time window in milliseconds. If no specific rate limit is defined it should return a default `{limit: 60, window: 60000}` (60 requests per minute).
*   Consider the trade-offs between different data structures and algorithms for storing and retrieving request counts.
*   The solution should be stateless as possible to scale horizontally.

**Example:**

```javascript
// Assume getRateLimit(userId, apiEndpoint) is a function provided by the config service.

// Example Usage:
const rateLimiter = new DistributedRateLimiter();

let userId = "user123";
let apiEndpoint = "/users";
let timestamp = Date.now();

let allowed = await rateLimiter.isAllowed(userId, apiEndpoint, timestamp); // Returns true/false
console.log(`Request for ${userId} to ${apiEndpoint} at ${timestamp} is allowed: ${allowed}`);

// ... subsequent calls to isAllowed()
```

This problem requires a deep understanding of distributed systems, concurrency, and data persistence.  It encourages the use of appropriate data structures and algorithms for efficient rate limiting and invites exploration of different architectural patterns for building a scalable and fault-tolerant system. Good luck!
