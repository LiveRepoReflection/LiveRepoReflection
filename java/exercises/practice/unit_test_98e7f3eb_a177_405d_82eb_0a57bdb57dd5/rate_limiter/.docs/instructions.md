## Project Name

`Distributed Rate Limiter`

## Question Description

You are tasked with designing and implementing a distributed rate limiter. This rate limiter should control the number of requests that can be made to a particular resource by a specific user or client within a given time window, even when requests are being handled by multiple servers.

**Scenario:**

Imagine a popular online service with millions of users. To protect your backend infrastructure from abuse and ensure fair usage, you need to implement a rate limiting mechanism. This mechanism should prevent individual users from overwhelming the system with too many requests in a short period. Because the service is horizontally scaled across multiple servers, a simple in-memory rate limiter on each server won't be sufficient. You need a distributed solution.

**Requirements:**

1.  **Functionality:**
    *   Implement a method `allowRequest(userId, resourceId, limit, timeWindow)` that returns `true` if a request from `userId` to `resourceId` is allowed within the given `limit` and `timeWindow` (in seconds), and `false` otherwise.
    *   The rate limiter should accurately track requests across all servers.
    *   The rate limiter should be able to handle a large number of concurrent requests efficiently.

2.  **Data Structures:**
    *   Select appropriate data structures to store and manage request counts and timestamps in a distributed manner. You can use in-memory data structures (e.g., using Redis) or consider more persistent storage (e.g., using a database). Justify your choice.

3.  **Algorithm:**
    *   Implement a suitable rate-limiting algorithm. Consider algorithms like:
        *   **Token Bucket:** Each user has a bucket of tokens. Each request consumes a token. Tokens are replenished at a certain rate.
        *   **Leaky Bucket:** Requests enter a bucket, and the bucket leaks requests at a constant rate.
        *   **Fixed Window Counter:** Tracks the number of requests within a fixed time window.
        *   **Sliding Window Log:** Stores a timestamp for each request in a log.
        *   **Sliding Window Counter:** Combines the advantages of fixed window and sliding window log, by dividing time window into multiple slots and maintaining counters for each.

    *   Explain the advantages and disadvantages of your chosen algorithm in the context of a distributed system.

4.  **Concurrency:**
    *   Ensure thread safety and handle concurrent requests from multiple users without data corruption. Use appropriate synchronization mechanisms if necessary.

5.  **Scalability:**
    *   Design the rate limiter to be scalable to handle millions of users and high request rates. Consider sharding or partitioning the data across multiple nodes.

6.  **Fault Tolerance:**
    *   Consider the impact of server failures.  The system should remain functional, possibly with slightly degraded performance, even if one or more servers go down.

7.  **Optimization:**
    *   Minimize latency and resource consumption. Optimize data access patterns and algorithm efficiency.  Consider the trade-offs between accuracy and performance.
    *   Implement efficient eviction policies to manage storage space.

8.  **Edge Cases:**
    *   Handle invalid inputs gracefully (e.g., negative `limit` or `timeWindow`).
    *   Consider scenarios where the clock synchronization between servers is not perfect.

9. **Assumptions:**
    * You can assume a reasonable network latency.
    * You can use external libraries or frameworks for distributed caching, data storage, or concurrency management, but be sure to justify their use.

**Deliverables:**

1.  A clear and concise explanation of your chosen data structures, algorithm, and design choices.  Justify your decisions, especially regarding scalability, fault tolerance, and optimization.
2.  A Java implementation of the `DistributedRateLimiter` class with the `allowRequest` method. The code should be well-structured, documented, and easy to understand.
3.  A brief analysis of the time and space complexity of your implementation.
4.  A discussion of potential improvements or alternative approaches.

This problem requires you to demonstrate a strong understanding of distributed systems concepts, data structures, algorithms, and concurrency. Good luck!
