## Project Name

`DistributedTransactionManager`

## Question Description

You are tasked with designing and implementing a simplified, yet robust, distributed transaction manager. This system will coordinate transactions across multiple independent services (databases, message queues, external APIs, etc.) to ensure atomicity, consistency, isolation, and durability (ACID properties).

**Scenario:**

Imagine an e-commerce application where placing an order involves several steps:

1.  Reserving the inventory in the `InventoryService`.
2.  Creating an order record in the `OrderService`.
3.  Charging the customer's credit card via the `PaymentService`.
4.  Publishing a message to a `ShippingQueue` to initiate shipment.

Each of these services operates independently and may use different technologies (e.g., different databases, message brokers). A failure in any of these services must roll back the entire transaction to maintain data consistency.

**Requirements:**

1.  **Transaction Coordination:** Implement a `TransactionManager` class that can coordinate transactions across multiple `Participant` services.
2.  **Two-Phase Commit (2PC):**  Implement a simplified 2PC protocol.
    *   **Phase 1 (Prepare):** The `TransactionManager` sends a `prepare()` request to all `Participant` services. Each `Participant` attempts to perform its operation and returns a vote (`COMMIT` or `ROLLBACK`).
    *   **Phase 2 (Commit/Rollback):** Based on the votes received:
        *   If all `Participant`s vote `COMMIT`, the `TransactionManager` sends a `commit()` request to all participants.
        *   If any `Participant` votes `ROLLBACK`, the `TransactionManager` sends a `rollback()` request to all participants.
3.  **Participant Interface:** Define an interface `Participant` that each service must implement. This interface should include `prepare()`, `commit()`, and `rollback()` methods.  These methods should simulate performing an action (e.g., reserving inventory) and potentially throwing an exception to simulate a failure.
4.  **Idempotency:** Ensure that `commit()` and `rollback()` operations are idempotent.  A service should be able to handle receiving the same `commit()` or `rollback()` request multiple times without adverse effects.
5.  **Transaction Logging:** Implement a basic transaction log to record the transaction state (preparing, committing, rolling back, completed). This log should be used to recover from `TransactionManager` failures. If the `TransactionManager` crashes after sending prepare but before completing the transaction, on restart, it should check the transaction log and proceed with the appropriate commit or rollback.
6.  **Concurrency:** Handle concurrent transaction requests safely, ensuring that transactions are properly isolated from each other.  Consider using appropriate synchronization mechanisms (e.g., locks) to prevent race conditions.
7.  **Timeout Handling:** Implement a timeout mechanism for the prepare phase. If a participant doesn't respond within a specified timeout, the transaction should be rolled back.

**Constraints:**

*   **Simulate Services:** You do not need to implement actual Inventory, Order, Payment, and Shipping services. Instead, simulate their behavior using simple classes that implement the `Participant` interface.
*   **No External Libraries (Except for basic utilities):**  You are allowed to use standard Java libraries (e.g., `java.util.concurrent`, `java.io`), but you are not allowed to use external transaction management libraries or frameworks.
*   **Error Handling:** Implement robust error handling to deal with network failures, service unavailability, and other potential issues.
*   **Logging:** Include basic logging to track the progress of transactions and aid in debugging.

**Considerations:**

*   **Scalability:** While not a primary requirement, consider how your design could be scaled to handle a large number of concurrent transactions and participants.
*   **Fault Tolerance:**  How can the system be made more resilient to failures of the `TransactionManager` or individual `Participant` services?

This problem requires a good understanding of distributed systems concepts, concurrency, and error handling. It challenges the solver to design a robust and efficient transaction management system from the ground up. Good luck!
