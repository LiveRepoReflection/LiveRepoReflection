## Project Name:

`Distributed Transaction Coordinator`

## Question Description:

You are tasked with designing and implementing a distributed transaction coordinator (DTC) for a simplified banking system. This system involves multiple geographically distributed bank branches, each managing its own database of customer accounts. To ensure data consistency, transactions that span multiple branches must adhere to the ACID properties (Atomicity, Consistency, Isolation, Durability).

**Scenario:**

Imagine a customer wants to transfer funds from their account in Branch A to another account in Branch B. This transfer involves two separate operations: debiting the account in Branch A and crediting the account in Branch B. These operations must be treated as a single atomic transaction. Either both succeed, or both fail.

**Your Task:**

Implement a simplified DTC that uses the Two-Phase Commit (2PC) protocol to coordinate distributed transactions across the bank branches.

**Specific Requirements:**

1.  **Branch Interface:** Assume each bank branch exposes a simple interface with the following methods:
    *   `prepare(transactionId, operation)`:  Indicates that the branch should prepare to execute the given `operation` (debit or credit) for the specified `transactionId`. The branch performs necessary checks (e.g., sufficient funds) and returns `true` if it can commit the operation, or `false` if it cannot. The branch MUST hold any necessary locks to ensure isolation until it receives either a `commit` or `rollback` message.
    *   `commit(transactionId)`: Instructs the branch to permanently apply the previously prepared `operation` for the given `transactionId`.
    *   `rollback(transactionId)`: Instructs the branch to undo any changes made during the preparation phase for the given `transactionId`.
    *   Assume a `Transaction` object exists with relevant details (source account, destination account, amount, etc.)
    *   Assume an `Operation` object encapsulates debit or credit actions with transaction details.

2.  **DTC Implementation:** Implement the DTC with the following responsibilities:
    *   **Transaction Management:**  Assign unique transaction IDs to each new distributed transaction.
    *   **2PC Coordination:** Implement the 2PC protocol to coordinate the transaction across all participating branches. This involves:
        *   **Phase 1 (Prepare):** Sending `prepare` requests to all involved branches.
        *   **Phase 2 (Commit/Rollback):** If all branches respond with success (`true`) in the prepare phase, send `commit` requests to all branches. If any branch responds with failure (`false`), send `rollback` requests to all branches.
    *   **Logging:** Implement logging to persistent storage (e.g., a simple file or in-memory data structure that persists) to record the state of each transaction.  This is crucial for recovery in case of failures.  Log entries should include at least: transaction ID, participating branches, and the outcome of each phase (prepare, commit, rollback).
    *   **Recovery:** Implement a recovery mechanism that allows the DTC to resume operation after a crash.  Upon restart, the DTC should scan the logs, identify incomplete transactions, and drive them to completion (either commit or rollback) based on the logged state. Assume that Branch services are highly available and can respond to requests after the DTC recovers.

3.  **Concurrency:** The DTC must handle concurrent transactions correctly.  Ensure that transactions are properly isolated and do not interfere with each other.  Consider using appropriate locking or concurrency control mechanisms within the DTC.

4.  **Error Handling:** Implement robust error handling to gracefully handle network failures, branch failures, and other potential exceptions.  Ensure that the system maintains data consistency even in the face of errors. You can assume network operations are unreliable and may fail or timeout.

5.  **Optimization:** Consider the performance implications of your design. While correctness is paramount, strive to minimize the latency of distributed transactions. Think about how to handle slow or unresponsive branches. Can you introduce any optimizations without compromising data integrity?

**Constraints:**

*   The number of branches participating in a single transaction can vary.
*   Network communication between the DTC and the branches can be unreliable.
*   The DTC itself can crash and restart.
*   Branches can fail temporarily but will eventually recover.
*   The amount of data involved in each transaction is relatively small.
*   Focus on the core 2PC logic and recovery mechanism. You do not need to implement a full-fledged database system or a sophisticated network transport layer.

**Deliverables:**

*   Well-documented Java code implementing the DTC and a simplified representation of the branch interface.
*   A description of your design choices, including the data structures used for logging, concurrency control mechanisms, and error handling strategies.
*   A brief explanation of how your solution ensures ACID properties.
*   Demonstrate with examples on how the DTC handles the concurrency of transactions and handles branch failures.

**Judging Criteria:**

*   **Correctness:** The solution must correctly implement the 2PC protocol and guarantee data consistency across all branches.
*   **Robustness:** The solution must handle network failures, branch failures, and DTC crashes gracefully.
*   **Concurrency:** The solution must correctly handle concurrent transactions.
*   **Efficiency:** The solution should strive for reasonable performance.
*   **Design:** The code should be well-structured, maintainable, and easy to understand.
*   **Completeness:** All the requirements are addressed.
*   **Error Handling:** Robust error handling strategies are implemented.

This is a challenging problem that requires a solid understanding of distributed systems concepts, concurrency control, and error handling. Good luck!
