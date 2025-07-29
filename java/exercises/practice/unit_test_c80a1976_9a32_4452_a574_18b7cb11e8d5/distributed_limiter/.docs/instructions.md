## Project Name

`DistributedRateLimiter`

## Question Description

Design and implement a distributed rate limiter in Java. This rate limiter should protect a critical resource (e.g., an API endpoint, a database) from being overwhelmed by excessive requests. It should be scalable, fault-tolerant, and efficient, especially when dealing with a high volume of requests across multiple servers.

**Requirements:**

1.  **Distributed:** The rate limiter must work across multiple servers/processes. Requests originating from any server should be subject to the same rate limit.
2.  **Configurable:** The rate limiter should allow configuration of:
    *   The resource being rate-limited (e.g., specified by a string key).
    *   The rate limit (e.g., X requests per Y seconds).
    *   Optionally, different rate limits for different clients or user groups.
3.  **Atomic:** The rate limiting logic must be atomic to prevent race conditions that could allow more requests than the limit.
4.  **Fault-Tolerant:** The rate limiter should continue to function correctly even if some servers or components fail.
5.  **Efficient:** The rate limiter should have low latency to avoid impacting the performance of the protected resource. The solution should be efficient for both common cases (request allowed) and less-frequent cases (request denied).
6.  **Scalable:** The system should scale horizontally to handle increasing request volumes.
7.  **Thread-safe:** The implementation must be thread-safe.
8.  **Expiration:** Expire old rate limit data to avoid memory exhaustion.
9.  **Time granularity:** The rate limiter must keep precise rate limits for the configured amount of time.

**Constraints:**

*   Assume you have access to a distributed key-value store (e.g., Redis, Memcached, or a similar system) that provides atomic operations (e.g., increment, get-and-set). You can abstract the interaction with this key-value store behind an interface.
*   Assume there are thousands of servers accessing the rate limiter.
*   Assume that requests arrive at a very high rate (millions of requests per minute).
*   Minimize the number of calls to the distributed key-value store for each request.
*   Consider different rate-limiting algorithms (e.g., Token Bucket, Leaky Bucket, Fixed Window, Sliding Window) and justify your choice.
*   Prioritize correctness, scalability, and performance.

**Specific Tasks:**

1.  **Design:** Describe your chosen rate-limiting algorithm and the data structures you will use in the distributed key-value store.
2.  **Implementation:** Provide Java code implementing the rate limiter, including:
    *   An interface for interacting with the distributed key-value store.
    *   An implementation of the rate limiter class with methods to configure the rate limit and check if a request is allowed.
    *   Appropriate error handling and logging.
3.  **Scalability Analysis:** Briefly explain how your design scales to handle increasing request volumes and the addition of more servers.
4.  **Trade-offs:** Discuss any trade-offs made in your design (e.g., memory usage vs. accuracy, latency vs. complexity).
5.  **Edge Cases:** Consider and handle edge cases such as:
    *   Clock skew between servers.
    *   Network latency.
    *   Key-value store failures.

**Bonus Challenges:**

*   Implement different rate limits for different clients or user groups.
*   Implement a circuit breaker pattern to prevent cascading failures if the key-value store becomes unavailable.
*   Implement metrics and monitoring to track the performance of the rate limiter.
*   Provide a basic simulation or test to demonstrate the correctness and performance of your rate limiter under high load.

This problem requires a good understanding of distributed systems, data structures, concurrency, and algorithm design. A well-reasoned solution with clear explanations and code will be highly regarded. Good luck!
