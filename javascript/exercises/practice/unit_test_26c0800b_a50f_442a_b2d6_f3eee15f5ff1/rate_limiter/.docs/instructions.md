## Project Name

`distributed-rate-limiter`

## Question Description

You are tasked with designing and implementing a distributed rate limiter in JavaScript. This rate limiter will be used to protect a critical API endpoint from abuse by limiting the number of requests a user can make within a given time window.  Unlike a single-instance rate limiter, this system must handle requests across multiple server instances.

**Scenario:**

Imagine you are building a microservices architecture with multiple instances of an API gateway behind a load balancer.  Each instance needs to be aware of the request volume from each user to ensure that no single user overwhelms the system, regardless of which gateway instance they hit.

**Requirements:**

1.  **Distributed Coordination:**  The rate limiter must function correctly even when requests from the same user are handled by different server instances.
2.  **Configurable Rate Limits:** The maximum number of requests allowed per user and the duration of the time window (e.g., 100 requests per minute) should be configurable.
3.  **Scalability:**  The system must be able to handle a large number of users and a high request rate. Consider potential bottlenecks.
4.  **Efficiency:**  The rate limiter should add minimal latency to the API requests.  Optimize for read and write operations.
5.  **Concurrency:**  The rate limiter must handle concurrent requests from multiple users without race conditions.
6.  **Fault Tolerance:**  The system should be reasonably resilient to temporary failures of underlying components (e.g., network issues connecting to the storage).
7.  **Atomic Operations:**  Ensure that incrementing the request count and checking the limit are atomic operations to prevent race conditions.

**Input:**

*   `userId`:  A unique identifier for the user making the request (string).
*   `timestamp`:  The timestamp of the request (milliseconds since epoch, number).

**Output:**

*   `allowRequest`:  A boolean indicating whether the request should be allowed (true) or rejected (false).
*   `retryAfter`:  If `allowRequest` is false, the number of seconds until the rate limit resets, allowing the user to make requests again (number).

**Constraints:**

*   You must use JavaScript (Node.js preferred, but browser-compatible solutions are acceptable with justification).
*   You are encouraged to use an external data store for persistent storage and distributed coordination. Redis is highly recommended, but you can argue for alternatives if you can justify their suitability for the problem, noting the trade-offs.
*   Consider using appropriate data structures and algorithms to optimize performance (e.g., sorted sets with timestamps in Redis).
*   Assume the number of users is very large.
*   Assume the API gateway handles millions of requests per second.

**Bonus Challenges:**

*   Implement sliding window rate limiting (instead of fixed window) for smoother rate limiting.
*   Add support for different rate limits for different API endpoints.
*   Implement a mechanism to handle expired rate limit data automatically to prevent the data store from growing indefinitely.
*   Implement graceful degradation: If the data store is temporarily unavailable, the rate limiter should fail open (allow all requests) or fail closed (reject all requests) based on configuration, with appropriate logging and alerting. Justify your choice.
*   Provide metrics and monitoring capabilities (e.g., request counts, rate limit rejections) for observability.
*   Consider security aspects (e.g., preventing malicious users from flooding the rate limiter with requests from fake user IDs).

**Evaluation Criteria:**

Your solution will be evaluated based on the following factors:

*   **Correctness:**  Does the rate limiter accurately enforce the configured rate limits?
*   **Performance:**  How efficiently does the rate limiter handle requests?
*   **Scalability:**  How well does the system scale to handle a large number of users and requests?
*   **Design:**  Is the code well-structured, maintainable, and easy to understand?
*   **Concurrency Handling:**  Does the solution correctly handle concurrent requests?
*   **Fault Tolerance:**  How resilient is the system to failures of underlying components?
*   **Completeness:**  Does the solution address all the requirements and constraints?
*   **Explanation:**  Clear and concise explanation of design choices and trade-offs made.

This problem requires a good understanding of distributed systems, data structures, algorithms, and concurrency. Good luck!
