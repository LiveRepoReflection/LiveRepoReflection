## Question: Distributed Transaction Manager

### Question Description

You are tasked with designing and implementing a simplified, distributed transaction manager in Rust. This transaction manager will be responsible for ensuring atomicity and consistency across multiple independent services.

Imagine a system composed of several microservices, each managing its own data. To perform complex operations, a transaction might need to update data across multiple services. Your transaction manager should coordinate these updates, ensuring that either all updates succeed (commit) or none of them do (rollback), even in the face of network failures or service crashes.

**Core Functionality:**

1.  **Transaction Initiation:** A client initiates a transaction by registering with the transaction manager. The transaction manager assigns a unique transaction ID (TXID).

2.  **Resource Registration:** Participating services (resources) register themselves with the transaction manager for a specific TXID. This registration indicates that the service will be part of the transaction and potentially perform updates.

3.  **Prepare Phase:** Upon client request, the transaction manager initiates the "prepare" phase. It sends a "prepare" message to all registered resources. Each resource attempts to perform its part of the transaction and signals back to the transaction manager whether it succeeded ("prepared") or failed ("abort"). This prepare stage must be idempotent, i.e. re-running it should not change the outcome (either prepared or aborted)

4.  **Commit/Rollback Phase:**
    *   If all resources successfully "prepared," the transaction manager initiates the "commit" phase by sending a "commit" message to all resources. Resources then permanently apply their changes.
    *   If any resource fails to "prepare," the transaction manager initiates the "rollback" phase by sending a "rollback" message to all resources. Resources then undo any temporary changes made during the "prepare" phase.
    *   Commit and Rollback stages must also be idempotent.

5.  **Transaction Completion:** After the "commit" or "rollback" phase, the transaction manager informs the client of the transaction's outcome (success or failure) and removes the transaction from its active transaction list.

**Constraints and Requirements:**

*   **Concurrency:** The transaction manager must handle multiple concurrent transactions.
*   **Idempotency:** The `prepare`, `commit`, and `rollback` operations on the resources must be idempotent. This is crucial for handling potential network issues and retries.
*   **Durability:** The transaction manager's state (active transactions, registered resources, etc.) must be durable. Implement simple persistence to disk (e.g., using a file) to simulate this. Upon restart, the transaction manager should recover its state and attempt to resolve any in-flight transactions (e.g., by re-sending prepare, commit, or rollback messages).
*   **Error Handling:** Implement robust error handling to deal with network failures, resource crashes, and other potential issues.
*   **Timeout:** Implement timeouts for all operations (resource registration, prepare response, etc.). If a resource doesn't respond within the timeout, the transaction manager should consider it a failure and initiate a rollback.
*   **Efficiency:** Your solution should be reasonably efficient. Avoid unnecessary data copying or locking. Consider appropriate data structures for managing transactions and resources.

**Simplifications:**

*   Assume a reliable message transport layer. Focus on the transaction coordination logic.
*   You don't need to implement actual data updates within the resources. You can simulate these with simple logging or state changes within the resource implementations.
*   Focus on the core transaction management logic. Don't worry about complex security features or advanced recovery mechanisms.

**Your Task:**

Implement the core logic of the distributed transaction manager, including transaction initiation, resource registration, prepare, commit, rollback, transaction completion, persistence, and recovery. Provide a clear and well-structured implementation in Rust, paying attention to concurrency, idempotency, durability, error handling, and efficiency.
