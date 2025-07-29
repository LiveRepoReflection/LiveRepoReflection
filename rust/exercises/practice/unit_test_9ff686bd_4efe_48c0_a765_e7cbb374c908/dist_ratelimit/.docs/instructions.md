## Project Name

`Distributed Rate Limiter`

## Question Description

Design and implement a distributed rate limiter service using Rust. This service should be able to limit the number of requests a client can make to a specific resource within a given time window. The rate limiter should be designed to handle a high volume of requests across multiple servers and clients concurrently, while maintaining accuracy and fairness.

**Specific Requirements:**

1.  **Distributed Operation:** The rate limiter must function correctly across multiple instances of the service. This implies that the state (e.g., request counts) needs to be shared and synchronized between instances.

2.  **Multiple Rate Limit Rules:** The rate limiter should support multiple rate limit rules, defined by resource ID and client ID. For example, client "A" can make 10 requests per minute to resource "X", while client "B" can make 5 requests per second to resource "Y".

3.  **Configurable Time Windows:** The time window for rate limits should be configurable (e.g., seconds, minutes, hours).

4.  **Atomic Operations:** All operations that modify the state of the rate limiter (e.g., incrementing request counts) must be atomic to prevent race conditions.

5.  **Efficient Data Structure:** You must choose an efficient data structure to store the rate limit information that allows for quick lookup and update.

6.  **Eviction Policy:** Implement an eviction policy to automatically remove rate limit rules that haven't been accessed for a certain period. This is to avoid unbounded memory usage.

7.  **Graceful Degradation:** In case of temporary failures (e.g., network issues, database unavailability), the rate limiter should degrade gracefully, possibly by temporarily allowing all requests or by falling back to a more lenient rate limit.

8.  **Concurrency:** The rate limiter should be able to handle a large number of concurrent requests.

9.  **Metrics:** The service should expose metrics such as requests allowed, requests rejected, and average latency.

**Constraints:**

*   Implement using Rust.
*   Focus on correctness, performance, and scalability.
*   Consider the trade-offs between different implementation approaches (e.g., memory usage vs. performance).
*   Assume that client and resource IDs are strings.
*   The system should be resilient to network partitions.

**Bonus Challenges:**

*   Implement a "leaky bucket" or "token bucket" algorithm for rate limiting, rather than a simple counter.
*   Implement a way to dynamically update rate limit rules without restarting the service.
*   Integrate with a distributed tracing system to monitor the performance of the rate limiter in a distributed environment.
*   Support request prioritization (e.g., allow some requests to bypass the rate limiter based on their priority).

This problem requires a strong understanding of distributed systems concepts, concurrency, data structures, and algorithms. It also requires careful consideration of error handling, fault tolerance, and performance optimization. Different architectural approaches are possible, each with their own trade-offs. The design choices made will significantly impact the performance and scalability of the rate limiter.
