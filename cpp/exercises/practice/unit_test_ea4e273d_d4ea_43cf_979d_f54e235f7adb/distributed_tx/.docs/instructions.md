## Question Title: Distributed Transaction Manager

### Question Description

You are tasked with designing a simplified distributed transaction manager for a microservices architecture. Imagine you have several independent services (databases, message queues, external APIs, etc.) participating in a single logical transaction.  The transaction must either commit atomically across all services or rollback entirely if any service fails.

Due to network instability and the independent nature of these services, direct two-phase commit (2PC) is not feasible. Instead, you will implement a Saga pattern with compensations to achieve eventual consistency.

**Specifically, you need to implement a `TransactionCoordinator` that manages a set of `TransactionParticipants`.**

A `TransactionParticipant` represents a single service participating in the transaction. Each participant exposes two operations:

*   `prepare()`:  Attempts to prepare the service for the transaction. Preparation may involve reserving resources, performing pre-checks, etc.  It returns `true` if preparation is successful, `false` otherwise.
*   `commit()`:  Commits the transaction within the service.  It returns `true` if successful, `false` otherwise.
*   `compensate()`: Rolls back the transaction within the service.  This should undo any changes made during the `prepare()` or `commit()` stage.  It returns `true` if successful, `false` otherwise. `Compensate` is called if there is a rollback or failure after the prepare stage.

The `TransactionCoordinator` must provide the following functionalities:

1.  **`begin()`:** Starts a new transaction.

2.  **`enroll(TransactionParticipant participant)`:** Adds a participant to the transaction.

3.  **`commit()`:** Attempts to commit the transaction across all participants.  The coordinator must:

    *   First, call `prepare()` on each participant **in the order they were enrolled**. If any `prepare()` call fails, the entire transaction must be rolled back (see below).
    *   If all `prepare()` calls succeed, then call `commit()` on each participant **in the order they were enrolled**.
    *   If all `commit()` calls succeed, the transaction is considered successfully committed.
    *   Return `true` if the entire transaction successfully commits, `false` otherwise.

4.  **`rollback()`:** Rolls back the transaction. The coordinator must:

    *   Call `compensate()` on each participant **in the reverse order they were enrolled**.
    *   The rollback procedure must execute even if compensation fails for some participants.  Record the failures, but continue compensating the remaining participants.
    *   Return `true` if **all** compensation calls are successful, `false` otherwise.

**Constraints and Considerations:**

*   **Concurrency:** The system should be designed to handle multiple concurrent transactions safely.  Consider thread safety and potential race conditions.
*   **Idempotency:** Implement the `prepare()`, `commit()`, and `compensate()` methods in a way that they are idempotent. That is, calling them multiple times with the same input should have the same effect as calling them once.
*   **Error Handling:** Implement robust error handling to gracefully manage failures. Log errors appropriately, but do not throw exceptions unless absolutely necessary.
*   **Logging:**  Include informative logging throughout the `TransactionCoordinator` to track the progress and outcome of each transaction and participant.
*   **Resource Management:** Ensure proper resource management, especially when dealing with potentially long-running transactions.
*   **Participant Failure:** Simulate participant failures using random number generator. The prepare, commit, and compensate of participants may fail randomly based on a small probability to test and trigger the rollback logic.
*   **Deadlock Prevention:** Be aware of potential deadlock scenarios during concurrent transactions and design the system to avoid them.

**Your task is to implement the `TransactionCoordinator` and a sample `TransactionParticipant` class, demonstrating the correct behavior and handling of both successful transactions and rollbacks.  Focus on correctness, concurrency safety, and efficient resource management.**
