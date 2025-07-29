## Project Name

`distributed-rate-limiter`

## Question Description

You are tasked with designing and implementing a distributed rate limiter in Go. This rate limiter must handle a high volume of requests across multiple servers and ensure that no single user or service exceeds a predefined request limit within a given time window.

**Scenario:**

Imagine you are building a popular API service. To protect your infrastructure from abuse and ensure fair usage, you need to implement a rate limiter. This rate limiter should:

*   **Identify Clients:** Uniquely identify clients making requests (e.g., using an API key, user ID, or IP address).
*   **Enforce Limits:** Enforce a limit on the number of requests a client can make within a specific time window (e.g., 100 requests per minute).
*   **Be Distributed:** Work correctly across multiple servers handling API requests. This means that the rate limiter state (request counts, timestamps) must be shared or coordinated across these servers.
*   **Be Highly Concurrent:** Handle a large number of concurrent requests efficiently.
*   **Be Resilient:** Tolerate server failures gracefully.
*   **Be Efficient:** Minimize latency and resource consumption.

**Requirements:**

1.  **Implement a `RateLimiter` interface with the following methods:**

    ```go
    type RateLimiter interface {
        Allow(clientID string) bool // Returns true if the client is allowed to make the request, false otherwise.
    }
    ```

2.  **Implement a distributed rate limiter using a suitable algorithm and data structure.**  You should consider the trade-offs between accuracy, efficiency, and complexity when choosing your approach. Some possible options include:
    *   **Redis-based:** Use Redis as a central store to track request counts and timestamps.
    *   **Token Bucket Algorithm:** Implement a distributed token bucket algorithm.
    *   **Leaky Bucket Algorithm:** Implement a distributed leaky bucket algorithm.
    *   **Fixed Window Counter:** Use a fixed window counter with some mechanism for synchronization/approximation across servers.
    *   **Sliding Window Log:** Maintain a log of request timestamps.
    *   **Sliding Window Counter:** Combine counters with interpolation.
3.  **Configuration:** The rate limiter should be configurable with the following parameters:

    *   `Limit`: The maximum number of requests allowed within the time window.
    *   `Window`: The time window in seconds.
    *   `RedisAddress` (if using Redis): The address of the Redis server.
4.  **Concurrency:** Ensure your implementation is thread-safe and can handle concurrent requests.
5.  **Error Handling:** Implement appropriate error handling, especially when interacting with external services like Redis.
6.  **Scalability:** Design your solution with scalability in mind.  Consider how your solution would perform with a large number of clients and servers.
7.  **Efficiency:** Strive for an efficient implementation that minimizes latency and resource consumption.
8.  **Resilience:** Consider the impact of server failures and design your rate limiter to be as resilient as possible. For example, if using Redis, consider using a Redis cluster for high availability.

**Constraints:**

*   You must use Go for your implementation.
*   You can use external libraries (e.g., for Redis interaction) but avoid using pre-built rate limiting libraries.  The goal is to demonstrate your understanding of rate limiting algorithms and distributed systems concepts.
*   Your solution should be well-documented and easy to understand.
*   Focus on correctness, efficiency, and scalability.

**Bonus (Optional):**

*   Implement a mechanism to dynamically update the rate limit configuration without restarting the service.
*   Implement metrics and monitoring to track the performance of the rate limiter (e.g., request rate, rejected requests, latency).
*   Provide a simple load testing script to demonstrate the performance of your rate limiter.

This problem requires a deep understanding of concurrency, distributed systems, and rate limiting algorithms. The numerous design choices and trade-offs will challenge even experienced Go developers. Good luck!
