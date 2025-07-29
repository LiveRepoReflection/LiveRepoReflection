## Problem: Distributed Transaction Coordinator

### Description:

You are tasked with designing and implementing a distributed transaction coordinator (DTC) for a simplified banking system. This system involves multiple bank branches (represented as services) that need to participate in transactions. A transaction might involve transferring funds from an account in one branch to an account in another.

To ensure data consistency across all branches, you need to implement the Two-Phase Commit (2PC) protocol. Your DTC will act as the coordinator, ensuring that either all branches commit the transaction or all branches roll back, even in the face of failures.

### Requirements:

1.  **Transaction Initiation:** The DTC receives a request to initiate a transaction. The request contains a unique transaction ID and a list of participating bank branches (their service endpoints).
2.  **Phase 1: Prepare Phase:** The DTC sends a "prepare" message to all participating branches. Each branch should attempt to perform the transaction tentatively (e.g., reserve funds). If successful, it responds with a "prepared" message. If it fails (e.g., insufficient funds, branch unavailable), it responds with a "abort" message.
3.  **Phase 2: Commit/Rollback Phase:**
    *   If the DTC receives "prepared" messages from all branches, it sends a "commit" message to all branches. Each branch should then permanently apply the transaction and respond with a "committed" message.
    *   If the DTC receives even a single "abort" message, or if a branch fails to respond within a reasonable timeout, it sends a "rollback" message to all branches. Each branch should then undo the tentative transaction and respond with a "rolledback" message.
4.  **Failure Handling:**
    *   **Branch Failure:** If a branch fails to respond during the prepare or commit/rollback phase, the DTC should assume the branch aborted and initiate a rollback for all other branches.
    *   **DTC Failure (Recovery):** The DTC should be able to recover from failures. Upon restarting, it should check the status of any ongoing transactions (transactions for which it hasn't received final confirmation from all branches) and complete them according to the 2PC protocol. This will likely involve logging transaction state to persistent storage.
5.  **Concurrency:** The DTC must handle multiple concurrent transactions.
6.  **Logging:** Implement logging to persistent storage (e.g., a file or a simple in-memory database for testing) to track the state of transactions. This is crucial for recovery after DTC failures.
7.  **Optimizations (Bonus):**
    *   Implement a mechanism to handle "orphaned" transactions – transactions that were prepared but for which the coordinator never issued a commit or rollback due to a failure. This might involve a periodic scan of prepared transactions and a communication with the DTC (if available) to determine the final outcome.
    *   Explore optimizations to reduce the number of messages exchanged in the 2PC protocol.

### Constraints:

*   **Simulate Branch Services:** You do not need to implement actual bank branch services. You can simulate them with simple classes/objects that respond to prepare, commit, and rollback messages. Implement this within the same JVM.
*   **Timeouts:** Implement appropriate timeouts for all network communications to handle branch failures.
*   **Transaction Isolation:** Assume that each branch service handles transaction isolation internally. Your focus is on coordinating the distributed transaction across branches.
*   **Error Handling:** Handle all potential exceptions and log errors appropriately.
*   **Scalability considerations:** Although full scalability is not required, consider how your design could be adapted to handle a large number of branches and concurrent transactions (e.g., sharding, distributed logging).

### Evaluation Criteria:

*   **Correctness:** Does the DTC correctly implement the 2PC protocol, ensuring atomicity and consistency?
*   **Failure Handling:** Does the DTC handle branch failures and DTC failures gracefully, recovering to a consistent state?
*   **Concurrency:** Does the DTC handle multiple concurrent transactions without data corruption or deadlocks?
*   **Code Quality:** Is the code well-structured, readable, and maintainable?
*   **Efficiency:** Is the solution reasonably efficient in terms of resource usage (CPU, memory)?
*   **Recovery:** Does the DTC correctly recover unfinished transactions after a failure?

This problem requires a solid understanding of distributed systems concepts, transaction management, and concurrency. It also tests your ability to design and implement a robust and fault-tolerant system. Good luck!
