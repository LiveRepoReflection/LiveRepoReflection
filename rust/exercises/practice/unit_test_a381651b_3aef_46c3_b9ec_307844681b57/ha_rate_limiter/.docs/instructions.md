## Problem: Highly Available Rate Limiter

**Description:**

Design and implement a distributed rate limiter service. This service is responsible for enforcing rate limits on incoming requests based on various criteria (e.g., IP address, user ID, API key). The key requirements are high availability, low latency, and the ability to handle a large volume of requests.

**Specific Requirements:**

1.  **Rate Limit Definition:** The rate limiter should be able to handle different rate limit configurations. A rate limit is defined by:

    *   `key`: The identifier on which the rate limit is applied (e.g., IP address, user ID).
    *   `limit`: The maximum number of requests allowed within a specified time window.
    *   `window`: The time window (in seconds) during which the `limit` applies.
    *   `priority`: An integer representing the priority of the rate limit. Higher values mean higher priority. When multiple rate limits apply to the same request, the one with the highest priority should be used.
    *   `metadata`: Arbitrary key-value pairs for additional filtering and context.

2.  **Request Matching:** The rate limiter must efficiently determine which rate limits apply to a given request. A request contains:

    *   `key`: The identifier associated with the request.
    *   `metadata`: Arbitrary key-value pairs associated with the request.

    A rate limit applies to a request if the request's `key` matches the rate limit's `key` and the request's `metadata` satisfies all constraints defined in the rate limit's `metadata`. If rate limit's `metadata` is empty, it should apply to requests with any `metadata`.

3.  **Concurrency and Distribution:** The rate limiter service must be distributed across multiple nodes to handle a high volume of requests. Implementations must consider concurrency issues and ensure data consistency across all nodes.

4.  **Persistence:** The rate limiter must persist rate limit definitions and current request counts to ensure data durability and recovery after failures.  Choose a suitable persistence mechanism (e.g., in-memory, Redis, database).

5.  **Atomic Operations:**  The incrementing of the request count and checking against the limit must be performed atomically to avoid race conditions.

6.  **Time Window Management:** Correctly handle the time window for each rate limit. Old requests should expire, and new windows should start without disrupting the service. Consider using a sliding window algorithm or a fixed window algorithm.

7.  **High Availability:** The service should remain available even if some nodes fail.  Consider redundancy and failover mechanisms.

8.  **Low Latency:** The rate limiter should introduce minimal latency to the request processing pipeline. Optimize data structures and algorithms to achieve low response times.

9.  **Efficient Configuration Updates:** Implement a mechanism to update rate limit configurations dynamically without restarting the service or causing significant performance degradation.

10. **Edge Cases and Error Handling:**

    *   Handle cases where no rate limits apply to a request.
    *   Handle invalid or malformed rate limit configurations.
    *   Gracefully handle failures in the persistence layer.

**Constraints:**

*   Assume a large number of concurrent requests.
*   Assume a large number of rate limit rules.
*   Minimize the impact of the rate limiter on the overall system performance.
*   Consider the memory footprint of the rate limiter service.

**Deliverables:**

*   A well-documented Rust code implementation of the rate limiter service.
*   A clear explanation of the design choices, data structures, and algorithms used.
*   A discussion of the trade-offs considered in the implementation.
*   A brief analysis of the performance characteristics of the rate limiter service.
*   Instructions on how to deploy and run the rate limiter service in a distributed environment.
