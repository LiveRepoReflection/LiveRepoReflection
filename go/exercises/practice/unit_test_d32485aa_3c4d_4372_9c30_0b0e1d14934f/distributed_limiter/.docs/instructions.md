## Problem: Distributed Rate Limiter with Consistency Guarantees

**Description:**

Design and implement a distributed rate limiter service in Go. This service must enforce rate limits across multiple independent instances, ensuring fairness and preventing abuse.

**Scenario:**

Imagine a microservices architecture where numerous client applications access a critical resource (e.g., an API endpoint, a database).  To prevent overload and ensure fair usage, a rate limiter is required. The rate limiter must operate across multiple instances of the microservice, handling requests from different clients concurrently.

**Requirements:**

1.  **Core Functionality:** Implement a function `Allow(client_id string, limit int, window time.Duration) bool` that returns `true` if a client is allowed to make a request, and `false` if the rate limit has been exceeded.  `client_id` uniquely identifies a client. `limit` specifies the maximum number of requests allowed within the `window` (duration).

2.  **Distributed Operation:** The rate limiter must function correctly even when deployed across multiple instances.  Each instance should be able to independently evaluate requests without requiring constant, synchronous communication with other instances for every request.

3.  **Consistency:**  While perfect consistency is generally impossible in a distributed system, strive for strong eventual consistency. Clients should observe reasonably consistent rate limiting behavior regardless of which instance handles their requests. Avoid scenarios where a client can easily bypass the rate limit by switching between instances.

4.  **Efficiency:**  The `Allow` function must be highly performant.  Minimize latency and resource consumption.  Consider the trade-offs between memory usage, network traffic, and computational complexity.

5.  **Scalability:**  The rate limiter service should be horizontally scalable.  Adding more instances should increase its capacity without significantly degrading performance.

6.  **Fault Tolerance:** The system should be resilient to failures.  If one instance of the rate limiter goes down, the others should continue to function correctly.

7.  **Concurrency:** The rate limiter must handle concurrent requests from multiple clients safely and efficiently.  Use appropriate synchronization primitives to avoid race conditions.

8.  **Durability:** Consider the persistence of rate limit data. Should rate limits reset if all instances restart simultaneously?  If so, in-memory storage is acceptable. If not, a persistent storage mechanism (e.g., Redis, a database) is required. Clearly state your assumptions about data persistence.

9.  **Time Synchronization:** Assume that all instances of the rate limiter service have reasonably synchronized clocks (e.g., using NTP). Clock skew should be minimized.  If your solution is sensitive to clock skew, explain how it could be mitigated.

**Constraints:**

*   The solution must be implemented in Go.
*   You can use external libraries, but justify their use and explain their impact on performance, scalability, and reliability.
*   Clearly document your design choices, including the data structures used, the algorithms employed, and the trade-offs considered.

**Bonus (Optional):**

*   Implement a mechanism for dynamically adjusting rate limits (e.g., based on server load or client subscription tier).
*   Provide a simple monitoring endpoint that exposes key metrics, such as the number of requests allowed/denied, average latency, and resource consumption.
*   Implement a distributed lock to prevent race conditions when updating rate limit data in a persistent store.
