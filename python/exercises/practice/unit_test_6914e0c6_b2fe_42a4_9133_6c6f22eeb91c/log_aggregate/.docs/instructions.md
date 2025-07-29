Okay, here's a challenging coding problem description designed for a high-level programming competition, aiming for LeetCode Hard difficulty.

**Project Name:** `ScalableLogAggregation`

**Question Description:**

You are tasked with designing a scalable and efficient log aggregation system.  Imagine you are receiving log streams from a massive distributed system, potentially thousands of servers each producing gigabytes of logs daily.  These logs are unstructured text data.

Your system must perform the following tasks:

1.  **Ingestion:**  Accept log entries from various sources (assume a simple string format for each log entry).
2.  **Parsing and Indexing:**  Parse each log entry to identify key fields (e.g., timestamp, log level, source IP, message).  You must build an *inverted index* on these fields to support efficient searching. For simplicity, assume that the key fields are delimited by '|'. For example, a log entry might look like: `2024-10-27T10:00:00Z|ERROR|192.168.1.10|Failed to connect to database`. The key fields are `timestamp`, `log level`, `source IP`, and `message`.
3.  **Querying:**  Support complex queries across multiple fields using boolean operators (AND, OR, NOT).  Queries should be performant even with billions of log entries.
4.  **Retention Policy:**  Implement a configurable retention policy.  Logs older than a specified duration (e.g., 7 days, 30 days) must be automatically purged from the system.  This purging must be done efficiently without impacting query performance significantly.
5.  **Real-time Aggregation:** Provide a mechanism for real-time aggregation of log events based on different criteria. For example, count the number of ERROR level logs per source IP address within a given time window.

**Constraints and Requirements:**

*   **Scalability:** The system must be able to handle a massive influx of log data and scale horizontally to accommodate increasing load. Consider how you would partition the data.
*   **Efficiency:**  Queries should return results in a reasonable time, even with billions of log entries.  The inverted index must be optimized for fast lookups.
*   **Memory Management:**  Minimize memory usage.  Consider using techniques like bloom filters or approximate data structures to optimize memory consumption.  Disk-based indexing may be necessary.
*   **Fault Tolerance:** The system should be resilient to failures.  Consider data replication or other fault-tolerance mechanisms.
*   **Concurrency:**  The system must be able to handle concurrent ingestion and querying requests.
*   **Retention Policy:** Efficiently removes outdated logs without impacting performance.
*   **Limited Resources:** Assume you have limited memory (e.g., 8GB) and processing power. You might not be able to load the entire dataset into memory.  Disk I/O should be minimized.
*   **Unstructured Data Robustness:** Your parsing logic should be robust to handle variations in log formatting and potential errors. You can assume a basic delimiter-based structure, but consider potential missing fields or malformed entries.

**Input Format:**

*   Log entries are provided as strings.

**Output Format:**

*   For queries, return a list of log entries that match the specified criteria.
*   For aggregation, return the aggregated results in a suitable format (e.g., a dictionary or list of tuples).

**Evaluation Criteria:**

*   Correctness: Does the system return the correct results for queries and aggregations?
*   Performance: How fast are queries and aggregations?
*   Scalability: How well does the system scale to handle increasing load?
*   Memory Usage: How much memory does the system consume?
*   Code Quality: Is the code well-structured, readable, and maintainable?
*   Handling of Edge Cases and Error Conditions: How well does the system handle invalid input or unexpected events?

This problem requires careful consideration of data structures, algorithms, and system design principles to create a robust and efficient log aggregation system.  Good luck!
