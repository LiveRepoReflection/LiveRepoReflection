## The Distributed Key-Value Store with Range Queries

**Problem Description:**

You are tasked with designing and implementing a distributed key-value store with support for range queries. The store consists of `N` nodes (where `N` can be quite large). Each node is responsible for storing a subset of the key space. Keys are 64-bit unsigned integers (`uint64`).

Your system should support the following operations:

1.  **`Put(key uint64, value string)`**: Stores the given key-value pair in the appropriate node. The placement of the key-value pair should be determined by a consistent hashing scheme (you can implement your own or use an existing library). The value can be up to 1MB in size.

2.  **`Get(key uint64) string`**: Retrieves the value associated with the given key. Returns an empty string if the key does not exist.

3.  **`RangeQuery(startKey uint64, endKey uint64) map[uint64]string`**: Retrieves all key-value pairs where `startKey <= key <= endKey`.  The result should be returned as a map where the key is the `uint64` key and the value is the associated `string`. The range query must be performed in parallel across all relevant nodes to minimize latency.  The range query must handle cases where the `startKey` is greater than the `endKey`, which should then return an empty map.

**Constraints and Requirements:**

*   **Scalability:** Your solution must be able to handle a large number of nodes (e.g., 1000+) and a large amount of data (e.g., terabytes).
*   **Fault Tolerance:** The system should continue to operate correctly even if some nodes fail.  Assume node failures are fail-stop (a node either works correctly or crashes completely). Data replication is **not** required for this problem, meaning data loss is acceptable upon node failure.
*   **Efficiency:**  `Put` and `Get` operations should be fast (ideally, single-hop). `RangeQuery` operations should be optimized to minimize latency, especially when the range spans multiple nodes.
*   **Consistent Hashing:** Implement or use a consistent hashing algorithm to distribute keys across the nodes.  This will help minimize data movement when nodes are added or removed.
*   **Concurrency:**  All operations should be thread-safe and handle concurrent requests correctly.
*   **Data Size:** Values can be up to 1MB in size. Consider how this size limit impacts your design (e.g., network bandwidth, memory usage).
*   **Network Latency:**  Assume that there is non-negligible network latency between nodes.
*   **Handling Overlapping Ranges:** Implement a mechanism that prevents or handles overlapping writes to the same key within the range queries, if the user is doing so. (e.g. last write wins).
*   **No External Databases:** You are not allowed to use external databases (e.g., Redis, Cassandra, etc.) to store the key-value data. The data must be stored in memory or on local disk within each node.
*   **Error Handling:** Implement robust error handling to gracefully handle unexpected situations (e.g., node failures, network errors).

**Bonus Challenges:**

*   Implement dynamic node addition and removal.
*   Implement data replication for improved fault tolerance.
*   Implement a mechanism for detecting and recovering from node failures.
*   Add support for more complex range queries (e.g., queries with predicates).

This problem tests your ability to design and implement a distributed system, considering aspects like scalability, fault tolerance, efficiency, and concurrency. Good luck!
