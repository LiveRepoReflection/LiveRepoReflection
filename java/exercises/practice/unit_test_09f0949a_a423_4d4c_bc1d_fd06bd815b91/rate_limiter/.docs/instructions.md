## Project Name

```
distributed-rate-limiter
```

## Question Description

Design and implement a distributed rate limiter in Java. This system must handle a high volume of requests across multiple servers and ensure that no client exceeds a predefined rate limit.

**Scenario:**

Imagine you are building a popular online service. To protect your infrastructure from abuse and ensure fair usage, you need to implement a rate limiter. This rate limiter must be distributed, meaning it can handle requests coming from multiple servers and apply a global rate limit per client.

**Requirements:**

1.  **Rate Limit Definition:** The rate limit is defined as the maximum number of requests a client can make within a specified time window. For example, 100 requests per minute per client.

2.  **Client Identification:** Clients are identified by a unique identifier (e.g., IP address, user ID).

3.  **Distributed Architecture:** The rate limiter must be able to handle requests from multiple servers. Each server should be able to independently check and enforce the rate limit.

4.  **Atomicity:** The rate limiting operation (checking the limit and incrementing the request count) must be atomic to prevent race conditions in a distributed environment.

5.  **Efficiency:** The rate limiter should be highly efficient and have minimal impact on request latency.

6.  **Scalability:** The system should be scalable to handle a large number of clients and requests.

7.  **Fault Tolerance:** The rate limiter should be resilient to server failures. If one server goes down, the rate limiting should continue to function correctly.

8.  **Data Persistence (Optional):** The system should persist the rate limit information to survive server restarts.

**Constraints:**

*   You must use Java.
*   You are free to use any suitable libraries or frameworks, but justify your choices. Consider trade-offs between complexity and performance.
*   Focus on the core rate limiting logic and distributed coordination. You don't need to build a full-fledged web server or client application.
*   The time window for rate limiting can be assumed to be relatively short (e.g., minutes or seconds).
*   Assume the number of clients is large.

**Specific Implementation Details:**

*   Implement a `RateLimiter` interface with a method `allowRequest(String clientId)` that returns `true` if the request is allowed and `false` if the rate limit has been exceeded.
*   Consider at least two different approaches to implement this distributed rate limiter (e.g., using Redis, using a distributed counter with ZooKeeper, etc.).  Clearly explain the design trade-offs of each approach in terms of consistency, performance, scalability, and fault tolerance.
*   Implement **one** of the approaches you have considered.
*   Pay attention to the thread safety implications of your implementation.
*   Provide a way to configure the rate limit (requests per time window) and the time window duration.

**Evaluation Criteria:**

*   Correctness: Does the rate limiter accurately enforce the defined rate limits?
*   Efficiency: How quickly can the rate limiter process requests?
*   Scalability: How well does the rate limiter scale to handle a large number of clients and requests?
*   Fault Tolerance: How resilient is the rate limiter to server failures?
*   Code Quality: Is the code well-structured, readable, and maintainable?
*   Design Rationale: Is the design well-reasoned and are the trade-offs clearly explained?
