## Problem: Distributed Transactional Key-Value Store with Snapshot Isolation

**Description:**

You are tasked with designing and implementing a simplified distributed key-value store that supports transactional operations with snapshot isolation. This key-value store operates across multiple nodes in a cluster.  Each node is responsible for storing a subset of the keys (using a consistent hashing scheme - assume this is already implemented and available).

**Core Requirements:**

1.  **Transactional Operations:** The system must support atomic transactions. A transaction consists of a series of read and write operations on the key-value store. All operations within a transaction must either succeed as a whole (commit) or fail as a whole (rollback).

2.  **Snapshot Isolation:**  The system must provide snapshot isolation. This means that each transaction operates on a consistent snapshot of the key-value store as it existed at the transaction's start time.  Reads within a transaction should always return the same values, even if other transactions are concurrently modifying the data. Updates made by other transactions should not be visible until the current transaction commits.

3.  **Distributed Operation:** The system should be truly distributed. Reads and writes for a given key may need to involve communication with other nodes in the cluster. You must handle network failures (nodes going down, network partitions) gracefully, while maintaining data consistency and availability as much as possible.

4.  **Concurrency Control:**  Implement a concurrency control mechanism to manage concurrent transactions.  Avoid common problems like lost updates, dirty reads, and non-repeatable reads.

**Detailed Specifications:**

*   **Data Model:** The key-value store stores string keys and string values.
*   **API:** Provide the following API methods:

    *   `begin_transaction()`: Starts a new transaction and returns a unique transaction ID (UUID).
    *   `read(transaction_id, key)`: Reads the value associated with the given key within the specified transaction.  Returns the value, or `null` if the key does not exist in the snapshot visible to the transaction.
    *   `write(transaction_id, key, value)`: Writes the given value to the given key within the specified transaction. These changes are not visible to other transactions until the transaction commits.
    *   `commit_transaction(transaction_id)`: Attempts to commit the transaction. If the commit is successful, all changes made by the transaction become visible.  If the commit fails (e.g., due to conflicts or node failures), the transaction is rolled back and an exception is thrown.
    *   `rollback_transaction(transaction_id)`: Rolls back the transaction, discarding all changes made within the transaction.

*   **Node Failure Handling:** The system should be able to tolerate a reasonable number of node failures without losing data.  Consider how you will handle scenarios where a node involved in a transaction fails before the transaction commits or rolls back.

*   **Consistency:** Even with node failures, the system should strive to maintain data consistency. Avoid scenarios where different nodes have conflicting versions of the same data.

*   **Scalability:**  While not the primary focus, consider how your design could be scaled to handle a large number of keys, values, and transactions.

**Constraints:**

*   **No external database:** You cannot use a traditional external database (e.g., MySQL, PostgreSQL) for storing the data. You must implement the key-value store yourself, using in-memory data structures on each node.
*   **Limited Resources:**  Assume each node has limited memory.  You cannot store the entire key-value store on a single node.
*   **Network Latency:**  Network latency between nodes is significant. Minimize the number of network round trips required for each operation.
*   **Concurrency:** The system will be subjected to a high degree of concurrent reads and writes from multiple clients.
*   **Transaction Size:** Transactions can involve a large number of reads and writes.

**Optimization Considerations:**

*   **Read Performance:**  Optimize for fast read performance, especially for frequently accessed keys.
*   **Write Performance:** Balance write performance with the need for snapshot isolation and data consistency.
*   **Concurrency:** Minimize contention between concurrent transactions.
*   **Space Efficiency:**  Minimize the amount of memory used by the system.

**Bonus Challenges:**

*   **Garbage Collection:** Implement a mechanism for garbage collecting old snapshots that are no longer needed by any active transactions.
*   **Linearizability:** Attempt to provide linearizability in addition to snapshot isolation.
*   **Fault Tolerance:** Enhance fault tolerance by implementing data replication or other fault-tolerance techniques.
*   **Dynamic Membership:** Handle nodes joining and leaving the cluster dynamically.

This problem requires a deep understanding of distributed systems concepts, data structures, algorithms, and concurrency control.  A well-designed solution will be efficient, scalable, and robust to node failures. Good luck!
