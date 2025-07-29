## Project Name

`Distributed Transaction Coordinator`

## Question Description

You are tasked with building a simplified, in-memory distributed transaction coordinator (DTC) for a microservices architecture. The goal is to ensure atomicity across multiple services when updating their individual data.  This DTC should support the two-phase commit (2PC) protocol.

**Scenario:**

Imagine you are designing a system for processing online orders.  An order involves multiple microservices:

*   **Order Service:** Manages order details (order ID, customer ID, total amount).
*   **Inventory Service:** Manages product inventory.
*   **Payment Service:** Processes payments.

When a customer places an order, all three services need to be updated atomically. If any service fails to commit its changes, the entire transaction must be rolled back.

**Requirements:**

1.  **Transaction Management:** Implement a `TransactionCoordinator` struct that manages distributed transactions. It should support the following operations:
    *   `begin_transaction()`: Starts a new transaction and returns a unique transaction ID (UUID).
    *   `enlist_resource(transaction_id, resource)`: Registers a `Resource` (see below) with the transaction.
    *   `prepare_transaction(transaction_id)`: Initiates the prepare phase of the 2PC protocol.  Each enlisted resource should be asked to "prepare" its changes.
    *   `commit_transaction(transaction_id)`: Initiates the commit phase of the 2PC protocol. If all resources prepared successfully, they should be asked to commit.
    *   `rollback_transaction(transaction_id)`: Initiates the rollback phase of the 2PC protocol. All enlisted resources should be asked to rollback.

2.  **Resource Abstraction:** Define a `Resource` trait that represents a service participating in a distributed transaction.  It should have the following methods:
    *   `prepare()`: Attempts to prepare the resource for committing the transaction. Returns `Ok(true)` if successful, `Ok(false)` if the resource cannot prepare (e.g., due to insufficient inventory), and `Err(String)` if an unrecoverable error occurs.
    *   `commit()`: Commits the changes made during the transaction. Returns `Ok(())` if successful, `Err(String)` otherwise.
    *   `rollback()`: Rolls back any changes made during the transaction. Returns `Ok(())` if successful, `Err(String)` otherwise.

3.  **Error Handling:**  Implement robust error handling. The `TransactionCoordinator` should handle different types of errors gracefully, including resource preparation failures, commit failures, and rollback failures.  Ensure that if one resource fails to prepare, all enlisted resources are rolled back.  If a resource fails to commit *after* all resources have prepared, attempt to rollback all resources, logging the commit failure and rollback attempts.

4.  **Concurrency:** The `TransactionCoordinator` must be thread-safe, allowing multiple transactions to be processed concurrently. Use appropriate synchronization primitives (e.g., Mutex, RwLock) to protect shared data.

5.  **Resource Locking (Optimistic Concurrency Control):** Implement a simple optimistic locking mechanism within the `Resource` trait.  Each resource should maintain a version number.  The `prepare()` method should check if the version number has changed since the transaction started. If it has, the resource should return `Ok(false)` to indicate that it cannot prepare because of a conflict. The `commit()` method should increment the version number.  The version number should be u64.

6.  **Timeout:** Implement a timeout mechanism for the `prepare_transaction` method.  If a resource takes longer than a specified duration (e.g., 5 seconds) to prepare, the `TransactionCoordinator` should consider it as a failure and rollback the transaction.

**Constraints:**

*   All operations within a single transaction must be atomic.
*   The system must be resilient to failures.
*   Implement the timeout for prepare transaction.
*   The solution must be thread-safe.
*   The solution must be implemented in Rust, leveraging its concurrency features.
*   The solution should avoid deadlocks.
*   Assume that the network is reliable - you do not need to handle network partitions or message loss. Focus on the core 2PC logic and resource locking.
*   You do not need to persist the transaction state to disk.  An in-memory implementation is sufficient.

**Bonus Challenges:**

*   Implement logging for all transaction-related events (begin, prepare, commit, rollback, failures).
*   Add a retry mechanism for commit and rollback operations in case of transient failures.
*   Implement a mechanism to detect and resolve orphaned transactions (transactions that are never completed due to coordinator failure).

This problem requires a good understanding of distributed transactions, concurrency, error handling, and the Rust programming language. Good luck!
