## Project Name

```
Distributed Rate Limiter with Adaptive Quorum
```

## Question Description

You are building a distributed rate limiter service. This service is designed to protect a critical API from being overwhelmed by excessive requests. The service needs to be highly available and resilient to network partitions.

**Core Requirements:**

1.  **Distributed Counting:** Implement a distributed counter that tracks the number of requests made within a given time window. The counter should be distributed across multiple nodes to avoid single points of failure.

2.  **Rate Limiting Enforcement:** Enforce a rate limit (maximum number of requests per second) for each client (identified by a unique client ID). If a client exceeds the rate limit, subsequent requests should be rejected with an appropriate error.

3.  **Adaptive Quorum:** Implement an adaptive quorum mechanism to handle network partitions and node failures. The quorum size (the minimum number of nodes that must agree on the counter value) should dynamically adjust based on the current network conditions. The system should maintain high availability even with a significant number of nodes being unavailable.  Specifically, if more than a certain percentage of nodes are available, the quorum should be the majority, otherwise, the quorum can reduce to a single node.

4.  **Eventual Consistency:** Due to the distributed nature of the system, perfect consistency is not required. However, the system should strive for eventual consistency, meaning that the counter values on all nodes should converge over time.

5.  **Concurrency:** The rate limiter must handle a high volume of concurrent requests from multiple clients.

**Specific Constraints and Requirements:**

*   **Time Window:** The rate limit should be enforced over a sliding one-second window.
*   **Client Identification:** Assume each request is associated with a unique client ID (string).
*   **Node Discovery:** Assume there is a mechanism (e.g., a distributed configuration service) that allows each node to discover the addresses of all other nodes in the cluster.  You can simulate this.
*   **Communication:** You can use any suitable communication protocol (e.g., gRPC, HTTP) for inter-node communication.
*   **Error Handling:** Implement robust error handling to deal with network failures, node crashes, and other unexpected events.
*   **Optimization:**  The solution should be optimized for low latency and high throughput. Consider the trade-offs between consistency and performance.
*   **Adaptive Quorum details**: When more than 75% of nodes are available, the quorum size should be a strict majority. When less than 75% of nodes are available, the quorum size can reduce to one, favoring availability over strong consistency.
*   **Assume**: Clock synchronization is "good enough". You don't need to implement NTP or similar.

**Scenarios to Consider:**

*   Normal operation with all nodes healthy.
*   Node failures and network partitions.
*   High request volume from multiple clients.
*   Clients exceeding their rate limits.
*   Adaptive quorum in action.

**Evaluation Criteria:**

*   Correctness: The rate limiter should accurately enforce the rate limits and handle edge cases.
*   Availability: The service should remain available even with node failures and network partitions.
*   Performance: The service should handle a high volume of concurrent requests with low latency.
*   Robustness: The solution should be resilient to errors and unexpected events.
*   Code Quality: The code should be well-structured, readable, and maintainable.

This problem requires a solid understanding of distributed systems concepts, concurrency, and data structures. Good luck!
