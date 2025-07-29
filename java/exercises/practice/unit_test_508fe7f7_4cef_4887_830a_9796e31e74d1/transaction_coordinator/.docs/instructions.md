## Question: Distributed Transaction Coordinator

**Problem Description:**

You are tasked with designing and implementing a distributed transaction coordinator for a simplified microservices architecture.  This coordinator will manage transactions across multiple independent services.  Imagine a scenario where a user wants to transfer funds from their account in Service A to another user's account in Service B.  This operation requires updating the balances in both services and must be performed atomically (either both updates succeed, or neither does).

Each service exposes a simple API for:

1.  **`prepare(transactionId, operationData)`:**  The coordinator calls this on each service to tentatively perform the operation described in `operationData` related to `transactionId`. The service performs the operation in a provisional state (e.g., reserving resources, updating a temporary balance).  It returns `true` if the preparation was successful, and `false` otherwise.  If `false` is returned, the service must guarantee that it has not made any permanent changes and can roll back if asked.
2.  **`commit(transactionId)`:**  If all services successfully prepared, the coordinator calls this to finalize the changes related to `transactionId`. The service must permanently apply the changes.
3.  **`rollback(transactionId)`:** If any service fails to prepare, or if the coordinator experiences a failure, the coordinator calls this to undo any provisional changes made during the prepare phase related to `transactionId`. The service must undo all changes made during the prepare phase.

**Your Task:**

Implement a `TransactionCoordinator` class with the following methods:

*   **`TransactionCoordinator(Set<Service> services)`:** Constructor. Accepts a set of `Service` objects participating in transactions.

*   **`boolean executeTransaction(UUID transactionId, Map<Service, OperationData> operations)`:** Executes a distributed transaction.

    *   `transactionId`: A unique identifier for the transaction.
    *   `operations`: A map where the key is a `Service` object, and the value is an `OperationData` object containing the information needed to perform the operation on that service (e.g., account IDs, amount to transfer).

    The method should implement a two-phase commit (2PC) protocol:

    1.  **Prepare Phase:** Call `prepare(transactionId, operationData)` on each service in the `services` set, in parallel.  Collect the results.
    2.  **Commit/Rollback Phase:**
        *   If all services successfully prepared (all returned `true`), call `commit(transactionId)` on each service, in parallel.  If a service fails to commit, log the error but continue attempting to commit to the other services.
        *   If any service failed to prepare (any returned `false`), call `rollback(transactionId)` on each service, in parallel.  If a service fails to rollback, log the error but continue attempting to rollback the other services.
    3.  Return `true` if all services prepared successfully, even if commit/rollback has individual service failures. Return `false` if any service failed to prepare.

**Interface Definitions (Provided):**

```java
import java.util.UUID;

interface Service {
    boolean prepare(UUID transactionId, OperationData operationData);
    void commit(UUID transactionId);
    void rollback(UUID transactionId);
}

interface OperationData {
    // Represents the data needed to perform an operation on a service.
    // (e.g., account IDs, amount to transfer)
}

```

**Constraints and Considerations:**

*   **Concurrency:**  The `prepare`, `commit`, and `rollback` operations on different services *must* be executed in parallel to minimize transaction latency.  Use appropriate concurrency mechanisms (e.g., ExecutorService, CompletableFuture) to achieve this.
*   **Idempotency:** The provided `Service` implementations are *not guaranteed* to be idempotent.  Your coordinator must handle potential duplicate `commit` or `rollback` calls gracefully and prevent errors due to repeated operations. Specifically, if a service fails to commit/rollback and is retried, it must not cause issues. Assume that a service will respond with success to a `commit` or `rollback` request for a `transactionId` that it has already successfully committed/rolled back.
*   **Error Handling:**  Services may fail to `prepare`, `commit`, or `rollback`.  Your coordinator must handle these failures gracefully.  Log any errors encountered during `commit` or `rollback` operations, but continue processing the other services. **Do not throw exceptions from the `executeTransaction` method.** The return value indicates overall success/failure of the prepare phase.
*   **Deadlock Avoidance:**  While not explicitly required to *detect* deadlocks, design your solution to minimize the *risk* of deadlocks. Assume the services may internally use locking mechanisms. Ordering of service preparation could be a factor.
*   **Optimization:**  Minimize the overall transaction execution time.  Parallelization is crucial.
*   **Scalability:**  Consider how your design could be adapted to handle a large number of services and concurrent transactions.  (While you don't need to implement scaling mechanisms, think about the implications of your design on scalability.)
*   **Logging:** Use `System.err.println` to log any errors during commit or rollback phases. Include the `transactionId` and the service involved in the error message.

This problem requires a strong understanding of distributed systems concepts, concurrency, and error handling. Good luck!
