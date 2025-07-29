## Project Name

```
distributed-rate-limiter
```

## Question Description

Design and implement a distributed rate limiter with the following requirements:

**Scenario:** Imagine you're building a large-scale distributed system where you need to protect your services from being overwhelmed by excessive requests. You need a rate limiter that can handle a high volume of requests across multiple servers and prevent abuse.

**Requirements:**

1.  **Distributed Operation:** The rate limiter should function correctly even when requests are being processed by multiple independent servers.  It cannot rely on single-server state.

2.  **Configurable Rate Limits:**  You should be able to define rate limits based on different criteria (e.g., requests per second, requests per minute, requests per day) and different keys (e.g., user ID, API key, IP address).

3.  **Atomic Operations:**  The rate limiting logic must be atomic to prevent race conditions when multiple requests arrive simultaneously.  Consider how to update the request count without losing data.

4.  **Efficiency:** The rate limiter should be highly performant, minimizing latency for each request.  Consider the overhead of distributed coordination and data storage.  Aim for sub-millisecond latency where possible, with graceful degradation under extreme load.

5.  **Scalability:** The system should be able to handle a large number of unique keys and a high request rate. Think about partitioning and sharding strategies.

6.  **Fault Tolerance:** The rate limiter should continue to function correctly even if some servers or storage nodes become unavailable.

7.  **Time-Based Expiration:**  Rate limits should automatically reset after the specified time period.  Implement a mechanism for expiring old data.

8.  **Throttling Response:**  When a request exceeds the rate limit, the rate limiter should return a clear error message, ideally including information about when the rate limit will be reset.

9.  **Extensibility:** The design should be easily extensible to support additional rate-limiting algorithms (e.g., token bucket, leaky bucket) and storage backends.

10. **Cost Effectiveness:** Consider the operational cost of your solution, choosing appropriate technologies and storage solutions to minimize expense.

**Constraints:**

*   **Language:** Implement the solution in JavaScript (Node.js preferred).
*   **External Libraries:** You can use external libraries, but justify their use and consider their impact on performance and dependencies.  Avoid libraries that provide full-blown rate limiting solutions; the goal is to build the core logic yourself.
*   **Storage:** Choose an appropriate storage backend for maintaining request counts.  Consider trade-offs between in-memory stores (e.g., Redis) and persistent databases (e.g., Cassandra, DynamoDB). Justify your choice. Simulate the behaviour of the chosen storage if you don't have access to it.
*   **Concurrency:**  Assume a high degree of concurrency.  Your solution must be thread-safe (or equivalent in Node.js).

**Deliverables:**

1.  **Code:** Well-structured, documented, and tested JavaScript code that implements the distributed rate limiter.
2.  **Design Document:** A brief document outlining the system design, including the chosen architecture, storage backend, algorithms, and trade-offs.  Explain how your design addresses the requirements and constraints.  Discuss potential bottlenecks and scalability limitations.
3.  **Testing Strategy:** Describe your testing approach, including unit tests, integration tests, and performance tests.  Demonstrate that your rate limiter functions correctly under various load conditions. Focus on edge cases and concurrency scenarios.
4.  **Optimization Report:** A report on the optimizations you performed to improve the rate limiter's performance, including any benchmarking data.

**Judging Criteria:**

*   Correctness: Does the rate limiter accurately enforce the configured limits?
*   Performance: How efficiently does the rate limiter handle requests?
*   Scalability: How well does the rate limiter scale to handle increasing load?
*   Fault Tolerance: How resilient is the rate limiter to failures?
*   Code Quality: Is the code well-structured, documented, and easy to understand?
*   Design Rationale: Is the design well-reasoned and justified?
*   Testing: Are the tests comprehensive and effective?

Good luck! This is a challenging problem that requires careful design and implementation.
