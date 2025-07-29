## Project Name

`Distributed Rate Limiter`

## Question Description

Design and implement a distributed rate limiter in Java. This rate limiter should be able to handle a high volume of requests across multiple servers, ensuring that no single user or API key exceeds a predefined request limit within a given time window.

**Scenario:**

Imagine you are building a popular online service. To protect your infrastructure and ensure fair usage, you need to implement a rate limiter. This rate limiter must be highly available, scalable, and fault-tolerant. Your goal is to design a system that limits the number of requests a user (identified by a unique API key) can make to your service within a defined time window.

**Requirements:**

1.  **Configuration:** The rate limiter should be configurable with the following parameters:
    *   `limit`: The maximum number of requests allowed within the time window.
    *   `timeWindow`: The duration of the time window in seconds.
    *   `granularity`: (NEW REQUIREMENT) The accuracy of the rate limit enforcement. Options are:
        *   `GLOBAL`: Rate limit is enforced across all servers.
        *   `SERVER`: Each server enforces the rate limit independently.
        *   `HYBRID`: Rate limit is globally enforced, but with a tolerance factor (see below).
    *   `tolerance`: (Only applicable for `HYBRID` granularity) A percentage representing the allowed overshoot of the rate limit due to eventual consistency in the distributed environment. For example, a tolerance of 10% means a user may temporarily exceed the `limit` by up to 10% during transient states.

2.  **Distributed Operation:** The rate limiter must function correctly in a distributed environment with multiple server instances. All servers must coordinate to enforce the rate limits.

3.  **Atomicity:** The rate limiting operation (checking the limit and incrementing the counter) must be atomic to prevent race conditions.

4.  **Scalability:** The rate limiter should be able to handle a large number of requests and scale horizontally as the service grows.

5.  **Fault Tolerance:** The system should remain functional even if some servers or components fail.

6.  **Efficiency:** The rate limiter should have minimal impact on the overall performance of the service.  Minimize latency introduced by the rate limiting mechanism.

7.  **Real-time Updates:** Changes to rate limiting configurations (e.g., changing `limit` or `timeWindow`) should propagate to all servers in near real-time.

8.  **Eviction Policy:** (NEW REQUIREMENT)  Implement an eviction policy for inactive or expired rate limit counters to prevent memory exhaustion.  Consider both Time-To-Live (TTL) and Least Recently Used (LRU) strategies, and allow the configuration of which strategy to use.

9.  **Accuracy:** For `HYBRID` granularity, ensure that the actual rate limit violation is minimized while staying within the configured tolerance level.

10. **Data Structure Choice:** Choose appropriate data structures to optimize for both read (checking the rate limit) and write (incrementing the counter) operations. Explain your choices.

**Constraints:**

*   You can use any suitable in-memory data store (e.g., Redis, Memcached) or a distributed coordination service (e.g., ZooKeeper, etcd) to share state between servers. Justify your choice.
*   Assume that the API key is readily available for each request.
*   Focus on the core rate limiting logic and do not worry about request parsing or authentication.
*   Assume a large number of unique API keys.

**Deliverables:**

1.  A well-documented Java code implementation of the distributed rate limiter.
2.  A design document explaining your architecture, data structures, algorithms, and trade-offs.  Specifically address how you handle concurrency, scalability, fault tolerance, real-time updates, eviction policy and different granularity options.
3.  A set of unit tests to demonstrate the correctness and performance of your rate limiter.  Include tests for different configurations and edge cases, and tests to verify the `tolerance` constraint for `HYBRID` granularity.
4.  A brief analysis of the time and space complexity of your solution.
