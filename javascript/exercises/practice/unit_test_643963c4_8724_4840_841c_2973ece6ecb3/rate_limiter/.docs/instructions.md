## Project Name

```
Distributed Rate Limiter
```

## Question Description

You are tasked with designing and implementing a distributed rate limiter. This rate limiter will be used to protect a highly scalable API from abuse and overuse across a cluster of multiple servers.

**Core Requirements:**

1.  **Global Rate Limiting:** The rate limiter must enforce a global limit on the number of requests allowed per user (identified by a unique `userId`) within a specific time window (e.g., 100 requests per minute). This limit applies across all servers in the cluster.

2.  **Atomic Operations:** To prevent race conditions in a distributed environment, all operations related to incrementing and checking the request count for a user must be atomic.

3.  **Fault Tolerance:** The rate limiter should continue to function correctly even if some servers or components fail.

4.  **Scalability:** The rate limiter should be able to handle a large number of users and requests per second.

5.  **Efficiency:** Minimize latency and resource consumption.  Reads should be as fast as possible.

6.  **Time Window Granularity:** The rate limiter should support relatively fine-grained time windows (e.g., 1 second, 1 minute).

7.  **Extensibility:** The design should be extensible to support different rate limiting algorithms (e.g., token bucket, leaky bucket) in the future.

8.  **User Level Configuration:** It must be possible to configure specific rate limits for individual users. If a user has a specific rate limit configuration, that must override the default configuration.

**Constraints:**

*   Assume you have access to a distributed key-value store (e.g., Redis, Memcached) that supports atomic operations.  You can choose the specific key-value store and its operations, but justify your choice.
*   You need to design an API with 2 functions: `isAllowed(userId: string): boolean` and `configureUserLimit(userId: string, requestLimit: number, timeWindow: number): void`.
*   The `isAllowed` function must be optimized for speed.
*   Consider the cost of each operation, especially read and write operations to the key-value store.
*   Consider memory usage.  How will you prevent the rate limiter from consuming excessive memory, especially with a large number of active users?
*   Explain your approach for handling time synchronization issues between servers in the cluster.
*   Implement the `isAllowed` function, focusing on correctness and performance. You may pseudocode other parts of the system, but the `isAllowed` function should be functional javascript code.
*   Assume that calls to configureUserLimit are infrequent compared to calls to isAllowed.
*   Assume that you can store user configuration data in the key-value store along with request count data.
*   Assume that requestLimit and timeWindow are positive integers.
*   Assume that the `userId` is a string of alphanumeric characters.
*   Assume the existence of a reliable and performant `getTimeInSeconds()` function that returns the current time in seconds since the epoch, synchronized across the cluster.
*   Assume the existence of a function `atomicIncrement(key: string, expiryInSeconds?: number): number` that atomically increments a key in your chosen key-value store.  If the key doesn't exist, it's created and initialized to 1. The function returns the new, incremented value. `expiryInSeconds` is optional, and if provided, sets an expiry on the key.
*   Consider the trade-offs between different approaches. Explain your reasoning behind your design choices.

**Deliverables:**

1.  **System Design Document:** A high-level description of your rate limiter architecture, including the components, data structures, and algorithms used.  Explain how your design addresses the core requirements and constraints.

2.  **API Design:** A clear definition of the API for the rate limiter, including the input parameters and return values for each method.

3.  **Code Implementation:** Implement the `isAllowed(userId: string): boolean` function in Javascript. This function must be well-commented and easy to understand.

4.  **Justification:** Explain why you chose the specific data structures, algorithms, and key-value store operations. Discuss the trade-offs and limitations of your design.

This problem requires a deep understanding of distributed systems, data structures, and algorithms.  A well-designed and implemented solution will demonstrate strong problem-solving skills and a solid understanding of the principles of scalability, fault tolerance, and performance optimization.  Good luck!
