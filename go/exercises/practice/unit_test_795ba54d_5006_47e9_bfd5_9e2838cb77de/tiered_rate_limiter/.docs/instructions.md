## Question: Distributed Rate Limiter with Tiered Buckets

### Question Description

Design and implement a distributed rate limiter service in Go. This service should be able to handle a high volume of requests and prevent abuse of a system by limiting the number of requests a user can make within a specific time window. The rate limiter must support tiered rate limits based on user tiers.

**Core Requirements:**

1.  **Distributed Operation:** The rate limiter must be designed to operate in a distributed environment, capable of handling requests from multiple servers/processes. Think about race conditions and data consistency.

2.  **Tiered Rate Limits:**  Implement three tiers of users: `Free`, `Standard`, and `Premium`. Each tier has different rate limits:

    *   `Free`: 5 requests per minute.
    *   `Standard`: 20 requests per minute.
    *   `Premium`: 100 requests per minute.

3.  **Sliding Window:** Implement a sliding window rate limiting algorithm.  The rate limit should be enforced over a rolling minute, not a fixed one.

4.  **Atomic Operations:** Utilize atomic operations to ensure thread safety and prevent race conditions, especially when incrementing request counts.

5.  **Efficient Storage:** Choose an appropriate data structure and storage mechanism (e.g., in-memory cache with Redis as a persistence layer) for storing request counts and timestamps. Consider memory usage and lookup speed.

6.  **Concurrency:** Handle concurrent requests efficiently using goroutines and channels.

**Input:**

The rate limiter service will receive requests that include:

*   `userID` (string): A unique identifier for the user making the request.
*   `tier` (string): User's tier (`Free`, `Standard`, `Premium`).

**Output:**

The service should return a boolean value:

*   `true`:  If the request is allowed (within the rate limit).
*   `false`: If the request is rejected (rate limit exceeded).

**Constraints:**

*   **High Throughput:** The rate limiter should be able to handle a high volume of requests with minimal latency.
*   **Scalability:** The design should be scalable to accommodate a growing number of users and requests.
*   **Fault Tolerance:** The system should be resilient to failures.
*   **Memory Limit:**  Assume a constrained memory environment. Avoid storing unnecessary data or letting memory usage grow unbounded.
*   **Time Complexity:**  The `Allow()` operation (checking if a request is allowed) should have a time complexity of O(log n) or better, where n is the number of requests in the sliding window, or O(1) if using a different efficient algorithm.

**Bonus Challenges:**

*   Implement dynamic tier updates (changing a user's tier on the fly).
*   Add support for different rate limiting periods (e.g., per second, per hour, per day).
*   Implement circuit breaker pattern to prevent cascading failures if the storage layer (e.g., Redis) becomes unavailable.
*   Implement metrics collection and monitoring to track the rate limiter's performance (e.g., requests per second, rejection rate).
*   Implement request queue to provide eventual consistency.
