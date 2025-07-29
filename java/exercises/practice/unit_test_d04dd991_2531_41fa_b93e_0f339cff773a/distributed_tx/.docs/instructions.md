## Problem: Distributed Transaction Coordinator

**Description:**

You are tasked with designing and implementing a simplified Distributed Transaction Coordinator (DTC) for a microservices architecture.  Imagine a system where multiple independent services need to perform operations that must be ACID (Atomicity, Consistency, Isolation, Durability). To ensure data consistency across these services, a DTC is required to orchestrate distributed transactions.

Your DTC will handle a simplified version of the Two-Phase Commit (2PC) protocol.  The system comprises a central coordinator and multiple participating resource managers (services).

**Specific Requirements:**

1.  **Transaction Representation:** A transaction is identified by a unique Transaction ID (TID), represented as a UUID.  Each transaction involves operations on multiple resources managed by different resource managers.

2.  **Resource Managers (RMs):** Assume you have access to a hypothetical `ResourceManager` interface. Each RM can perform two key actions:
    *   `prepare(TID, operationDetails)`:  The RM attempts to tentatively perform the operation described in `operationDetails`. If successful, it locks the resources involved and returns `true`. If it fails (e.g., due to resource unavailability, validation errors), it returns `false`.
    *   `commit(TID)`: The RM permanently applies the changes associated with the transaction.  This method assumes `prepare()` was successful.
    *   `rollback(TID)`: The RM undoes any changes made during the `prepare()` phase and releases any locks.

3.  **Coordinator Responsibilities:**  The DTC must implement the following operations:
    *   `beginTransaction()`:  Starts a new transaction and returns a unique TID.
    *   `enlistResource(TID, ResourceManager rm, operationDetails)`:  Registers a resource manager and its associated operation details with the specified transaction. The coordinator maintains a list of RMs participating in each transaction.
    *   `commitTransaction(TID)`:  Initiates the 2PC protocol to commit the transaction. This involves the following steps:
        *   **Prepare Phase:**  The coordinator sends a `prepare()` message to all enlisted RMs.
        *   **Decision Phase:**
            *   If all RMs successfully prepared, the coordinator sends a `commit()` message to all RMs.
            *   If any RM failed to prepare, the coordinator sends a `rollback()` message to all RMs.
    *   `rollbackTransaction(TID)`: Initiates a rollback of the transaction by sending a `rollback()` message to all enlisted RMs. This can be called if the coordinator detects an unrecoverable error before calling commitTransaction.

4.  **Concurrency & Deadlock Handling:** The DTC must handle concurrent transaction requests. Consider the possibility of deadlocks (e.g., two transactions attempting to access the same resources in different orders). Implement a simple deadlock detection mechanism (e.g., timeout-based). If a deadlock is suspected, roll back one of the involved transactions.

5.  **Fault Tolerance:**  The DTC should be resilient to RM failures during the 2PC protocol.  If an RM fails to respond to a `prepare()`, `commit()`, or `rollback()` message within a reasonable timeout, the coordinator should assume the RM has failed. In the prepare phase, if an RM fails, the transaction must be rolled back.  In the commit/rollback phase, the coordinator must repeatedly attempt to send the commit/rollback message to the failed RM until it succeeds or a maximum retry count is reached.  Log the reattempt failures.

6.  **Logging:** All significant events (transaction start, RM enlistment, prepare/commit/rollback messages sent/received, RM failures, deadlock detection, transaction outcome) must be logged.  The logging mechanism should be configurable (e.g., to different log levels).

7.  **Optimizations (Bonus):**
    *   Implement a read-only optimization: If an RM only performs read operations (and therefore doesn't need to lock any resources), it can immediately return `true` during the prepare phase and skip the commit/rollback phases.
    *   Batch prepare/commit/rollback messages to RMs when possible to reduce network overhead.

**Constraints:**

*   The `ResourceManager` interface is provided.  You cannot modify it. You can, however, create mock implementations of it for testing.
*   Assume a maximum of 10 resource managers can be enlisted in a single transaction.
*   The timeout for RM responses should be configurable.
*   The maximum retry count for failed RMs during commit/rollback should be configurable.
*   The logging level should be configurable.
*   The operationDetails is a String and can be anything.

**Judging Criteria:**

*   Correctness: The DTC must correctly implement the 2PC protocol and ensure ACID properties.
*   Concurrency: The DTC must handle concurrent transaction requests efficiently.
*   Fault Tolerance: The DTC must be resilient to RM failures.
*   Deadlock Handling: The DTC must detect and resolve deadlocks.
*   Code Quality: The code must be well-structured, readable, and maintainable.
*   Adherence to Constraints: The solution must adhere to all specified constraints.
*   Optimization (Bonus): Solutions that implement the read-only optimization or batching will be given extra consideration.
