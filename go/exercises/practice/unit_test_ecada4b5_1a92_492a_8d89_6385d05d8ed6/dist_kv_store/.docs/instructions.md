Okay, here's a problem designed to be challenging for a Go coding competition, focusing on graph algorithms, concurrency, and optimization.

## Problem: Distributed Transactional Key-Value Store

**Description:**

You are tasked with designing and implementing a distributed, transactional key-value store. The store consists of multiple nodes that communicate over a network. Each node stores a subset of the key-value pairs. The system must support ACID (Atomicity, Consistency, Isolation, Durability) properties for transactions.

**Functionality:**

The key-value store must support the following operations within a transaction:

1.  **`Get(key string) (string, error)`**: Retrieves the value associated with a given key. If the key does not exist, return an appropriate error.
2.  **`Put(key string, value string) error`**:  Sets the value associated with a given key.
3.  **`Delete(key string) error`**: Deletes the key-value pair associated with a given key. If the key does not exist, return an appropriate error.

Additionally, it must support:

4.  **`BeginTransaction() (TransactionID, error)`**: Starts a new transaction and returns a unique `TransactionID`.
5.  **`CommitTransaction(TransactionID) error`**: Attempts to commit a transaction. If successful, all changes made within the transaction are made visible.
6.  **`RollbackTransaction(TransactionID) error`**: Rolls back a transaction, discarding all changes made within it.

**Constraints & Requirements:**

1.  **Distribution:** The data is distributed across multiple nodes. You must implement a mechanism to locate the node responsible for a given key (e.g., consistent hashing).
2.  **Concurrency:** Multiple transactions can run concurrently. You must ensure proper isolation to prevent data corruption and ensure serializability.
3.  **Atomicity:** All operations within a transaction must either succeed or fail as a whole.
4.  **Durability:** Once a transaction is committed, the changes must be persisted and survive node failures.
5.  **Fault Tolerance:** The system should be able to tolerate the failure of a minority of nodes without losing data or compromising availability.  Assume a crash-fault tolerant model.
6.  **Scalability:** The system should be designed to scale horizontally by adding more nodes.
7.  **Performance:** The system should provide reasonable performance for both read and write operations.  Minimize latency and maximize throughput.
8.  **Conflict Resolution:** Design a mechanism to handle conflicting writes from concurrent transactions (e.g., optimistic locking, two-phase commit). You must clearly describe your chosen approach.
9.  **Garbage Collection:** Implement a mechanism to clean up aborted or committed transactions to prevent storage from filling up with stale data.
10. **Data Size:** Assume that both keys and values can be relatively large (e.g., up to 1MB).

**Specific Challenges:**

*   Implementing a distributed consensus algorithm (e.g., Raft, Paxos) for transaction commit and rollback.
*   Handling network partitions and node failures gracefully.
*   Optimizing data access patterns to minimize network communication.
*   Choosing appropriate data structures for efficient storage and retrieval.

**Input/Output:**

The core of the solution is the implementation of the key-value store's API (functions described above). A set of concurrent operations will be called against your implementation, testing for correctness, performance, and fault tolerance.  The specific format of the input (e.g., via gRPC or REST) is left to your design.

**Judging Criteria:**

*   **Correctness:**  Does the system correctly implement the ACID properties?
*   **Performance:** How quickly can the system process transactions under load?
*   **Scalability:** How well does the system scale as the number of nodes and transactions increases?
*   **Fault Tolerance:** How well does the system handle node failures and network partitions?
*   **Code Quality:** Is the code well-structured, readable, and maintainable?
*   **Design Documentation:** Is the design clearly documented, including the chosen conflict resolution mechanism and consensus algorithm?

This problem requires a solid understanding of distributed systems principles, concurrency control, and data structures.  It is intended to be a challenging and rewarding exercise for experienced Go programmers. Good luck!
