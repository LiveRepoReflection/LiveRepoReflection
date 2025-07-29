## Question: Distributed Transaction Coordinator

**Problem Description:**

You are tasked with designing and implementing a distributed transaction coordinator (DTC) for a simplified banking system.  This system involves multiple bank branches (represented as services), each managing its own account balances.  A single transaction can involve multiple branches (e.g., transferring money from an account at branch A to an account at branch B).  The coordinator must ensure atomicity: either the entire transaction succeeds across all branches, or the entire transaction fails, leaving all branches in their original state.

**Specific Requirements:**

1.  **Transaction Management:** Implement a `TransactionCoordinator` class that manages distributed transactions.  Each transaction is identified by a unique Transaction ID (UUID).

2.  **Two-Phase Commit (2PC):** Implement the 2PC protocol.
    *   **Phase 1 (Prepare):** The coordinator sends a "prepare" message to each participating branch. Each branch attempts to perform its part of the transaction tentatively. If successful, it replies with "prepared" (or "vote commit"). If it fails, it replies with "aborted" (or "vote rollback").
    *   **Phase 2 (Commit/Rollback):**
        *   If all branches vote to commit, the coordinator sends a "commit" message to all branches.
        *   If any branch votes to abort, or if the coordinator times out waiting for a response, the coordinator sends a "rollback" message to all branches.

3.  **Branch Interface:** Each branch exposes a simple interface:
    *   `prepare(transactionId, operationDetails)`:  The branch attempts to tentatively perform the specified operation (e.g., debit/credit an account). Returns `true` if prepared successfully, `false` otherwise.
    *   `commit(transactionId)`: The branch permanently applies the transaction.
    *   `rollback(transactionId)`: The branch undoes the tentative changes made during the prepare phase.

4.  **Concurrency:** Your coordinator must handle concurrent transactions.  Use appropriate synchronization mechanisms to prevent race conditions and ensure data consistency.

5.  **Fault Tolerance (Limited):** Implement basic fault tolerance. If a branch fails to respond during the prepare phase, the coordinator should treat it as an abort. (Full fault tolerance would involve handling coordinator failures and persistent logs, which are outside the scope of this problem).

6.  **Deadlock Prevention/Detection:**  The branches might be holding locks on accounts during the "prepare" phase.  Implement a basic deadlock prevention or detection mechanism (e.g., timeout-based deadlock detection).  If a deadlock is detected, the coordinator should abort the transaction.

7.  **Optimization:** Minimize the overall transaction latency.  Consider the trade-offs between synchronous and asynchronous communication between the coordinator and the branches.

**Input:**

The system will receive a series of transaction requests. Each request specifies:
*   A unique Transaction ID (UUID)
*   A list of participating branches.
*   For each branch, the operation details (e.g., account ID, amount to debit/credit).

**Output:**

For each transaction, the coordinator should output:
*   "Transaction [Transaction ID] committed" if the transaction was successful.
*   "Transaction [Transaction ID] rolled back" if the transaction was aborted.

**Constraints:**

*   The number of branches per transaction can vary.
*   Branch operations can be complex and may fail for various reasons (e.g., insufficient funds, invalid account).
*   Network communication between the coordinator and branches is unreliable and may be subject to delays or failures.
*   Minimize the time each branch holds locks.

**Example:**

Let's say you have three branches: A, B, and C. A transaction requires debiting $100 from account X at branch A, crediting $100 to account Y at branch B, and recording a transaction log at branch C.

1.  The coordinator sends a "prepare" message to A, B, and C, specifying the details of their respective operations.
2.  A, B, and C attempt to prepare their operations.
3.  If all branches successfully prepare, they send "prepared" messages to the coordinator.
4.  The coordinator sends "commit" messages to A, B, and C.
5.  A, B, and C commit their operations.
6.  The coordinator outputs "Transaction [Transaction ID] committed".

If any branch fails to prepare (e.g., A has insufficient funds), it sends an "aborted" message to the coordinator. The coordinator then sends "rollback" messages to B and C, and outputs "Transaction [Transaction ID] rolled back".

**Judging Criteria:**

Your solution will be judged on:

*   Correctness: Does it correctly implement the 2PC protocol and ensure atomicity?
*   Concurrency: Does it handle concurrent transactions correctly?
*   Fault Tolerance: Does it handle branch failures during the prepare phase?
*   Deadlock Handling: Does it prevent or detect and resolve deadlocks?
*   Performance: Is the transaction latency minimized?
*   Code Quality: Is the code well-structured, readable, and maintainable?

This problem requires a strong understanding of distributed systems concepts, concurrency, and transaction management.  A well-designed and efficient solution will be highly challenging. Good luck!
