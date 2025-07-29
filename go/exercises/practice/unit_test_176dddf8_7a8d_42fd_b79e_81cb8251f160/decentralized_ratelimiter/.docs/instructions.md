## Question: Decentralized Rate Limiter

### Description

You are tasked with designing and implementing a highly performant, decentralized rate limiter. This rate limiter will be used to protect a distributed system of microservices from being overwhelmed by excessive requests from any single user. Unlike traditional centralized rate limiters, this system must operate without a single point of failure or bottleneck.

The system consists of `N` microservice nodes (where `N` can be very large). Each node receives incoming requests identified by a unique `user_id`.  The rate limit is defined as the maximum number of requests (`R`) a user can make within a specific time window (`T`).

**Requirements:**

1.  **Decentralization:** No single node should maintain the complete state of all users' request counts.  The system should operate correctly even if some nodes are temporarily unavailable.

2.  **High Performance:**  The rate limiter must handle a very high volume of requests with minimal latency.  Every request should be processed in sub-millisecond time.

3.  **Fault Tolerance:**  The system must be resilient to node failures.  If a node goes down, the rate limiter should continue to function correctly, potentially with slightly degraded accuracy in edge cases.

4.  **Approximate Rate Limiting:**  Perfectly accurate rate limiting across all nodes is not required and may be impossible to achieve in a decentralized environment.  The system should aim to provide a *probabilistic* guarantee that the rate limit is not exceeded.  You must justify your choice of probabilistic guarantee.

5.  **Time Window Handling:** The time window `T` must be handled correctly. Expired requests should not contribute to the rate limit.

6.  **Scalability:** The system should be able to scale to handle a large number of users and microservice nodes.

7.  **User ID Space:** The user ID space is very large (2^64).

**Input:**

The rate limiter will receive a stream of requests, each represented by a `user_id` (uint64).

**Output:**

For each request, the rate limiter should return a boolean value:

*   `true`: if the request is allowed (i.e., does not exceed the rate limit).
*   `false`: if the request is denied (i.e., would exceed the rate limit).

**Constraints:**

*   `1 <= N <= 10000` (Number of microservice nodes)
*   `1 <= R <= 1000` (Maximum requests per time window)
*   `1 <= T <= 60` (Time window in seconds)
*   Assume a distributed environment with potential network latency between nodes.
*   Memory usage per node should be minimized.

**Evaluation Criteria:**

Your solution will be evaluated based on:

*   Correctness: How accurately does the rate limiter enforce the rate limit?
*   Performance: How quickly does the rate limiter process requests?
*   Scalability: How well does the system scale to a large number of users and nodes?
*   Fault Tolerance: How well does the system handle node failures?
*   Resource Usage: How much memory and CPU resources does the system consume?
*   Clarity and Justification: How well is your design explained and justified, including the choice of data structures, algorithms, and probabilistic guarantees?

**Bonus:**

*   Implement a mechanism to dynamically adjust the rate limit (`R`) based on system load.
*   Provide a mechanism to monitor and visualize the performance of the rate limiter.
*   Consider strategies to handle bursts of traffic.
