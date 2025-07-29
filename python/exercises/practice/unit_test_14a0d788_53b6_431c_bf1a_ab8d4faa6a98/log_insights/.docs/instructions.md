Okay, here's a challenging coding problem designed to be at the LeetCode Hard level, incorporating advanced data structures, optimization requirements, and real-world considerations.

**Problem Title:** Scalable Log Aggregation and Analysis

**Problem Description:**

You are tasked with designing a scalable log aggregation and analysis system. Your system will receive a continuous stream of log entries from a distributed network of servers. Each log entry consists of the following:

*   `timestamp`: An integer representing the epoch timestamp (seconds since Jan 1, 1970 UTC) when the log entry was generated.
*   `server_id`: A string identifying the server that generated the log entry.
*   `log_level`: An integer representing the severity level of the log entry (e.g., 1 for DEBUG, 2 for INFO, 3 for WARNING, 4 for ERROR, 5 for CRITICAL).
*   `message`: A string containing the log message.

Your system should support the following operations with optimal efficiency:

1.  **Ingest Log Entry:** Add a new log entry to the system.
2.  **Query by Time Range:** Given a start and end timestamp (inclusive), retrieve all log entries within that time range, sorted by timestamp in ascending order.
3.  **Query by Server and Log Level:** Given a server ID and a log level, retrieve all log entries from that server with a log level greater than or equal to the given log level, sorted by timestamp in ascending order.
4.  **Top K Frequent Messages:** Given a time range and an integer 'k', return the 'k' most frequent log messages within that time range, along with their counts, sorted by frequency in descending order. If frequencies are the same, sort by message (lexicographically ascending).

**Constraints:**

*   The number of log entries can be extremely large (billions).
*   The system should be designed for high read and write throughput.
*   Memory usage should be optimized to avoid out-of-memory errors.
*   The queries should be answered as quickly as possible.
*   The `timestamp` values are monotonically increasing, but not necessarily unique (multiple logs can have the same timestamp).
*   Server IDs are strings of alphanumeric characters and underscores, with maximum length 20.
*   Log messages are strings of any character with maximum length 200.
*   'k' for the Top K Frequent Messages query will always be a positive integer.
*   The solution must be implemented in Python.

**Evaluation:**

Your solution will be evaluated based on the following criteria:

*   **Correctness:** The system should return accurate results for all queries.
*   **Performance:** The system should handle a large volume of log entries and respond to queries efficiently.  Pay particular attention to the time complexity of each operation.
*   **Memory Usage:** The system should minimize memory consumption.
*   **Code Quality:** The code should be well-structured, readable, and maintainable.
*   **Scalability:** The design should be able to handle increasing data volumes and query loads.

**Hints (But Don't Give it Away):**

*   Consider using a combination of appropriate data structures to optimize different operations. Think about how to leverage properties of the data (e.g. monotonic timestamps).
*   Think about trade-offs between memory usage and query performance.
*   Consider using external libraries or modules if they can significantly improve performance or memory usage.  Be mindful of dependencies when submitting your code.
*   For the "Top K Frequent Messages" query, think about how to efficiently track message frequencies within a given time range.  Heap-based solutions can be useful.
*   Consider the indexing strategy to enhance the query performance.

Good luck! This problem is designed to be very challenging and requires a deep understanding of data structures, algorithms, and system design principles.
