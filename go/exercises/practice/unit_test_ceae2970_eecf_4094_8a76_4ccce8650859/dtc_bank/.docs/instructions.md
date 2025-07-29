## Problem: Distributed Transaction Coordinator

### Question Description

You are tasked with implementing a distributed transaction coordinator (DTC) in Go for a simplified banking system. This system consists of multiple independent bank services (nodes), each responsible for managing a subset of user accounts and their balances. A single transaction might involve transferring funds between accounts located on different bank services.

Your DTC must ensure Atomicity, Consistency, Isolation, and Durability (ACID properties) for these distributed transactions. The focus of this problem is achieving atomicity and durability in the face of network failures and service crashes.

**Simplified System Architecture:**

*   **Bank Services (Nodes):** Each node maintains a local database of accounts and their balances. They expose an API to:
    *   `Prepare(transactionID, operations)`: Checks if the node can perform the operations (e.g., sufficient balance). Returns `Prepared`, `ReadOnly`, or `Aborted`.
    *   `Commit(transactionID)`: Persistently applies the prepared operations.
    *   `Rollback(transactionID)`: Reverts any prepared operations.
    *   `GetBalance(accountID)`: Returns the current balance of an account.
*   **DTC:** The central coordinator responsible for orchestrating the transaction across multiple nodes.

**Transaction Operations:**

Each operation consists of the affected `accountID` and the `amount` to transfer. A positive amount indicates deposit and a negative amount indicates withdrawal.

**Your Task:**

Implement the DTC logic in Go using the Two-Phase Commit (2PC) protocol with the following requirements:

1.  **Transaction ID Generation:** The DTC must generate unique transaction IDs.
2.  **Prepare Phase:**
    *   The DTC sends `Prepare` requests to all involved nodes, along with the transaction ID and the operations relevant to each node.
    *   It must handle potential network errors (e.g., timeouts, connection refused). Implement retry logic with exponential backoff.
    *   The DTC must collect responses from all nodes.
3.  **Commit/Rollback Phase:**
    *   If all nodes respond with `Prepared` or `ReadOnly`, the DTC sends `Commit` requests to all nodes.
    *   If any node responds with `Aborted`, or if the DTC encounters an error during the prepare phase, it sends `Rollback` requests to all nodes.
    *   The DTC must handle potential network errors during the commit/rollback phase, implementing retry logic with exponential backoff.
4.  **Logging:**
    *   The DTC must maintain a persistent log of all transaction state transitions (e.g., "Prepare sent", "Commit sent", "Transaction committed", "Transaction rolled back"). This log is crucial for recovery after a DTC crash. The log should be append-only.
5.  **Recovery:**
    *   Upon DTC restart, it must recover its state by reading the log and resuming any incomplete transactions. This means re-sending `Commit` or `Rollback` requests if necessary.
6.  **Idempotency:** The `Commit` and `Rollback` operations on bank services (nodes) must be idempotent. This means that receiving the same `Commit` or `Rollback` request multiple times has the same effect as receiving it once. (This aspect is assumed to be implemented on the bank service side and doesn't need to be explicitly implemented in the DTC).
7.  **Concurrency:** The DTC must handle concurrent transaction requests.

**Constraints:**

*   **Network Failures:** Simulate network failures using techniques like introducing random delays or dropping packets during communication between the DTC and bank services.
*   **DTC Crashes:** Simulate DTC crashes by abruptly terminating the DTC process.
*   **Scalability:** While the core logic must function correctly with a small number of nodes, consider the scalability implications of your design.
*   **Performance:** The DTC should perform efficiently, minimizing the overall transaction latency.
*   **Error Handling:** Robust error handling is crucial. The DTC must handle unexpected errors gracefully and avoid data corruption.
*   **No External Database:** You are not allowed to use external databases (like MySQL, Postgres) for the DTC's persistent log. You must implement a simple file-based logging mechanism.

**Bonus:**

*   Implement optimizations such as asynchronous communication with nodes.
*   Add support for detecting and handling deadlocks.

This problem requires careful consideration of concurrency, error handling, and fault tolerance. A well-designed solution will demonstrate a strong understanding of distributed systems concepts and the 2PC protocol.
