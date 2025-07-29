## Project Name

```
distributed-key-value-store
```

## Question Description

You are tasked with designing and implementing a simplified, distributed key-value store using Rust. This system must handle concurrent requests, data persistence, and basic fault tolerance.

**Core Requirements:**

1.  **Data Model:** The store holds arbitrary key-value pairs where both keys and values are strings.

2.  **API:** Implement the following operations:
    *   `put(key: String, value: String)`: Stores the `value` associated with the `key`.  Overwrites existing values.
    *   `get(key: String)`: Retrieves the `value` associated with the `key`. Returns `Option<String>`.
    *   `delete(key: String)`: Removes the `key` and its associated `value`.

3.  **Distribution:** The store consists of multiple nodes, each maintaining a subset of the total data.  Implement consistent hashing to distribute keys across nodes. The number of nodes is configurable.

4.  **Concurrency:** The system must handle concurrent `put`, `get`, and `delete` requests efficiently. Use appropriate synchronization primitives to ensure data consistency.

5.  **Persistence:** Implement durable storage of the key-value pairs. On node restart, data must be recoverable.  Use a simple file-based storage mechanism (e.g., appending to a log file).  Consider a checkpointing mechanism to avoid replaying the entire log on startup.

6.  **Fault Tolerance:**  Implement a simple replication scheme for fault tolerance. Each key-value pair should be replicated across N nodes (N is configurable).  Implement read repair: when reading a value, compare the values returned from all replicas. If discrepancies are found, propagate the most recent value to all replicas.

7.  **Communication:** Nodes communicate using TCP. Define a simple protocol for `put`, `get`, and `delete` operations.

**Constraints & Considerations:**

*   **Scalability:** While a full-fledged distributed system requires complex solutions, design your implementation with scalability in mind. Consider the implications of adding more nodes or handling larger datasets. Think about potential bottlenecks.
*   **Latency:**  Minimize latency for `get` operations.
*   **Data Consistency:**  Aim for eventual consistency.  Strong consistency is not required, but the system should strive to minimize inconsistency windows.
*   **Error Handling:**  Implement robust error handling.  Nodes should be able to gracefully handle network errors, disk I/O errors, and other unexpected situations.
*   **Configuration:** Make the number of nodes, replication factor (N), and storage directory configurable.
*   **Performance:**  The solution should provide acceptable performance under moderate load.  Consider the trade-offs between performance and consistency.  A high throughput is expected.
*   **Memory Usage:** Your service must be able to handle a large set of keys, consider memory usage.

**Bonus Challenges:**

*   **Implement a background process for log compaction.**
*   **Add metrics and monitoring (e.g., using `prometheus` and `tracing`).**
*   **Implement a basic command-line interface (CLI) to interact with the store.**

This problem requires a solid understanding of distributed systems concepts, concurrency, data persistence, and networking. It challenges the solver to make design decisions, balance trade-offs, and write robust and efficient Rust code.
