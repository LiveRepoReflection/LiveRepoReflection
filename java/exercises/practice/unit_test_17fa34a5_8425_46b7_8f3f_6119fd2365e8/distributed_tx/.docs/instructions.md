## Question: Distributed Transaction Coordinator

### Question Description

You are tasked with designing and implementing a simplified, in-memory Distributed Transaction Coordinator (DTC) for a microservices architecture. This DTC will ensure Atomicity, Consistency, Isolation, and Durability (ACID) properties for transactions spanning multiple services.

**Scenario:**

Imagine an e-commerce platform where placing an order involves two microservices: a `PaymentService` and an `InventoryService`. To ensure data integrity, both services must either succeed in their respective operations (charging the customer and reserving inventory) or both must fail (if payment fails, inventory should not be reserved).

**Your Goal:**

Implement a `TransactionCoordinator` class that manages the execution of transactions involving multiple `Resource` instances (representing the microservices). The coordinator should use a two-phase commit (2PC) protocol to guarantee atomicity.

**Specific Requirements:**

1.  **Resource Interface:** Define an interface `Resource` with two methods:
    *   `prepare(TransactionContext context)`: This method simulates a "prepare" phase in the 2PC protocol. The resource should attempt to perform its part of the transaction (e.g., reserve inventory, pre-authorize payment). It should return `true` if successful, and `false` if it encounters an error. Implement a retry mechanism with exponential backoff for transient failures. The context will include the transaction ID.
    *   `commit(TransactionContext context)`: This method simulates the "commit" phase. The resource should permanently apply the changes made during the prepare phase.  It should return `true` if successful, and `false` if it encounters an error.  If a commit fails, the resource should log the error and attempt to rollback. Throw an exception if rollback also fails.
    *   `rollback(TransactionContext context)`: This method simulates the "rollback" phase. The resource should undo any changes made during the prepare phase. It should return `true` if successful, and `false` if it encounters an error.

2.  **TransactionContext:** Create a class `TransactionContext` that holds relevant information for each transaction, such as a unique `transactionId` (UUID) and any shared data required by the resources.

3.  **TransactionCoordinator Class:** Implement a `TransactionCoordinator` class with the following methods:
    *   `beginTransaction()`:  Starts a new transaction by generating a unique `transactionId` and creating a `TransactionContext`. Returns the `TransactionContext`.
    *   `enlistResource(TransactionContext context, Resource resource)`: Adds a `Resource` to the transaction represented by the given `TransactionContext`.
    *   `commitTransaction(TransactionContext context)`:  Executes the 2PC protocol for all enlisted resources within the given `TransactionContext`.
        *   **Phase 1 (Prepare):**  Call the `prepare()` method on each resource. If any `prepare()` call returns `false`, immediately abort the transaction and initiate rollback.
        *   **Phase 2 (Commit):** If all `prepare()` calls succeed, call the `commit()` method on each resource. If any `commit()` call fails, attempt to rollback all committed resources. If rollback fails, log the error and throw an exception.
    *   `rollbackTransaction(TransactionContext context)`: Rolls back the transaction for all enlisted resources within the given `TransactionContext`. This should be called if any prepare phase fails.

**Constraints and Edge Cases:**

*   **Concurrency:** The `TransactionCoordinator` should be thread-safe to handle concurrent transaction requests.
*   **Idempotency:** The `prepare()`, `commit()`, and `rollback()` methods of the `Resource` interface should be idempotent. Meaning calling them multiple times with the same `TransactionContext` should have the same effect as calling them once.
*   **Resource Failure:** Simulate resource failures by randomly making `prepare()`, `commit()`, and `rollback()` methods return `false`. Implement a robust retry mechanism with exponential backoff and a maximum number of retries for `prepare`. For `commit` and `rollback` failures, attempt to rollback/compensate and log errors extensively.
*   **Deadlock Prevention:** Implement a basic deadlock prevention mechanism (e.g., resource locking with timeouts) if necessary, considering the possibility of multiple concurrent transactions accessing the same resources.  Assume resources are identified by a String ID.
*   **Logging:** Implement detailed logging to track the progress of each transaction, including prepare, commit, and rollback events, along with any errors encountered.
*   **Optimizations:** Consider optimization techniques for performance, such as parallelizing prepare and commit/rollback phases where appropriate.

**Evaluation Criteria:**

*   **Correctness:** The code must correctly implement the 2PC protocol and guarantee ACID properties.
*   **Robustness:** The code must handle resource failures, concurrency, and idempotency gracefully.
*   **Efficiency:** The code should be optimized for performance, considering the overhead of distributed transactions.
*   **Code Quality:** The code should be well-structured, readable, and maintainable, with clear comments and appropriate error handling.

This problem requires a deep understanding of distributed systems concepts, transaction management, concurrency, and error handling. It challenges the solver to design and implement a robust and efficient solution for ensuring data consistency in a microservices environment. Good luck!
