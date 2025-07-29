## Project Name

```
distributed-rate-limiter
```

## Question Description

Design and implement a distributed rate limiter in C++.  This rate limiter will be used to protect a set of backend services from being overwhelmed by excessive requests. The rate limiter must meet the following requirements:

*   **Distributed:** The rate limiter should work across multiple instances/servers.
*   **Configurable:** The rate limit (requests per time window) and time window duration should be configurable.
*   **Atomic:**  The rate limiting logic must be atomic to prevent race conditions and ensure accuracy.
*   **Efficient:**  The rate limiter should have low latency to avoid impacting the performance of the backend services.
*   **Fault-Tolerant:**  The rate limiter should continue to function even if some of the instances/servers fail.
*   **Flexible:** The rate limiter should be able to handle different types of keys and rate limiting rules.
*   **Thread-Safe:** The rate limiter must be thread-safe and be able to handle concurrent requests from multiple threads.
*   **Scalable:** The rate limiter should be scalable and be able to handle a large number of requests.
*   **Non-blocking:** The rate limiter should be non-blocking and should not block the calling thread.

**Specifically, you need to implement the following:**

1.  **Data Storage:** Choose a suitable data store for maintaining the request counts and timestamps. You should justify your choice, considering factors like scalability, atomicity, and fault tolerance.  Consider in-memory distributed caches (like Redis or Memcached) or a distributed database. You are allowed to use external libraries for this data storage.

2.  **Rate Limiting Algorithm:** Implement a rate limiting algorithm. Common algorithms include:
    *   **Token Bucket:** Each key has a bucket of tokens that are replenished at a certain rate. Each request consumes a token. If the bucket is empty, the request is rate limited.
    *   **Leaky Bucket:** Requests are added to a queue (the bucket). The queue leaks at a certain rate. If the queue is full, the request is rate limited.
    *   **Fixed Window Counter:** A simple counter tracks the number of requests within a fixed time window. If the counter exceeds the limit, the request is rate limited. The counter is reset at the end of the window.
    *   **Sliding Window Log:** Keep a log of request timestamps within a sliding window. Calculate the number of requests within the window. If it exceeds the limit, the request is rate limited.
    *   **Sliding Window Counter:** Combination of fixed window and log.

    Justify your choice of algorithm, considering its complexity, accuracy, and memory usage.

3.  **API:** Implement the following API:

    ```cpp
    class RateLimiter {
    public:
        // Constructor: takes the rate limit (requests per window),
        // window duration (in milliseconds), and any necessary configuration
        // for the data store.
        RateLimiter(int rateLimit, int windowDurationMs, /* data store config */);

        // Attempts to acquire a permit for the given key.
        // Returns true if the request is allowed, false if it is rate limited.
        bool allow(const std::string& key);

    private:
        // Implementation details (data store, rate limiting algorithm, etc.)
    };
    ```

**Constraints and Considerations:**

*   **High Concurrency:** The system needs to handle a very high volume of requests concurrently.
*   **Low Latency:** The `allow()` method must have minimal latency.
*   **Global Rate Limiting:** The rate limit should be enforced globally across all instances of the rate limiter.
*   **Key Granularity:**  The rate limiting should be configurable per key (e.g., per user ID, per API endpoint).
*   **Time Precision:** Window durations should be handled with millisecond precision.
*   **No Central Lock:** Avoid using a central lock that could become a bottleneck.
*   **Error Handling:**  Handle potential errors from the data store gracefully.

**Bonus Challenges:**

*   Implement dynamic rate limit updates without restarting the rate limiter.
*   Add support for different rate limiting scopes (e.g., global, per-user, per-API endpoint).
*   Implement metrics and monitoring to track rate limiter performance and effectiveness.
*   Implement a distributed consensus algorithm to ensure consistency across all rate limiter instances (e.g., Paxos or Raft) if the data store does not provide strong consistency guarantees.
*   Implement a graceful degradation strategy if the data store becomes unavailable. The rate limiter could temporarily allow all requests or use a more lenient rate limit.
