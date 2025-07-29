## Project Name

**Distributed Transaction Coordinator**

## Question Description

You are tasked with building a simplified, in-memory distributed transaction coordinator. This coordinator must manage transactions across multiple independent "resource managers." These resource managers could represent anything from databases to message queues, but for this problem, they are simulated with a simple key-value store.

Your coordinator must implement the two-phase commit (2PC) protocol to ensure atomicity of transactions. Atomicity means that a transaction either commits successfully across all resource managers, or it rolls back on all resource managers.

**System Architecture:**

1.  **Transaction Coordinator:** This is the core component you will implement. It receives transaction requests, coordinates with resource managers, and ensures atomicity.
2.  **Resource Managers:** These are independent services that manage their own data. They expose an API for the transaction coordinator to interact with. For this problem, each resource manager maintains a simple in-memory key-value store.
3.  **Clients:** These are external entities that initiate transactions through the transaction coordinator.

**Requirements:**

1.  **Transaction Isolation:**  Implement `Read Committed` isolation level. This means a transaction can only read data committed by other transactions. Uncommitted changes made by other transactions should not be visible.

2.  **Concurrency:**  The coordinator must handle concurrent transaction requests.

3.  **Failure Handling:**  The coordinator must be resilient to failures of resource managers *during* the transaction process.  Specifically, if a resource manager fails *after* voting to commit (but before the commit command is received), the coordinator must be able to detect this on recovery and ensure the transaction eventually commits on that resource manager.

4.  **API:**  Implement the following functions for the Coordinator:

    *   `begin_transaction() -> TransactionId`: Starts a new transaction and returns a unique transaction ID.
    *   `read(transaction_id: TransactionId, resource_manager_id: ResourceManagerId, key: String) -> Option<String>`: Reads the value associated with a key from a specific resource manager within the context of a transaction.
    *   `write(transaction_id: TransactionId, resource_manager_id: ResourceManagerId, key: String, value: String)`: Writes a key-value pair to a specific resource manager within the context of a transaction.
    *   `commit_transaction(transaction_id: TransactionId) -> bool`: Attempts to commit the transaction. Returns `true` on success, `false` on failure (e.g., timeout, resource manager failure).
    *   `rollback_transaction(transaction_id: TransactionId)`: Rolls back the transaction.

5.  **Resource Manager API (Simulated):** Assume each resource manager provides the following (simulated) API:

    *   `prepare(transaction_id: TransactionId) -> bool`:  The resource manager checks if it can commit the transaction (e.g., no conflicts). Returns `true` if ready to commit, `false` otherwise.
    *   `commit(transaction_id: TransactionId)`:  Commits the transaction.
    *   `rollback(transaction_id: TransactionId)`:  Rolls back the transaction.
    *   `get_value(key: String) -> Option<String>`:  Gets the value associated with a key.

6.  **Optimization:**  Optimize for throughput and latency.  Minimize the time it takes to commit or rollback transactions.

**Constraints:**

*   **In-memory:**  All data (transaction state, resource manager data) should be stored in memory.
*   **Limited Resources:**  Simulate a system with a limited number of threads/workers.  Avoid unbounded thread creation.
*   **Timeout:**  Implement a reasonable timeout mechanism for waiting on responses from resource managers.  Transactions should not be blocked indefinitely if a resource manager fails.
*   **ResourceManagerId and TransactionId:** These are simple `u64` numbers.
*   **Assumptions:** You can assume perfect network conditions (no packet loss or corruption) except for resource manager failures.

**Edge Cases:**

*   **Duplicate Commit/Rollback:**  Handle cases where a client attempts to commit or rollback the same transaction multiple times.
*   **Orphaned Transactions:**  The coordinator should be able to handle orphaned transactions (transactions that are interrupted before completion due to coordinator failure).  Upon restart, the coordinator should recover and either commit or rollback these transactions based on their last known state.
*   **Resource Manager Unavailability:** Handle cases where a resource manager is temporarily unavailable during prepare phase or commit phase.

**Bonus:**

*   Implement a simple logging mechanism to disk to persist transaction state, enabling recovery after coordinator failure.
*   Add a distributed lock manager to handle write-write conflicts between concurrent transactions.

This problem requires a strong understanding of distributed systems concepts, concurrency, and error handling.  Good luck!
