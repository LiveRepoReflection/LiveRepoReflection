## Project Name

`Scalable Analytics Platform`

## Question Description

You are tasked with designing and implementing a core component of a scalable analytics platform. This platform processes a continuous stream of data points, each representing a timestamped event associated with a specific user and a numerical value. The goal is to efficiently calculate and maintain real-time percentile approximations for each user's data stream.

More formally, you need to implement a system that can:

1.  **Ingest Data:** Accept data points of the form `(user_id, timestamp, value)`, where `user_id` is a string, `timestamp` is a Unix timestamp (int64), and `value` is a float64. The system must be able to handle a high volume of incoming data points (millions per second).

2.  **Maintain Per-User Percentiles:** For each user, maintain an approximate percentile distribution of their data values. You should support querying for specific percentiles (e.g., 50th, 90th, 99th) in near real-time.

3.  **Support High Cardinality:**  The system must handle a large number of distinct users (millions or even billions).

4.  **Provide Approximate Results:** Exact percentile calculation is often too computationally expensive. Therefore, you can use approximation algorithms like t-digest or similar. The accuracy of the approximation should be configurable, allowing for a trade-off between accuracy and memory usage. Provide an API for setting the desired approximation error.

5.  **Handle Time Decay (Optional):**  Optionally, the system should support a time decay mechanism, giving more weight to recent data points when calculating percentiles. This can be implemented using techniques like exponential decay. The decay factor should be configurable.

6.  **Memory Efficiency:** The system must be memory-efficient, as it needs to store data for a large number of users. Consider using techniques like data summarization or probabilistic data structures.

7.  **Concurrent Access:**  The system will be accessed by multiple concurrent readers and writers. Ensure thread safety.

8. **Query Latency:** Should return the requested percentile in acceptable time, even when processing a large amount of data.

**Constraints:**

*   The system should be implemented in Go.
*   You are allowed to use external libraries for data structures and algorithms, but you must justify your choices.
*   Assume the data stream is unordered in terms of timestamps.
*   Error handling is important. Provide clear error messages for invalid inputs or unexpected conditions.
*   Provide a clear and concise API for adding data points and querying percentiles.
*   The platform must be able to handle a large amount of distinct users.
*   Optimize memory usage and query performance.

**Example API:**

```go
type AnalyticsPlatform interface {
	AddDataPoint(userID string, timestamp int64, value float64) error
	GetPercentile(userID string, percentile float64) (float64, error)
	SetCompressionFactor(compressionFactor float64) error // For adjusting approximation error
	SetDecayFactor(decayFactor float64) error // For enabling time decay (optional)
}
```

**Evaluation Criteria:**

*   Correctness of percentile calculations.
*   Efficiency of data ingestion and query processing.
*   Memory usage.
*   Scalability to handle a large number of users and data points.
*   Code quality, readability, and maintainability.
*   Thread safety and concurrency handling.
*   Ability to handle edge cases and invalid inputs.
*   Clear explanation of design choices and trade-offs.
