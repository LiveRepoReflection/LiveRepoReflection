## Question: Distributed Transactional Key-Value Store with Conflict Resolution

**Problem Description:**

You are tasked with designing and implementing a distributed transactional key-value store. This store must handle concurrent read and write operations from multiple clients while maintaining data consistency and durability. Due to network partitions and eventual consistency requirements, conflicts might arise when updating the same key from different clients concurrently. Your system must detect and resolve these conflicts using a custom conflict resolution strategy.

**Specific Requirements:**

1.  **Data Model:** The store holds string keys and string values.
2.  **Transactions:** Clients can initiate transactions that allow them to perform multiple read and write operations atomically. Transactions must support ACID properties (Atomicity, Consistency, Isolation, Durability).
3.  **Concurrency:** The store must handle concurrent transactions from multiple clients efficiently. Locking mechanisms (optimistic or pessimistic) are expected to manage concurrent access to data.
4.  **Distribution:** The store consists of multiple nodes. Key-value pairs are distributed across these nodes (you can assume a consistent hashing scheme is used for key distribution).
5.  **Conflict Detection and Resolution:** When concurrent transactions modify the same key, a conflict is detected. Implement a versioning scheme (e.g., vector clocks or timestamps) to track changes to the data.  You must define a conflict resolution function that takes the conflicting values and their associated versions as input and returns a single, merged value. The conflict resolution function *must* be deterministic. If no resolution is possible, the function should return an error indicating a non-resolvable conflict.
6.  **Durability:** Committed transactions must be durable. Implement a write-ahead log (WAL) to ensure data persistence in case of node failures.
7.  **Fault Tolerance:** The system should be resilient to node failures. Data replication across multiple nodes is required to provide fault tolerance. (At least factor of 3).
8.  **API:** Implement the following operations:

    *   `begin_transaction()`: Starts a new transaction and returns a transaction ID.
    *   `read(transaction_id, key)`: Reads the value associated with the given key within the specified transaction.
    *   `write(transaction_id, key, value)`: Writes the given value to the specified key within the transaction.
    *   `commit_transaction(transaction_id)`: Commits the transaction. This should persist all changes made within the transaction to the store.
    *   `abort_transaction(transaction_id)`: Aborts the transaction, discarding all changes made within it.

**Constraints:**

*   The number of nodes in the distributed system can be up to 100.
*   The maximum size of a key is 256 bytes.
*   The maximum size of a value is 1 MB.
*   The system should be able to handle at least 10,000 transactions per second.
*   The latency of read and write operations should be minimized.
*   The conflict resolution function must be efficient and should not introduce significant overhead.
*   You must use Rust's concurrency primitives (e.g., `Mutex`, `RwLock`, `Arc`, channels) effectively to ensure thread safety and efficient resource utilization.

**Optimization Requirements:**

*   Optimize for both throughput (transactions per second) and latency.
*   Minimize the overhead of conflict detection and resolution.
*   Consider caching strategies to improve read performance.
*   Implement efficient data serialization and deserialization for network communication and persistence.

**Evaluation Criteria:**

*   Correctness (all test cases pass)
*   Performance (throughput and latency)
*   Fault tolerance
*   Code quality (readability, maintainability, and use of Rust best practices)
*   Efficiency of the conflict resolution strategy.
*   Adherence to ACID properties.
