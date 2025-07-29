## Question: Distributed Transaction Coordinator

### Question Description

You are tasked with designing and implementing a simplified, in-memory distributed transaction coordinator (DTC) service. This service is responsible for ensuring the atomicity and consistency of transactions across multiple independent resource managers (RMs). In this scenario, RMs are simplified to in-memory dictionaries.

**System Architecture:**

The system consists of:

*   **Transaction Coordinator (TC):** The central service responsible for managing the transaction lifecycle (begin, prepare, commit, rollback).
*   **Resource Managers (RMs):** Independent entities that manage data resources. Each RM exposes an interface to participate in transactions. They can either commit or rollback their changes based on the TC's decision.
*   **Clients:** Initiate transactions that involve operations on multiple RMs.

**Simplified Model:**

*   Transactions are identified by a unique transaction ID (UUID).
*   The only operation supported on RMs is "write".
*   The 2-Phase Commit (2PC) protocol is used for transaction management.

**Detailed Requirements:**

1.  **`begin_transaction()`:**
    *   The client requests the TC to start a new transaction.
    *   The TC generates a unique transaction ID (UUID) and returns it to the client.

2.  **`write(transaction_id, rm_id, key, value)`:**
    *   The client instructs an RM to perform a write operation within a specific transaction.
    *   The RM stores the write operation (key-value pair) in a temporary storage associated with the transaction ID. This temporary storage acts as the RM's "prepared" state.
    *   If the RM fails to prepare (e.g., due to resource constraints or internal errors), it should return an error to the TC.

3.  **`prepare_transaction(transaction_id)`:**
    *   The client informs the TC that all operations for a given transaction are complete and requests the TC to initiate the prepare phase.
    *   The TC contacts all RMs involved in the transaction.
    *   Each RM checks if it's able to commit the changes associated with the transaction ID.
    *   If all RMs respond with a "ready to commit" signal, the TC moves to the commit phase.
    *   If any RM responds with a "cannot commit" signal (or fails to respond within a reasonable timeout - assume 1 second), the TC moves to the rollback phase.

4.  **`commit_transaction(transaction_id)`:**
    *   The TC instructs all RMs that signaled "ready to commit" to permanently apply the changes associated with the transaction ID.
    *   The RMs apply the changes from their temporary storage to their main data store.
    *   The RMs remove the temporary storage associated with the transaction ID.

5.  **`rollback_transaction(transaction_id)`:**
    *   The TC instructs all RMs involved in the transaction to discard the changes associated with the transaction ID.
    *   The RMs discard the temporary storage associated with the transaction ID.

**Constraints and Edge Cases:**

*   **Concurrency:**  The TC must handle concurrent transactions from multiple clients.
*   **RM Failure:** The system must handle cases where an RM fails to respond during the prepare phase (timeout of 1 second).
*   **Idempotency:** The `commit_transaction` and `rollback_transaction` operations should be idempotent. If the TC sends a commit/rollback command multiple times to an RM, the RM should only perform the action once.
*   **RM Registration:** RMs dynamically register with the TC upon startup, providing a unique `rm_id`.
*   **Transaction Isolation:**  Reads are not part of this problem. We only focus on ensuring atomicity and consistency of write operations.
*   **Optimizations:** Focus on correctness first. However, consider potential optimizations regarding concurrency and the 2PC protocol execution.

**Evaluation Criteria:**

Your solution will be evaluated based on:

*   **Correctness:** Ensuring atomicity and consistency across RMs. All or nothing should happen.
*   **Concurrency Handling:** Gracefully handling concurrent transactions.
*   **RM Failure Handling:** Recovering from RM failures during the prepare phase.
*   **Idempotency:** Correctly handling duplicate commit/rollback commands.
*   **Code Clarity and Structure:** Well-organized and readable code.
*   **Efficiency:** Efficient implementation of the 2PC protocol. While not the primary focus, excessive resource usage should be avoided.
*   **Scalability Considerations:** While not explicitly implemented, briefly discuss how the system design could be scaled to handle a large number of RMs and transactions.

This problem requires a deep understanding of distributed transaction concepts, concurrency, and error handling. Good luck!
