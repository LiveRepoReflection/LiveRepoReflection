## Question Title: Distributed Rate Limiter with Adaptive Thresholding

### Question Description:

You are tasked with designing and implementing a distributed rate limiter for a high-volume API. The API receives requests from numerous clients across the globe. The goal is to protect the API from being overwhelmed by malicious or unintentional overuse, while ensuring legitimate users experience minimal disruption.

**Core Requirements:**

1.  **Distributed Rate Limiting:** The rate limiter must operate effectively across multiple servers, ensuring consistent enforcement of rate limits regardless of which server a request hits.

2.  **Adaptive Thresholding:**  Instead of using a fixed rate limit, the rate limiter should dynamically adjust its threshold based on the current load and health of the API servers. Factors to consider for adaptation include:
    *   **Server CPU utilization:** Higher CPU usage should trigger stricter rate limits.
    *   **Request latency:** Increasing latency indicates overload, necessitating tighter limits.
    *   **Error rates:** Elevated error rates suggest instability, requiring aggressive throttling.

3.  **Granularity:**  The rate limiter should allow for different levels of granularity:
    *   **Global rate limiting:** Applies to all requests across the entire API.
    *   **User-specific rate limiting:** Enforces limits on a per-user basis (identified by a unique user ID).
    *   **Endpoint-specific rate limiting:** Controls the rate of requests to individual API endpoints.
    *   These granularities can be combined (e.g., user-specific rate limiting for a particular endpoint).

4.  **Fault Tolerance:** The rate limiter should be resilient to failures. If one or more rate limiting components fail, the system should continue to operate, potentially with degraded performance (e.g., temporarily less precise rate limiting).

5.  **Efficiency:** The rate limiter must have minimal impact on API performance. The added latency from rate limiting should be kept as low as possible, even under heavy load.

6.  **Configurability:** The system should be configurable, allowing administrators to adjust:
    *   The relative weight given to each factor (CPU utilization, latency, error rate) in the adaptive thresholding algorithm.
    *   The initial rate limits for each granularity level.
    *   The sensitivity of the adaptive thresholding to changes in the system's health metrics.

**Implementation Details/Constraints:**

*   You are free to choose the appropriate data structures, algorithms, and technologies for your solution, but must justify your choices. Consider the trade-offs between different approaches (e.g., memory usage vs. performance, consistency vs. availability).
*   Assume access to real-time metrics for API server CPU utilization, request latency, and error rates. You do not need to implement the metric collection, but you *do* need to describe how you would integrate them into your rate limiting algorithm.
*   Consider using a distributed caching system (e.g., Redis, Memcached) or a distributed consensus algorithm (e.g., Raft, Paxos) for managing rate limit counters and adaptive thresholds.  Explain your selection.
*   You are not required to implement the API itself. Focus solely on the rate limiting logic.
*   **Scalability is paramount.**  Your design should be able to handle a massive number of requests and users.

**Deliverables:**

1.  A detailed design document outlining your approach, including:
    *   A system architecture diagram.
    *   A description of the data structures used for storing rate limit information and adaptive thresholds.
    *   A pseudocode representation of the rate limiting algorithm, including the adaptive thresholding logic.
    *   An explanation of how you would handle fault tolerance and ensure data consistency.
    *   A justification for your technology choices and a discussion of the trade-offs involved.
    *   An analysis of the time and space complexity of your solution.
2.  Well-documented Python code implementing the core rate limiting logic, including the adaptive thresholding algorithm. The code should be modular and easy to understand.  Focus on clarity and correctness rather than complete production-readiness.
3.  A discussion of potential edge cases and how your solution handles them.
4.  Describe how you would test your rate limiter to ensure it meets the required performance and reliability goals.

This problem assesses your ability to design and implement a complex, distributed system with real-world constraints. Good luck!
