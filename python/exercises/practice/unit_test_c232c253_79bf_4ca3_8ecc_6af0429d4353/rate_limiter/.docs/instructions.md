## Project Name

`Distributed Rate Limiter`

## Question Description

Design and implement a distributed rate limiter. This system should limit the number of requests a client can make to a service within a specific time window, preventing abuse and ensuring service availability.

**Requirements:**

1.  **Distributed:** The rate limiter must work across multiple instances of the service.  A single client's requests can be handled by different servers and the rate limit must be consistent across all instances.
2.  **Configurable Rate Limits:**  The rate limit (number of requests allowed per time window) should be configurable on a per-client basis.  Different clients may have different service level agreements (SLAs).
3.  **Real-time Enforcement:** The rate limit must be enforced in real-time with minimal latency.  The performance overhead of rate limiting should not significantly impact the overall request processing time.
4.  **Time Window Granularity:** The time window should be configurable, allowing for rate limits per second, per minute, per hour, or even custom durations.
5.  **Fault Tolerance:** The system should be resilient to failures.  If one or more rate limiter components fail, the system should degrade gracefully, ideally by allowing requests (fail-open) rather than blocking them (fail-closed).  However, the number of requests allowed during degraded mode should be limited, so the system is not vulnerable to abuse.
6.  **Concurrency:** Handle a high volume of concurrent requests efficiently.
7.  **Scalability:** The rate limiter should be scalable to handle a growing number of clients and requests.
8. **Client Identification:** The system must be able to uniquely identify clients. You can assume that each client is identified by a unique string ID (e.g., API key, user ID).

**Constraints:**

*   You can use any suitable data structures and algorithms.
*   You can use any external libraries or services.
*   Assume a large number of clients (millions).
*   Assume a high request rate (thousands of requests per second).
*   Minimize memory usage.
*   Minimize latency.
*   The rate limits can change dynamically at any time.

**Deliverables:**

1.  A clear design document outlining the architecture of your distributed rate limiter, including the components involved, their interactions, and the data structures used.  Explain the rationale behind your design choices.
2.  A Python implementation of the core rate limiting logic.  Focus on the key aspects of the algorithm and data structures. You don't need to implement the entire system (e.g., API endpoints, configuration management), but you should demonstrate how the core rate limiting logic works.
3.  A brief analysis of the time and space complexity of your solution. Discuss the trade-offs between different approaches.
4.  A discussion of potential failure scenarios and how your design addresses them.
5.  A section on how you would scale your solution to handle even higher loads.

**Bonus:**

*   Implement a mechanism for dynamically updating rate limits without service interruption.
*   Implement a burst allowance strategy, allowing clients to exceed their rate limit for a short period.
*   Consider the impact of clock synchronization issues in a distributed environment and propose solutions.

Good luck!
