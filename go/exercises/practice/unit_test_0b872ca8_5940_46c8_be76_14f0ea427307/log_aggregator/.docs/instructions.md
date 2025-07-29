Okay, challenge accepted! Here's a problem designed to test a Go programmer's skills in algorithm design, data structure usage, and optimization.

### Project Name

`ScalableLogAggregator`

### Question Description

You are tasked with building a scalable log aggregation service.  This service needs to ingest logs from a massive number of distributed applications, process them, and make them available for querying.

Specifically, the service must:

1.  **Ingest Logs:**  Receive log entries from a potentially very large number of applications. Each log entry consists of:
    *   A timestamp (Unix epoch in nanoseconds, `int64`).
    *   A log level (string: "DEBUG", "INFO", "WARN", "ERROR", "FATAL").
    *   A message (string, can be arbitrarily long).
    *   An application ID (string, uniquely identifies the application emitting the log).

2.  **Store Logs Efficiently:** Store the ingested logs in a way that allows for efficient querying.  Consider the potential volume of log data and design your storage appropriately.

3.  **Query Logs:**  Provide an endpoint to query logs based on:
    *   Application ID (exact match).
    *   Time range (inclusive start and end timestamps, Unix epoch in nanoseconds, `int64`).
    *   Log levels (a list of log levels to include in the results).  If the list is empty, include all log levels.

4.  **Real-time Aggregation:** Provide an endpoint to get the total number of logs for each log level in a specific time range.

**Constraints and Requirements:**

*   **Scalability:** The service must be able to handle a very high volume of log entries (millions per second) and a large number of concurrent queries.
*   **Concurrency:** The service must be thread-safe and handle concurrent requests efficiently.  Pay close attention to potential race conditions.
*   **Memory Usage:** Minimize memory usage.  The service should not consume excessive memory, especially when dealing with a large number of applications and log entries.
*   **Latency:** Queries should be executed with minimal latency.  Optimize your data structures and algorithms to achieve this.
*   **Real-time Aggregation:** Real-time aggregation endpoint should respond quickly, even under high load.
*   **Error Handling:**  Handle invalid input gracefully and return appropriate error codes.
*   **Data Consistency:** Ensure data consistency. No data loss or data corruption.
*   **Limited Resources:** Assume you have limited resources (e.g., memory, CPU cores). You have to design the system carefully so that it can handle large number of applications, logs and queries with the given resources.

**Considerations:**

*   Think about data structures that are well-suited for time-based queries and efficient storage.  Consider in-memory data structures and how they might interact with persistence mechanisms (if needed).
*   Consider using goroutines and channels for concurrency.
*   Think about how you would handle a large number of unique application IDs.
*   Explore different approaches for real-time aggregation and their performance characteristics.
*   Think about how to avoid full table scans during the queries.

**Bonus (Optional):**

*   Implement a persistence mechanism (e.g., using a simple file-based storage or a more robust database).
*   Implement a simple UI to visualize the logs and aggregations.
*   Add support for additional query parameters (e.g., searching for specific keywords in the log message).

This problem requires a good understanding of data structures, algorithms, concurrency, and system design principles. Good luck!
