Okay, here's a challenging problem designed to test a competitor's skills in algorithm design, optimization, and data structure manipulation.

## Problem: Scalable Distributed Transaction Log Aggregation

**Question Description:**

You are building a highly scalable distributed system that processes a massive stream of transactions. Each transaction is represented as a JSON object with a unique transaction ID (a UUID string), a timestamp (in milliseconds since epoch), and a payload (an arbitrary JSON object).

The system consists of numerous worker nodes, each independently processing a subset of the total transaction stream. Each worker node maintains a local, in-memory transaction log, which is periodically flushed to persistent storage (e.g., a distributed file system). These local logs are unordered and may contain duplicate transactions.

Your task is to design and implement a system that efficiently aggregates these distributed, potentially overlapping transaction logs to provide a consistent, globally ordered view of the transactions within a specified time window.

**Specifically, you need to implement the following:**

1.  **Data Ingestion:** Design a mechanism to ingest transaction logs from multiple worker nodes.  Assume you have a function `fetch_log(worker_id)` that returns a list of transaction JSON objects from a given worker.

2.  **Deduplication:** Implement a deduplication strategy to handle duplicate transactions reported by different worker nodes. The transaction with the *earliest* timestamp should be considered the canonical version.

3.  **Time Window Filtering:** Filter the aggregated transactions to include only those that fall within a given start and end timestamp (inclusive).

4.  **Global Ordering:**  Produce a globally ordered list of transactions within the time window, sorted by timestamp in ascending order.

5.  **Memory Constraints:** The system has limited memory and *cannot* store the entire transaction history in memory. The solution should be designed to handle a continuous, unbounded transaction stream.

6.  **Scalability:** The system must be scalable to handle a large number of worker nodes and a high transaction rate. Consider the potential for parallelism and distributed processing.

7.  **Performance:** Your solution should be optimized for performance.  Consider time and space complexity.  Avoid unnecessary iterations and data copies.

**Input:**

*   `worker_ids`: A list of strings representing the IDs of the worker nodes to query.
*   `start_time`: An integer representing the start timestamp (in milliseconds since epoch) of the time window.
*   `end_time`: An integer representing the end timestamp (in milliseconds since epoch) of the time window.

**Output:**

*   A list of transaction JSON objects, ordered by timestamp (ascending), containing only unique transactions within the specified time window.  Each transaction should contain the transaction ID, timestamp, and payload. The transaction with the earliest timestamp must be chosen in the case of duplicates.

**Constraints:**

*   The number of worker nodes can be very large (e.g., hundreds or thousands).
*   The transaction rate can be very high (e.g., millions of transactions per second).
*   The available memory is limited, and you cannot store all transactions in memory at once.
*   You are free to use standard Python libraries and data structures.
*   Assume the `fetch_log(worker_id)` function is provided and handles network communication with the worker node. You do not need to implement it.
*   The solution must be thread-safe if using parallelism.

**Scoring:**

The solution will be evaluated based on the following criteria:

*   **Correctness:** The solution must produce the correct output for all valid inputs.
*   **Efficiency:** The solution must be efficient in terms of both time and space complexity.
*   **Scalability:** The solution must be able to handle a large number of worker nodes and a high transaction rate.
*   **Code Quality:** The solution must be well-structured, readable, and maintainable.

This problem challenges candidates to think critically about distributed systems, data deduplication, time-series data processing, and performance optimization. Good luck!
