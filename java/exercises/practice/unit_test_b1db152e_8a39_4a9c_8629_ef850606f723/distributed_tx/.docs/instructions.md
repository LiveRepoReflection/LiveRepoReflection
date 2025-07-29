## Project Name

`DistributedTransactionManager`

## Question Description

You are tasked with designing and implementing a simplified distributed transaction manager for a microservices architecture. This system needs to ensure atomicity across multiple services when a single business operation requires modifications in several of them.

Imagine an e-commerce application where placing an order involves:

1.  Reserving inventory in the `InventoryService`.
2.  Creating an order record in the `OrderService`.
3.  Deducting payment from the `PaymentService`.

If any of these steps fail, the entire operation must be rolled back to maintain data consistency.

**Your Goal:**

Design and implement a `DistributedTransactionManager` class that coordinates transactions across these (simulated) microservices. You need to provide two core functionalities: `beginTransaction()` and `commitTransaction()`.

**Specific Requirements:**

1.  **Transaction ID Generation:** The `beginTransaction()` method should generate a unique transaction ID (UUID).

2.  **Service Registry:** You must be able to register services (represented by a simple interface `TransactionalService`) with the `DistributedTransactionManager`. Each service provides methods to `prepare()`, `commit()`, and `rollback()` operations.

    ```java
    interface TransactionalService {
        boolean prepare(UUID transactionId, Object data);
        boolean commit(UUID transactionId);
        boolean rollback(UUID transactionId);
    }
    ```
    The `prepare()` method is called before the commit. It should perform pre-commit validation and resource locking.

3.  **Two-Phase Commit (2PC) Protocol:**
    *   `commitTransaction(UUID transactionId, Object data)` method should initiate the 2PC protocol:
        *   **Prepare Phase:**  Iterate through registered services and call their `prepare()` methods with the `transactionId` and an object containing the data needed to complete the transaction.  If **any** `prepare()` call fails (returns `false`), the entire transaction should be rolled back. The `prepare()` phase should be implemented with a timeout. If the `prepare()` method does not return within the timeout, the transaction should be rolled back.
        *   **Commit Phase:** If all `prepare()` calls succeed, iterate through the registered services again and call their `commit()` methods.
    *   **Rollback:** If any `prepare()` call fails, or if the timeout is reached, iterate through the registered services and call their `rollback()` methods. Rollback should also happen in the event of a failure in the commit phase.

4.  **Idempotency:** Implement the `prepare()`, `commit()`, and `rollback()` methods such that they are idempotent. Meaning, calling these methods multiple times with the same `transactionId` does not change the outcome.

5.  **Concurrency:** The `DistributedTransactionManager` must be thread-safe. Multiple transactions can be initiated and committed concurrently.

6.  **Timeout:** The `prepare` phase should implement a timeout. If a service does not respond within a specified time, the transaction should be rolled back.

7.  **Error Handling:** Implement proper error handling, logging, and exception management.

8. **Resource contention:** Each service has limited resources. Simulate this by limiting the number of concurrent `prepare` calls that each service can handle. If a service exceeds its concurrency limit, the `prepare` call should fail.

**Constraints:**

*   Focus on the core transaction management logic. You don't need to implement actual microservices.  Instead, create mock implementations of `TransactionalService` to simulate their behavior.

*   Assume that network communication between the `DistributedTransactionManager` and the services is reliable (no network partitions to handle).
*   Keep the design as simple as possible while meeting the requirements.
*   Optimize for concurrency and minimizing blocking.

**Evaluation Criteria:**

*   Correctness: Does the implementation correctly implement the 2PC protocol and ensure atomicity?
*   Concurrency: Is the implementation thread-safe and able to handle concurrent transactions?
*   Idempotency: Are the `prepare()`, `commit()`, and `rollback()` methods idempotent?
*   Error Handling: Does the implementation handle errors gracefully and provide informative logging?
*   Efficiency: Does the implementation minimize blocking and optimize for performance?
*   Code Quality: Is the code well-structured, readable, and maintainable?

This problem requires a solid understanding of distributed systems concepts, concurrency, and exception handling. Good luck!
