## Project Name

`Distributed Key-Value Store with Transactional Consistency`

## Question Description

You are tasked with implementing a simplified, distributed key-value store with transactional consistency guarantees. This system will consist of multiple nodes, each capable of storing data.  The challenge lies in ensuring that concurrent operations across these nodes maintain ACID (Atomicity, Consistency, Isolation, Durability) properties, particularly Atomicity and Consistency.

**System Requirements:**

1.  **Data Model:** The key-value store should support string keys and string values.
2.  **Basic Operations:** Implement the following operations:
    *   `put(key: String, value: String)`: Stores the key-value pair.
    *   `get(key: String)`: Retrieves the value associated with the key.  Returns `None` if the key doesn't exist.
    *   `delete(key: String)`: Removes the key-value pair. Returns `true` if deleted, `false` if the key doesn't exist.
3.  **Distribution:** The system should consist of `N` nodes (where `N` is configurable, e.g., between 3 and 7). Key-value pairs should be distributed across these nodes using a consistent hashing scheme (you can implement your own simple version).  Consider a virtual node setup to ensure even distribution.
4.  **Transactions:**  Implement support for atomic transactions.  A transaction should allow multiple `put`, `get`, and `delete` operations to be performed as a single unit of work.  Implement `begin_transaction()`, `commit_transaction()`, and `rollback_transaction()` methods.  Transactions must be isolated from each other.
5.  **Consistency:**  Guarantee strong consistency across all nodes.  After a transaction commits, all nodes must eventually see the same state. Linearizability is not a strict requirement, but eventual consistency isn't sufficient.
6.  **Fault Tolerance:**  The system should tolerate the failure of up to `(N-1)/2` nodes without losing data or compromising consistency. Use a consensus algorithm like Paxos or Raft (simplified versions are acceptable and encouraged) to achieve this.
7.  **Concurrency:**  The system must handle concurrent requests from multiple clients safely and efficiently.  Use appropriate locking or concurrency control mechanisms to prevent data corruption.
8.  **Scalability:**  While a full-blown scalable architecture isn't required, consider design choices that would facilitate future scaling (e.g., sharding, replication).
9.  **Durability:** Once a transaction is committed, the data must be persisted to disk (simulated persistence is acceptable using files). The design should consider how to recover from node failures and ensure data is not lost.
10. **API Design** The API should be asynchronous, leveraging Rust's async/await features for non-blocking operation.

**Constraints:**

*   **Resource Limits:**  Memory usage should be reasonable. Avoid unnecessary data duplication.
*   **Latency:**  Operations should complete within a reasonable time frame. Optimize for common use cases.
*   **Complexity:**  Keep the implementation as simple as possible while meeting the requirements.  Favor clear and maintainable code over premature optimization.
*   **Dependencies:**  Minimize external dependencies.  Focus on using Rust's standard library and a minimal set of well-established crates.
*   **Testing:**  Provide comprehensive unit tests and integration tests to verify the correctness and robustness of your implementation. Include tests for fault tolerance scenarios.
*   **Error Handling:** Handle potential errors gracefully. Return informative error messages to the client.

**Bonus Challenges:**

*   Implement a mechanism for detecting and resolving deadlocks.
*   Add support for more complex data types (e.g., lists, sets).
*   Implement a monitoring system to track the health and performance of the nodes.
*   Implement dynamic reconfiguration to allow nodes to be added or removed from the cluster without downtime.

This problem requires a solid understanding of distributed systems concepts, concurrency, and Rust's async programming model. It also demands careful attention to detail and a rigorous testing strategy. Good luck!
