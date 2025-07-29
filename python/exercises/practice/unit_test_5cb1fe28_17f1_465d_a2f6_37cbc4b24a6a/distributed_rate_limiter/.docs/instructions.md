## Project Name

`Distributed Rate Limiter with Consistency Guarantees`

## Question Description

You are tasked with designing and implementing a highly scalable and consistent distributed rate limiter. This rate limiter should be able to handle a large number of requests across multiple servers while ensuring that the rate limits are accurately enforced, even in the presence of network partitions and server failures.

**Detailed Requirements:**

1.  **Core Functionality:**
    *   Implement a function `allow_request(user_id, api_endpoint, rate_limit, time_window)` that determines whether a given request should be allowed based on the specified rate limit.
    *   The `rate_limit` represents the maximum number of requests allowed within the given `time_window` (in seconds).
    *   `user_id` is a unique identifier for the user making the request.
    *   `api_endpoint` is a string identifying the specific API endpoint being accessed.

2.  **Distributed Architecture:**
    *   The rate limiter must be able to run on multiple servers (nodes) in a distributed system.
    *   Requests should be able to be routed to any available server.
    *   Assume that requests for the same `user_id` and `api_endpoint` will eventually arrive to the same server (e.g., using consistent hashing). However, brief inconsistencies are allowed during server failure and recovery.

3.  **Consistency:**
    *   The rate limiter must ensure that the rate limits are not exceeded, even with concurrent requests across multiple servers.
    *   Achieve strong eventual consistency. During normal operation, the rate limiter should behave as if it were a single, centralized system.

4.  **Scalability:**
    *   The system should be able to handle a high volume of requests.
    *   The solution should be horizontally scalable, meaning that you can increase capacity by adding more servers.

5.  **Fault Tolerance:**
    *   The system should be resilient to server failures.
    *   If a server goes down, the system should continue to operate, and the rate limits should still be enforced (though potentially with a temporary period of inaccuracy).

6.  **Data Storage:**
    *   You can choose your own data storage mechanism (e.g., Redis, Memcached, a distributed database). Justify your choice. Consider both performance and consistency trade-offs.

7.  **Optimization:**
    *   Optimize for both read (checking rate limit) and write (incrementing request count) performance.
    *   Minimize latency for the `allow_request` function.

8.  **Edge Cases and Constraints:**
    *   Handle edge cases such as:
        *   Requests arriving slightly outside the `time_window`.
        *   Clock skew between servers.
    *   Consider the impact of very large user IDs.

9.  **System Design Considerations:**
    *   Describe the overall architecture of your rate limiter.
    *   Explain how you handle concurrent requests.
    *   Explain how you handle server failures and recovery.
    *   Discuss the trade-offs between consistency, availability, and performance.
    *   Justify your choice of algorithms and data structures.

**Bonus (Optional):**

*   Implement a mechanism to dynamically adjust rate limits based on system load or other factors.
*   Implement a monitoring system to track rate limiter performance and identify potential issues.

**Note:** You are not expected to write a production-ready system in a short time. The goal is to demonstrate your understanding of distributed systems concepts, rate limiting algorithms, and trade-offs.  Focus on the core logic and design, and clearly explain your reasoning.
