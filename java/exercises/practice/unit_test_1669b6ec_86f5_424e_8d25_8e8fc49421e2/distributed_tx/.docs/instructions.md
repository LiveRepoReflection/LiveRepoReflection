## Question: Distributed Transaction Coordinator

You are tasked with designing and implementing a simplified, in-memory, distributed transaction coordinator (similar to a two-phase commit protocol) for a system of microservices.

**Scenario:**

Imagine you have a set of independent microservices, each responsible for managing its own data. To perform complex operations that require consistency across multiple services, you need a distributed transaction. Your task is to implement a coordinator that ensures either all operations in the transaction succeed (commit) or all operations are rolled back (abort).

**Microservice Interface:**

Each microservice exposes a simplified interface for participating in transactions:

*   `prepare(transactionId)`: The coordinator calls this method to ask the microservice to prepare for the transaction. The microservice should perform all necessary checks (e.g., resource availability, validation) and reserve the resources required for the transaction. It returns `true` if prepared successfully, `false` otherwise.
*   `commit(transactionId)`: If all microservices successfully prepared, the coordinator calls this to instruct the microservice to permanently apply the changes associated with the transaction.
*   `rollback(transactionId)`: If any microservice fails to prepare, or if the coordinator decides to abort the transaction, this method is called to undo any changes made during the prepare phase.

**Your Task:**

Implement a `TransactionCoordinator` class in Java with the following methods:

*   `begin()`: Starts a new transaction and returns a unique transaction ID (a simple incrementing integer is sufficient).
*   `enlist(transactionId, microservice)`: Adds a microservice to the transaction. `microservice` is an interface (defined below).
*   `commit(transactionId)`: Attempts to commit the transaction. This involves:
    1.  Calling `prepare(transactionId)` on all enlisted microservices.
    2.  If all `prepare()` calls return `true`, call `commit(transactionId)` on all microservices.
    3.  Return `true` if all operations succeeded.
    4.  If any `prepare()` call returns `false`, call `rollback(transactionId)` on all microservices.
    5.  Return `false` if any operation fails.
*   `rollback(transactionId)`: Rolls back the transaction. This involves calling `rollback(transactionId)` on all enlisted microservices. Return `true` if all rollback operations succeeded, `false` otherwise.

**Microservice Interface (Define this interface in your code):**

```java
interface Microservice {
    boolean prepare(int transactionId);
    void commit(int transactionId);
    void rollback(int transactionId);
}
```

**Constraints and Considerations:**

*   **Concurrency:** The `commit` and `rollback` methods of the `TransactionCoordinator` *must* be thread-safe. Multiple transactions might be initiated concurrently.
*   **Timeout:**  Introduce a timeout mechanism for the `prepare` phase. If a microservice doesn't respond within a reasonable time (e.g., 5 seconds), consider it a failure and initiate a rollback.  This timeout should be configurable.
*   **Idempotency:**  Assume that microservices *may* not be fully idempotent.  That is, calling prepare/commit/rollback multiple times with the same transaction ID *may* have unintended side effects.  Design your coordinator to minimize the chances of such calls, and document any remaining risks.
*   **Error Handling:** Implement robust error handling.  Log any exceptions thrown by the microservices and handle them gracefully.  The coordinator should attempt to rollback even if some microservices throw exceptions during the prepare or commit phases.
*   **Logging:**  Implement logging to track the progress of transactions (e.g., transaction started, microservice enlisted, prepare successful/failed, commit successful/failed, rollback successful/failed).
*   **Optimization:** The `prepare` calls can be performed concurrently to reduce the overall commit time.

**Bonus Challenges:**

*   **Recovery:** If the coordinator crashes during a transaction (e.g., after preparing some services but before committing others), how could you implement a recovery mechanism to ensure data consistency when the coordinator restarts? (No need to implement the full recovery, just describe the approach).
*   **Deadlock Prevention:** If microservices access resources in different orders, deadlocks could occur.  How would you modify the coordinator or the microservice interface to prevent deadlocks? (Again, just describe the approach).

This problem requires careful consideration of concurrency, error handling, and distributed systems principles. Good luck!
