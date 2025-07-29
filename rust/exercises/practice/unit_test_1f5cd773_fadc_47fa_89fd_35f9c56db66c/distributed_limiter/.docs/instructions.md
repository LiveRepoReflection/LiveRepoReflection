Okay, I'm ready to create a challenging Rust programming competition problem. Here it is:

**Problem Title: Distributed Rate Limiter**

**Problem Description:**

You are tasked with designing and implementing a distributed rate limiter service in Rust. This service must limit the number of requests from a specific client (identified by a unique `client_id`) within a given time window. The rate limiter will be deployed across multiple nodes in a cluster to handle high traffic.

**Functional Requirements:**

1.  **`is_allowed(client_id: &str) -> bool`**: This function is the core of the rate limiter. It should determine whether a request from the given `client_id` is allowed at the current time. If the request is allowed, the rate limiter should record the request and return `true`. Otherwise, it should return `false`.

2.  **Configuration:** The rate limiter must be configurable with:

    *   `rate_limit`: The maximum number of requests allowed per time window.
    *   `time_window`: The duration of the time window in seconds.

3.  **Persistence:** The rate limiter needs to persist request counts across restarts. Use a suitable data store for persistence (e.g., Redis, RocksDB, or an in-memory store with snapshotting to disk). Consider trade-offs of each option.

4.  **Concurrency:** The `is_allowed` function must be thread-safe to handle concurrent requests from multiple clients across different threads.

5.  **Distribution:** The rate limiter service is distributed across multiple nodes. You need to address the challenges of maintaining consistent request counts across these nodes.  Consider techniques such as:
    *   Centralized counting (e.g., using a distributed lock on a shared counter).
    *   Distributed counters (e.g., using probabilistic data structures like Bloom filters or HyperLogLog, or sharded counters).
    *   Token bucket algorithm with distributed refills.

**Non-Functional Requirements:**

1.  **Performance:** The `is_allowed` function should have minimal latency. Aim for very high throughput (requests per second).
2.  **Scalability:** The rate limiter service should be horizontally scalable by adding more nodes to the cluster.
3.  **Fault Tolerance:** The rate limiter should continue to function correctly even if some nodes in the cluster fail.
4.  **Consistency:**  The rate limiter should provide a reasonable level of consistency.  Strict consistency might be too expensive, so explore eventual consistency models if appropriate. Justify your choice.
5.  **Efficiency:** Minimize memory usage and CPU consumption.
6.  **Maintainability:** The code should be well-structured, documented, and easy to maintain.
7.  **Observability:** Provide metrics (e.g., using Prometheus) to monitor the rate limiter's performance, such as request throughput, latency, and error rates.  Also log important events.

**Constraints:**

*   The rate limiter should be implemented in Rust.
*   You are free to use any external crates, but justify your choices in the documentation.
*   Assume the `client_id` is a string that can be arbitrarily long.
*   The number of nodes in the cluster can vary.

**Evaluation Criteria:**

*   **Correctness:** Does the rate limiter accurately limit requests based on the configured rate and time window?
*   **Performance:** How many requests per second can the rate limiter handle? What is the average latency of the `is_allowed` function?
*   **Scalability:** How does the performance of the rate limiter scale as the number of nodes increases?
*   **Fault Tolerance:** How does the rate limiter behave when nodes fail?
*   **Code Quality:** Is the code well-structured, documented, and easy to understand?
*   **Resource Usage:** How much memory and CPU does the rate limiter consume?
*   **Completeness:** Does the solution address all the functional and non-functional requirements?
*   **Design Justification:** Provide clear reasoning for the design choices made, especially regarding data structures, algorithms, concurrency, and distribution.

**Bonus Challenges:**

*   Implement dynamic rate limiting, where the rate limit can be adjusted at runtime.
*   Support different rate limits for different clients.
*   Implement a "burst" allowance, allowing clients to exceed the rate limit temporarily.
*   Add support for rate limiting based on other criteria, such as geographical location or request type.

This problem is designed to be very open-ended and allows for a wide range of solutions with different trade-offs. The best solutions will demonstrate a deep understanding of distributed systems principles, concurrency, and performance optimization. Good luck!
