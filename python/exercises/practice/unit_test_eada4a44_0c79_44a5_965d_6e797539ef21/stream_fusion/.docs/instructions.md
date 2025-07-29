## Question: Parallel Data Stream Processor

**Project Name:** `StreamFusion`

**Question Description:**

You are tasked with designing and implementing a system for processing a high-volume, continuous stream of numerical data in real-time. The data stream consists of a sequence of numerical events, each containing a timestamp and a floating-point value. Your system must perform several complex calculations on this stream while adhering to strict latency and resource constraints.

Specifically, your system must:

1.  **Ingest and Buffer:** Efficiently ingest the incoming data stream. Due to unpredictable network conditions, the stream might experience bursts of data followed by periods of inactivity. Implement a buffering mechanism to handle these fluctuations gracefully. The buffer has a limited capacity. When the buffer is full, older events must be discarded to make space for new events (First-In-First-Out eviction policy).

2.  **Sliding Window Aggregation:** Maintain a sliding window of fixed size `W` (in terms of the *number* of events, not time) over the buffered data. For each new event ingested, compute the following aggregate statistics over the current window:
    *   **Mean:** The average of the floating-point values in the window.
    *   **Variance:** The statistical variance of the floating-point values in the window.
    *   **Median:** The median of the floating-point values in the window. Note: This must be computed efficiently.

3.  **Anomaly Detection:** Implement a simple anomaly detection mechanism. A data point is considered an anomaly if its value deviates significantly from the mean of the current window. Specifically, a data point is an anomaly if its absolute difference from the mean is greater than `K` times the standard deviation of the window (where standard deviation is the square root of the variance). Report all anomalies detected.

4.  **Parallel Processing:** The data stream is extremely high-volume, and the calculations are computationally intensive. Design your system to leverage parallel processing to minimize latency. You must utilize multi-threading or multi-processing (choose the most appropriate for your design) to distribute the workload across multiple CPU cores.

5.  **Bounded Resources:** The system operates in a resource-constrained environment. Memory usage must be carefully managed. Avoid unnecessary data duplication and optimize data structures for memory efficiency. The number of threads/processes you create should also be bounded to prevent excessive context switching overhead.

6.  **Real-time Constraints:** The system must process data in real-time. The latency between data ingestion and anomaly detection should be minimized. Your design should prioritize minimizing the average processing time per event.

7.  **Data Structure Choice:** Select appropriate data structures for buffering the stream, maintaining the sliding window, and computing the aggregates. Justify your choice based on efficiency and memory usage considerations. The use of standard library data structures is encouraged, but you may need to adapt or combine them to meet the performance requirements.

8.  **Error Handling:** Implement robust error handling to deal with potential issues such as invalid data, numerical instability (e.g., division by zero when calculating variance), and thread synchronization problems.

**Input:**

The input to your system will be a sequence of events provided through a generator or an input stream. Each event is represented as a tuple `(timestamp, value)`, where `timestamp` is an integer representing the time the event occurred and `value` is a float representing the event's numerical value.

**Output:**

Your system should output a list of anomalies. Each anomaly should be a tuple `(timestamp, value)`, representing the timestamp and value of the anomalous event. The anomalies should be reported in the order they are detected.

**Constraints:**

*   `1 <= W <= 100,000` (Window size)
*   `0 <= K <= 5` (Anomaly threshold multiplier)
*   The data stream can contain up to `1,000,000` events.
*   Timestamps are non-decreasing.
*   Minimize memory usage.
*   Minimize latency. Average processing time per event should be less than X ms (where X will be determined during judging).
*   The number of threads/processes must be limited to a reasonable number (e.g., no more than the number of CPU cores available + 2).

**Evaluation Criteria:**

Your solution will be evaluated based on the following criteria:

*   **Correctness:** The accuracy of the anomaly detection results.
*   **Performance:** The average processing time per event (latency).
*   **Memory Usage:** The peak memory consumption of the system.
*   **Code Quality:** The clarity, maintainability, and organization of your code.
*   **Scalability:** How well your system scales to handle larger data streams and window sizes.
*   **Robustness:** How well your system handles errors and unexpected input.

This problem requires a combination of algorithmic thinking, data structure knowledge, and parallel programming expertise to implement a high-performance, real-time data stream processing system. Good luck!
