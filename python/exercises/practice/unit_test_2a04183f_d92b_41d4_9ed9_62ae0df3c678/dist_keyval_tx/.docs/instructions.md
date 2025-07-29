## Question: Distributed Key-Value Store with Transactional Consistency

**Description:**

You are tasked with designing and implementing a simplified distributed key-value store. This store must support concurrent read and write operations across multiple nodes, while guaranteeing transactional consistency (specifically, ACID properties).  The store uses a simplified Two-Phase Commit (2PC) protocol to achieve this consistency.

**System Architecture:**

The system consists of `N` nodes, each capable of storing key-value pairs.  A client interacts with a "coordinator" node to initiate transactions. The coordinator is responsible for orchestrating the 2PC protocol across the relevant nodes (participants) that store the keys involved in the transaction.

**Data Model:**

*   Keys are strings.
*   Values are strings.

**Operations:**

The system must support the following operations:

1.  `read(key)`: Retrieves the value associated with the given key. If the key does not exist, return `None` (or an equivalent representation).

2.  `write(key, value)`: Writes the given value to the key.

3.  `begin_transaction()`: Initiates a new transaction and returns a transaction ID (TID).

4.  `commit_transaction(TID)`: Attempts to commit the transaction with the given TID.

5.  `abort_transaction(TID)`: Aborts the transaction with the given TID.

**Constraints and Requirements:**

*   **Atomicity:** A transaction must be either entirely committed or entirely aborted. No partial updates are allowed.

*   **Consistency:** Transactions must maintain data integrity.  You can assume that each node stores data consistently on its own. Your task is to ensure consistency *across* nodes during concurrent transactions.

*   **Isolation:** Concurrent transactions must be isolated from each other.  A read operation should always see a consistent state (either before or after a committed transaction, but not a partially committed transaction).  You can implement Serializable isolation level using locking.

*   **Durability:** Once a transaction is committed, its changes must be durable. (Simulate durability by logging the transaction to a file before committing).

*   **Concurrency:** The system must handle concurrent read and write operations from multiple clients efficiently.

*   **Node Failure:**  Assume nodes can fail (crash) at any time. The system must be able to recover from node failures and maintain data consistency. (Simulate node failure by interrupting the program during different phases of the 2PC protocol. After restart, the system should be able to resolve the transaction status by checking the logs).

*   **Optimization:**  Minimize latency for read operations. Design your data structures and algorithms to efficiently handle a large number of concurrent transactions.

*   **Distributed Environment:**  You can simulate the distributed environment using threads or processes on a single machine. Communication between nodes can be implemented using shared memory, queues, or RPC mechanisms.

*   **Transaction ID (TID) generation:** Implement a mechanism for generating unique transaction IDs.

*   **2PC Implementation Details:** Implement the 2PC protocol as follows:
    *   **Phase 1 (Prepare):** The coordinator sends a "prepare" message to all participant nodes involved in the transaction. Each participant attempts to prepare the transaction (e.g., by acquiring locks, writing to a temporary log). If successful, it sends a "vote-commit" message to the coordinator; otherwise, it sends a "vote-abort" message.
    *   **Phase 2 (Commit/Abort):**
        *   If the coordinator receives "vote-commit" messages from all participants, it sends a "commit" message to all participants.
        *   If the coordinator receives a "vote-abort" message from any participant or if a timeout occurs, it sends an "abort" message to all participants.
        *   Participants then either commit or abort the transaction based on the coordinator's decision.

*   **Logging:**  Implement logging at each node to record transaction state changes. These logs are crucial for recovery after node failures. Log at least the following: `Prepare`, `Commit`, `Abort`. You may log more as necessary.

**Scalability:** While you don't need to physically deploy this across multiple machines, consider how your design would scale if you had to add more nodes. Discuss the potential bottlenecks and how you might address them.

**Assumptions:**

*   Network communication is reliable (no message loss or corruption, but nodes can fail).
*   Nodes have synchronized clocks (sufficient for timeout mechanisms).

**Difficulty:** Hard (LeetCode Hard)

This problem requires a solid understanding of distributed systems concepts, concurrency control, and fault tolerance. It challenges the solver to design a robust and efficient solution that meets the specified constraints and requirements.
