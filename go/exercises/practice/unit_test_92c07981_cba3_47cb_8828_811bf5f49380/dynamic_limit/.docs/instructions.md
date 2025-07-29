Okay, here's a problem designed to be challenging and require thoughtful implementation in Go, drawing inspiration from the provided example and aiming for LeetCode Hard difficulty:

**Problem Title:** Distributed Rate Limiter with Dynamic Capacity

**Problem Description:**

You are tasked with designing and implementing a distributed rate limiter system in Go.  This rate limiter needs to protect a critical service from being overwhelmed by incoming requests. However, unlike a simple fixed-window rate limiter, this system needs to dynamically adjust its capacity based on observed service health and resource availability.

The system consists of several components:

1.  **Rate Limiter Nodes:** Multiple independent Go processes acting as rate limiters. These nodes receive requests, check against the current rate limit, and either allow or reject the request.

2.  **Capacity Manager:** A central Go process responsible for monitoring service health (e.g., CPU usage, memory usage, error rates) and adjusting the overall request capacity of the rate limiter system.

3.  **Service Under Protection:** The actual service being protected by the rate limiter.  This service is assumed to be running independently and exposes metrics that the Capacity Manager can consume.

**Specific Requirements:**

*   **Distributed Consensus:**  The rate limiter nodes must maintain a consistent view of the current request capacity, even in the presence of network partitions or node failures. You should implement a distributed consensus mechanism (e.g., Raft, Paxos, or a simpler, custom protocol sufficient for this specific use case) to ensure this consistency.  Assume you have a reliable, ordered message passing mechanism available between the rate limiter nodes.

*   **Dynamic Capacity Adjustment:** The Capacity Manager should periodically (e.g., every 5 seconds) collect metrics from the Service Under Protection. Based on these metrics, it should calculate a new total request capacity for the rate limiter system. The algorithm for capacity adjustment is as follows:

    *   **Base Capacity:**  The system starts with a `baseCapacity`.
    *   **CPU Usage Penalty:** If the service's CPU usage exceeds a threshold `cpuThreshold`, the capacity is reduced by `(CPU usage - cpuThreshold) * cpuPenaltyFactor`.
    *   **Error Rate Penalty:** If the service's error rate exceeds a threshold `errorRateThreshold`, the capacity is reduced by `(Error Rate - errorRateThreshold) * errorRatePenaltyFactor`.
    *   **Capacity Limits:** The total capacity must always be within the range `minCapacity` and `maxCapacity`.

    The Capacity Manager must then reliably communicate the updated capacity to all rate limiter nodes.

*   **Atomic Rate Limiting:** Each rate limiter node must implement an atomic mechanism to determine whether a request should be allowed or rejected. This mechanism must be thread-safe (using mutexes, channels, or atomic operations) to handle concurrent requests.

*   **Request Representation:** Assume each request is represented by a unique request ID (a string).

*   **Fault Tolerance:** The system should be reasonably fault-tolerant.  If a rate limiter node fails, the other nodes should continue to operate correctly.  The Capacity Manager should also be designed to be resilient to temporary network connectivity issues.

*   **Optimization:** Strive for optimal performance. The rate limiting logic must be highly efficient to avoid introducing significant latency to the service.  Consider the trade-offs between different data structures and algorithms. Minimize network traffic and computational overhead.

**Constraints:**

*   **No External Libraries:** You can use standard Go libraries, but are prohibited from using external libraries or frameworks for distributed consensus (Raft, etcd, Consul, etc.). The goal is to design and implement the consensus mechanism yourself, albeit a simplified version sufficient for this specific problem.
*   **Integer Arithmetic:** All capacity values (baseCapacity, minCapacity, maxCapacity, penalties) should be represented as integers.
*   **Real-World Considerations:** Consider potential race conditions, deadlocks, and error handling. Your solution should be robust and handle unexpected situations gracefully.
*   **Scalability:** While the problem focuses on a limited number of rate limiter nodes, think about how your design could be scaled to handle a larger number of nodes in a real-world deployment.

**Input:**

The initial configurations are provided via command-line arguments or a configuration file (you can choose the format). These configurations include:

*   `baseCapacity`: The initial request capacity.
*   `minCapacity`: The minimum allowed request capacity.
*   `maxCapacity`: The maximum allowed request capacity.
*   `cpuThreshold`: The CPU usage threshold.
*   `cpuPenaltyFactor`: The penalty factor for exceeding the CPU threshold.
*   `errorRateThreshold`: The error rate threshold.
*   `errorRatePenaltyFactor`: The penalty factor for exceeding the error rate threshold.
*   A list of addresses for all rate limiter nodes (including the current node).
*   The address of the Capacity Manager.
*   The address of the Service Under Protection (for fetching metrics).

**Output:**

The rate limiter nodes should expose an endpoint (e.g., an HTTP endpoint) that accepts requests.  The endpoint should return:

*   `200 OK` if the request is allowed.
*   `429 Too Many Requests` if the request is rate-limited.

The Capacity Manager should print its capacity adjustments to standard output at regular intervals.

**Judging Criteria:**

*   **Correctness:** Does the rate limiter correctly allow or reject requests based on the current capacity?
*   **Consistency:** Do the rate limiter nodes maintain a consistent view of the capacity?
*   **Dynamic Adjustment:** Does the Capacity Manager correctly adjust the capacity based on the service's metrics?
*   **Fault Tolerance:** Does the system continue to operate correctly in the presence of node failures or network issues?
*   **Performance:** Is the rate limiting logic efficient and does it avoid introducing excessive latency?
*   **Code Quality:** Is the code well-structured, readable, and maintainable?
*   **Error Handling:** Does the code handle errors gracefully?

This problem is designed to be open-ended and allow for multiple valid approaches with different trade-offs. The challenge lies in designing a robust, efficient, and fault-tolerant distributed system while adhering to the constraints. Good luck!
