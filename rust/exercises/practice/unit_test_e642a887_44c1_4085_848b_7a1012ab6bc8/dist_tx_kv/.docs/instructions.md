## Problem Title: Distributed Transactional Key-Value Store

### Question Description

You are tasked with designing and implementing a distributed transactional key-value store. This system must handle concurrent read and write operations across multiple nodes while guaranteeing ACID (Atomicity, Consistency, Isolation, Durability) properties for transactions.

The system consists of `N` nodes, each identified by a unique integer ID from `0` to `N-1`.  Clients can connect to any node to initiate transactions. A transaction can involve multiple key-value pairs, potentially spread across different nodes.

**Functionality:**

1.  **`begin_transaction()`:** Initiates a new transaction. Returns a unique transaction ID (TID).

2.  **`read(TID, key)`:** Reads the value associated with a given `key` within the context of a specific transaction `TID`. If the `key` does not exist, return `None`.

3.  **`write(TID, key, value)`:** Writes a `value` to a given `key` within the context of a specific transaction `TID`. If the `key` already exists within the transaction, overwrite the previous value.

4.  **`commit_transaction(TID)`:** Attempts to commit the transaction associated with `TID`. If successful (all nodes involved agree), the changes become permanent. Returns `true` on success, `false` on failure (e.g., due to a conflict with another transaction, or a node being unavailable).

5.  **`rollback_transaction(TID)`:** Aborts the transaction associated with `TID`, discarding any changes made within the transaction.

**Constraints and Requirements:**

*   **Atomicity:** A transaction must be either entirely committed, or entirely rolled back. Partial commits are not allowed.

*   **Consistency:** The system must always be in a valid state. Committing a transaction moves the system from one valid state to another.

*   **Isolation:** Concurrent transactions must not interfere with each other. The result of concurrent transactions should be the same as if they were executed serially. You must implement a suitable concurrency control mechanism (e.g., two-phase locking, optimistic concurrency control, etc.).

*   **Durability:** Once a transaction is committed, the changes must be persistent, even in the face of node failures. Consider replication or other durability mechanisms.

*   **Scalability:** The system should be designed to handle a large number of concurrent transactions and a large dataset.

*   **Fault Tolerance:** The system should be resilient to node failures. Transactions involving failed nodes should be able to be rolled back cleanly. If a node recovers, it should be able to rejoin the system.

*   **Performance:**  Optimize for low latency reads and writes, and efficient transaction commit/rollback. Minimize network communication.

*   **Key Distribution:** You need to determine how to distribute keys across the `N` nodes. Consider techniques like consistent hashing.

*   **Conflict Resolution:** You need to implement a strategy to detect and resolve conflicts between concurrent transactions. Deadlock avoidance or detection and resolution are required.

*   **Data Size:** Values can be up to 1MB.

*   **Number of Nodes:** `N` can be up to 100.

*   **Concurrency:** The system should support hundreds of concurrent transactions.

**Implementation Details:**

You are free to choose the specific data structures and algorithms to implement the system. However, you must clearly explain your design choices and justify their suitability for the given requirements. Focus on the core logic and concurrency control mechanisms. You don't need to implement full network communication (you can simulate network calls), but you should design your system with network communication in mind.

**Considerations:**

*   **Two-Phase Commit (2PC):**  A common algorithm for distributed transactions.  Consider the trade-offs of 2PC, including its vulnerability to blocking failures, and explore potential mitigation strategies.
*   **Paxos/Raft:**  Consider how a consensus algorithm could be used to ensure consistency, especially for metadata (e.g., transaction status).

This problem requires careful consideration of distributed systems principles, concurrency control, fault tolerance, and performance optimization. Good luck!
