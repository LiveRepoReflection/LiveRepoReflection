## Question: Multi-Tenant Rate Limiter

### Question Description

You are tasked with designing and implementing a distributed rate limiter service for a multi-tenant application. This application serves numerous tenants, each identified by a unique `tenantId`. Each tenant has a specific rate limit defined as `N` requests per `T` seconds. The system needs to handle a high volume of requests concurrently while strictly enforcing the rate limits for each tenant, even under heavy load and potential distributed system issues.

**Specific Requirements:**

1.  **Multi-Tenancy:** The rate limiter must correctly track and enforce rate limits independently for each tenant.

2.  **Configurable Rate Limits:** The values of `N` (number of requests) and `T` (time window in seconds) should be configurable on a per-tenant basis. These values can change at any time. Your system must adapt to these changes without significant downtime or disruption.

3.  **Distributed Operation:** The rate limiter must be able to run on multiple machines (nodes) in a distributed environment. This means that requests from the same tenant might hit different nodes. The system needs to ensure global rate limiting across all nodes for each tenant.

4.  **High Throughput and Low Latency:** The rate limiter should be able to handle a high volume of requests with minimal latency overhead. The target should be supporting thousands of requests per second per node.

5.  **Fault Tolerance:** The system should be resilient to node failures. If a node goes down, the rate limiter should continue to function correctly, although there might be a temporary increase in error rates for a brief period.

6.  **Data Consistency:** The rate limiter needs to ensure that the request counts are consistent across the distributed system. Inconsistencies could lead to rate limits not being enforced correctly, which is unacceptable.

7.  **Atomic Operations:** All operations related to incrementing counters and checking rate limits must be atomic to prevent race conditions, especially in the distributed environment.

8.  **Dynamic Configuration Updates:** The system must support dynamic updates to the rate limits (`N` and `T`) for each tenant without causing service disruption.

9.  **Metrics and Monitoring:** The system should expose metrics like request counts, rate limit hits, and latency for monitoring and alerting purposes.

10. **Eviction Policy:** If the number of tenants becomes very large, you need an eviction policy to remove inactive tenants from memory to prevent resource exhaustion. Implement a Least Recently Used (LRU) cache with a configurable maximum size.

**Input:**

The rate limiter will receive requests, each containing a `tenantId`.

**Output:**

For each request, the rate limiter should return a boolean value: `true` if the request is allowed (i.e., the tenant is within their rate limit), and `false` if the request is rejected (i.e., the tenant has exceeded their rate limit).

**Constraints:**

*   Number of tenants: Up to 1,000,000
*   Requests per second per node: Up to 10,000
*   Latency per request: Must be less than 1 millisecond on average.
*   Time window (T): Between 1 and 60 seconds.
*   Rate Limit (N): Between 1 and 10000.
*   Memory usage per node: Limited to 10GB.
*   Assume a reasonably reliable network connection between nodes.
*   You do not need to handle malicious tenants attempting to game the system. Assume all requests are legitimate.

**Bonus Challenges:**

*   Implement graceful degradation under extreme load. For instance, prioritize requests from high-value tenants if the system is overloaded.
*   Add support for tiered rate limits (e.g., different rate limits during peak and off-peak hours).
*   Implement a command-line interface (CLI) to configure rate limits for tenants.
*   Implement Leader Election between distributed nodes to handle configuration updates in a single point.

**Considerations:**

*   Think carefully about the data structures you use to store request counts.
*   Consider different approaches for synchronizing request counts across nodes. (e.g., distributed counters, consensus algorithms, eventual consistency)
*   Balance consistency, availability, and partition tolerance (CAP theorem).
*   Consider the impact of clock skew between nodes.
*   Assume you have access to a reliable time source.

This is a challenging problem that requires a strong understanding of distributed systems, data structures, and algorithms. Good luck!
