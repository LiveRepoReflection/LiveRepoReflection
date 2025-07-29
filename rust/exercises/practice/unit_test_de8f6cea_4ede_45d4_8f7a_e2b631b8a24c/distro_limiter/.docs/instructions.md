## Project Name

```
distributed-rate-limiter
```

## Question Description

Design and implement a distributed rate limiter service in Rust. This service must enforce rate limits across multiple independent application instances accessing a shared resource.

**Scenario:**

Imagine you are building a popular online service with numerous geographically distributed application servers. To protect a critical backend database from being overwhelmed, you need a rate limiter that restricts the number of requests from all application instances within a given time window.

**Requirements:**

1.  **Distributed Counting:** The rate limiter must accurately track the total number of requests across all application instances.
2.  **Configurable Rate Limits:** The rate limit (requests per second/minute/hour) should be configurable, and the service must allow dynamic updates to these limits.
3.  **Atomic Operations:** Rate limit checks and increments must be atomic to prevent race conditions when multiple requests occur simultaneously.
4.  **Low Latency:** The rate limiter must introduce minimal latency to request processing. Implement optimizations to achieve high throughput.
5.  **Fault Tolerance:** The rate limiter should be resilient to node failures. Data persistence and replication should be considered to prevent loss of rate limit state.
6.  **Scalability:** The system should be able to handle a large number of concurrent requests and application instances.  Consider sharding or other partitioning strategies.
7.  **Time-Based Reset:** The rate limiter must reset the request count after the specified time window (e.g., reset the count to zero at the start of each minute).
8.  **Graceful Degradation:** In the event of a major failure, the rate limiter can temporarily switch to a more permissive mode (e.g., disable rate limiting entirely) instead of blocking all requests.
9. **Multiple Rate Limit Keys**: The rate limiter needs to be able to handle different types of requests that are rate limited by different keys. An example can be rate limiting user signups by the user's IP address vs. rate limiting password resets by user ID.
10. **Sliding Window Rate Limiting**: Instead of fixed time windows, implement a sliding window rate limiting algorithm to provide finer granularity and prevent burst requests at the boundary of fixed windows.

**Constraints:**

*   The solution must be implemented in Rust.
*   You are free to use any appropriate external libraries or data stores (e.g., Redis, etcd, a distributed consensus algorithm implementation) for distributed coordination and storage. Justify your choices.
*   Assume that the application instances can communicate with the rate limiter service over a network.
*   Consider the cost of the solution, including memory usage, CPU usage, and network bandwidth.

**Considerations:**

*   Explore different rate-limiting algorithms (e.g., Token Bucket, Leaky Bucket, Fixed Window Counter, Sliding Window Log, Sliding Window Counter). Justify your choice based on the requirements.
*   Discuss trade-offs between consistency and availability.
*   Address potential security concerns, such as preventing malicious clients from bypassing the rate limiter.
*   Document your design choices, including data structures, algorithms, and architecture.

**Goal:**

Provide a well-documented, robust, and performant distributed rate limiter service that meets the specified requirements and constraints. Focus on code clarity, maintainability, and scalability. Justify all the design choices.
