## Project Name

`Distributed Transaction Coordinator`

## Question Description

You are tasked with designing and implementing a simplified distributed transaction coordinator for a system involving multiple independent services. These services need to perform operations that must be atomic across all participants. A failure in any service should roll back the entire transaction.

**Scenario:**

Imagine an e-commerce system where placing an order involves multiple services:

1.  **Inventory Service:** Checks and reserves items in the inventory.
2.  **Payment Service:** Processes the payment.
3.  **Shipping Service:** Schedules the shipment.

If any of these steps fail (e.g., insufficient inventory, payment failure, shipping unavailable), the entire order placement process must be rolled back to maintain data consistency.

**Requirements:**

1.  **Implement a `TransactionCoordinator` class** with the following methods:

    *   `begin_transaction()`: Starts a new transaction and returns a unique transaction ID (UUID).
    *   `enlist_participant(transaction_id, participant)`: Adds a participant service to the transaction. A participant must implement the `commit()` and `rollback()` methods.
    *   `commit_transaction(transaction_id)`: Attempts to commit the transaction by calling the `commit()` method on all participants. If any participant's `commit()` call fails (raises an exception), the transaction coordinator must call `rollback()` on all participants (including the ones that already committed) to revert the changes.
    *   `rollback_transaction(transaction_id)`: Rolls back the transaction by calling the `rollback()` method on all participants. This is called if the commit fails or if a client explicitly requests a rollback.

2.  **Implement a base `Participant` class** that defines the `commit()` and `rollback()` methods as abstract methods (must be overridden by subclasses).

3.  **Ensure atomicity:** All operations within a transaction must either succeed completely or be rolled back completely.

4.  **Handle failures gracefully:** The transaction coordinator should handle exceptions raised by participants during commit or rollback and attempt to rollback even if some participants fail during the rollback process. Log these failures.

5.  **Idempotency:** Design the `commit()` and `rollback()` operations to be idempotent. This means that if a `commit()` or `rollback()` operation is called multiple times on the same participant for the same transaction, it should only have the intended effect once. Consider using a state tracking mechanism within each participant to achieve this.

6.  **Concurrency:** The TransactionCoordinator needs to handle multiple concurrent transactions safely. Use appropriate locking mechanisms to prevent race conditions and ensure data consistency.

7.  **Logging:** Implement logging to track the progress of transactions, including participant enlistment, commit attempts, rollbacks, and any errors encountered.

**Constraints:**

*   **Error Handling:** Use custom exception classes to represent transaction-related errors (e.g., `TransactionNotFound`, `ParticipantFailedToCommit`, `ParticipantFailedToRollback`).
*   **Resource Limits:** Assume that the number of participants in a transaction is limited (e.g., maximum 10 participants). The number of concurrent transactions is also limited (e.g., maximum 100 concurrent transactions). Consider the memory implications of tracking these transactions.
*   **Timeouts:** Implement a timeout mechanism for commit operations. If a participant does not respond within a specified timeout period, the transaction should be rolled back.
*   **Distributed Environment Simulation:** You don't need to implement actual network communication. Simulate the distributed environment by having participants operate on in-memory data or simple file operations. The key is to demonstrate the coordination and rollback logic.
*   **Scalability is NOT a main focus:** While consider scalability, the primary goal is to implement a correct and robust transaction coordinator. Optimize for clarity and correctness over extreme performance.

**Bonus (optional):**

*   Implement a recovery mechanism. If the transaction coordinator crashes, it should be able to recover its state and resume any in-flight transactions.
*   Implement a two-phase commit (2PC) protocol for enhanced reliability.
