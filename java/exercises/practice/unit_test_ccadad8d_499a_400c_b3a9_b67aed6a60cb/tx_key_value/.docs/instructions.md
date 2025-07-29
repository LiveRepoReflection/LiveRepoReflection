Okay, here's the problem statement:

**Problem Title: Distributed Transactional Key-Value Store with Snapshot Isolation**

**Problem Description:**

You are tasked with designing and implementing a highly scalable, distributed key-value store that supports ACID properties, specifically focusing on snapshot isolation for concurrent transactions. The system must handle a large number of concurrent read and write requests across multiple nodes in a distributed environment.

**System Requirements:**

1.  **Data Model:** The key-value store should support string keys and string values.
2.  **API:** Implement the following API:

    *   `get(key, transaction_id)`: Retrieves the value associated with a given key within the context of a specific transaction.  If the key does not exist or is not visible within the transaction's snapshot, return `null`.
    *   `put(key, value, transaction_id)`:  Sets the value for a given key within the context of a specific transaction. Overwrites any existing value.
    *   `begin_transaction()`: Starts a new transaction and returns a unique `transaction_id`.
    *   `commit_transaction(transaction_id)`:  Commits the transaction associated with the given `transaction_id`. All changes made within the transaction become visible to subsequent transactions.
    *   `abort_transaction(transaction_id)`: Aborts the transaction associated with the given `transaction_id`. All changes made within the transaction are discarded.

3.  **Snapshot Isolation:** Implement snapshot isolation. Each transaction operates on a consistent snapshot of the data as it existed at the time the transaction started. This means a transaction will not see changes made by other concurrent transactions until those transactions are committed.

4.  **Distribution:** The key-value store should be distributed across multiple nodes. You can assume a simple consistent hashing scheme is used to distribute keys across nodes.  You do not need to implement the consistent hashing itself, but your implementation must be able to handle the concept of key distribution. Assume a `getNodeForKey(key)` function exists which deterministically returns the node responsible for a given key.

5.  **Concurrency:** The system must handle a high degree of concurrent transactions.

6.  **Durability:**  Committed data must be durable.  Consider using a write-ahead log (WAL) or similar mechanism to ensure durability.  *You do not need to implement full crash recovery*, but the design should clearly show how WAL would be used.

7.  **Scalability:** The system should be designed to scale horizontally by adding more nodes.

**Constraints:**

1.  **Transaction ID:** Transaction IDs are globally unique and monotonically increasing. You can assume a centralized transaction ID generator exists.
2.  **Memory:**  Each node has limited memory.  Do not assume you can load the entire dataset into memory.
3.  **Network:** Network communication between nodes is reliable but may have variable latency.
4.  **Timeouts:** Operations should have reasonable timeout mechanisms to handle failures and prevent indefinite blocking.
5.  **Conflict Resolution:** You are allowed to assume a single writer for each key at any given time to simplify conflict resolution.
6.  **No External Databases:** You cannot use external databases (e.g., MySQL, PostgreSQL, MongoDB) as part of your implementation. You must implement the key-value store from scratch.

**Evaluation Criteria:**

*   **Correctness:** The implementation must correctly implement the API and adhere to snapshot isolation.
*   **Concurrency Handling:** The system must handle concurrent transactions efficiently and without data corruption.
*   **Scalability:** The design should be scalable horizontally.
*   **Durability:** The design should clearly address durability.
*   **Code Quality:**  Code should be well-structured, readable, and maintainable.
*   **Efficiency:**  Operations should be reasonably efficient in terms of time and memory usage. Consider the trade-offs between different data structures and algorithms.

**Bonus:**

*   Implement basic crash recovery based on the WAL.
*   Implement a mechanism for garbage collecting old snapshots.

This is a demanding problem that requires a solid understanding of distributed systems principles, concurrency control, and data structures. Good luck!
