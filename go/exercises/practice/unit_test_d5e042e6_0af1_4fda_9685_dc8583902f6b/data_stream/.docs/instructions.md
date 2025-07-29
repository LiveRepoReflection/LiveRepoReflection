## Project Name

```
optimized-data-stream-analytics
```

## Question Description

You are building a real-time data analytics pipeline for a high-volume sensor network. The network consists of `N` sensors, each emitting numerical data points at irregular intervals. Your task is to design and implement a system that efficiently calculates and maintains a set of statistical measures across all sensors' data streams, subject to stringent memory and latency constraints.

Specifically, your system must support the following operations:

1.  **Ingest Data:** Accept a stream of data points from the sensor network. Each data point is a tuple `(sensor_id, timestamp, value)`, where `sensor_id` is an integer between `0` and `N-1`, `timestamp` is a Unix timestamp (integer), and `value` is a floating-point number. The stream arrives in no particular order (sensor_id or timestamp).

2.  **Calculate Aggregate Statistics:**
    *   **Mean:** Calculate the average value across all sensors for data points within a specified time window `[start_time, end_time]`.
    *   **Median:** Calculate the median value across all sensors for data points within a specified time window `[start_time, end_time]`.
    *   **Percentile (P):** Calculate the P-th percentile value across all sensors for data points within a specified time window `[start_time, end_time]`. P will be in the range `[0, 100]`.
    *   **Variance:** Calculate the variance of values across all sensors for data points within a specified time window `[start_time, end_time]`.

3.  **Time Window Handling:** The system should efficiently handle queries with different time windows. Older data points (older than a certain configurable `MAX_RETENTION_TIME`) can be discarded to manage memory usage.

**Constraints:**

*   **Number of Sensors (N):** `1 <= N <= 10^5`
*   **Data Stream Rate:** Up to `10^6` data points per second.
*   **Value Range:** `-10^9 <= value <= 10^9`
*   **Timestamp Range:** Unix timestamps (seconds).
*   **Time Window Range:** The difference between `end_time` and `start_time` can range from milliseconds to days.
*   **Memory Limit:** Your system has a limited memory footprint (e.g., 1GB). Exceeding this limit will result in failure. You need to carefully consider which data to store and how to store it.
*   **Latency:** Queries for aggregate statistics must be processed within a reasonable time frame. The target latency will be defined with test cases (e.g., median calculation should be faster than 5 seconds).
*   **Accuracy:** Due to the limitations of real-time processing and memory constraints, you might need to use approximate algorithms for calculating statistics like median and percentiles. However, the accuracy should be within a specified tolerance (e.g., median should be within 1% of the actual median).

**Considerations:**

*   **Data Structures:** Choosing the right data structures is crucial for performance. Consider using data structures optimized for streaming data, range queries, and approximate calculations.
*   **Concurrency:** The system should be able to handle concurrent ingestion of data and queries for statistics.
*   **Optimization:** Explore techniques like sampling, bucketing, or sketching to reduce memory usage and improve query performance.  Trade-offs between accuracy and performance need to be carefully considered and implemented.
*   **Error Handling:** Robust error handling is essential, especially when dealing with large data streams.

**Your Task:**

Design and implement a Go program that efficiently ingests data from the sensor network and provides the required statistical measures within the given constraints. You need to balance memory usage, latency, and accuracy to create a practical and scalable solution.
