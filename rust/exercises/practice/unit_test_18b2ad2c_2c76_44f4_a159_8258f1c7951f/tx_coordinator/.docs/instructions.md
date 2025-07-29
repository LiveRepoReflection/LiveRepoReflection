## Project Name

`DistributedTransactionCoordinator`

## Question Description

You are tasked with building a simplified, in-memory distributed transaction coordinator in Rust. This coordinator will manage transactions across multiple independent "resource managers". Think of these resource managers as distinct databases or services. The goal is to ensure ACID properties (Atomicity, Consistency, Isolation, Durability) across these resource managers when a single transaction involves operations on more than one of them.

**Core Concepts:**

*   **Transaction ID (TxId):** A unique identifier for each transaction.
*   **Resource Manager (RM):** An independent service or database that participates in transactions. For simplicity, each RM is represented by a string identifier.
*   **Transaction State:** A transaction can be in one of the following states: `Active`, `Prepared`, `Committed`, `Aborted`.
*   **Two-Phase Commit (2PC):** The core protocol for distributed transactions.

**Your Task:**

Implement a `TransactionCoordinator` struct with the following functionality:

1.  **`new()`:** Constructor for the `TransactionCoordinator`.

2.  **`begin_transaction() -> TxId`:** Starts a new transaction and returns a unique `TxId`. The transaction should initially be in the `Active` state.

3.  **`enlist_resource(tx_id: TxId, resource_manager: &str) -> Result<(), String>`:**  Adds a resource manager to the transaction's participant list. A resource manager can only be enlisted once per transaction.  Return an error string if the transaction doesn't exist, or if the RM is already enlisted.

4.  **`prepare_transaction(tx_id: TxId) -> Result<(), String>`:** Initiates the prepare phase of the 2PC protocol. For each enlisted resource manager, simulate a "prepare" operation.  For simplicity, assume each RM always successfully prepares (no RM failures during prepare). After all RMs have "prepared", the transaction moves to the `Prepared` state. Return an error string if the transaction doesn't exist or is not in the `Active` state.

5.  **`commit_transaction(tx_id: TxId) -> Result<(), String>`:**  Initiates the commit phase of the 2PC protocol. For simplicity, assume all RMs successfully commit. After all RMs have "committed", the transaction moves to the `Committed` state.  Return an error string if the transaction doesn't exist or is not in the `Prepared` state.

6.  **`abort_transaction(tx_id: TxId) -> Result<(), String>`:** Aborts the transaction. For simplicity, assume all RMs successfully abort. The transaction moves to the `Aborted` state. Return an error string if the transaction doesn't exist. It's allowed to abort a transaction at any state before it's committed.

7.  **`get_transaction_state(tx_id: TxId) -> Option<TransactionState>`:** Returns the current state of the transaction. Returns `None` if the transaction doesn't exist.

**Constraints and Considerations:**

*   **Concurrency:** The `TransactionCoordinator` must be thread-safe, allowing multiple concurrent transactions.
*   **Efficiency:**  Minimize locking contention and optimize for read performance (getting the transaction state).
*   **Error Handling:** Provide informative error messages.
*   **Memory Management:** Avoid memory leaks.
*   **Scalability:** Consider the design implications if the number of active transactions and resource managers were significantly larger.
*   **Durability (Simplified):** Assume the transaction log (the state of each transaction) is stored in memory. In a real system, this would need to be persisted to disk for crash recovery. You do not need to implement disk persistence for this problem.

**Bonus Challenges:**

*   **Timeout:** Implement a timeout mechanism for transactions. If a transaction remains in the `Active` or `Prepared` state for longer than a specified timeout, automatically abort it.
*   **Resource Manager Failure:** Simulate resource manager failures during the prepare or commit phase and handle them gracefully (e.g., by retrying, logging errors, or escalating to a higher-level administrator).
*   **Idempotency:** Ensure that the prepare, commit, and abort operations are idempotent (i.e., executing them multiple times has the same effect as executing them once).

This problem requires a good understanding of concurrency, data structures, and distributed systems concepts. It challenges you to design a thread-safe and efficient transaction coordinator that can manage transactions across multiple resource managers while adhering to the principles of the 2PC protocol.
