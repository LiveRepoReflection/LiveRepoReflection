## Question: Distributed Transaction Manager

### Project Name:

`dtm`

### Question Description:

You are tasked with designing and implementing a simplified distributed transaction manager (DTM) in Java. This DTM will coordinate transactions across multiple independent services. The goal is to ensure atomicity; either all services commit their changes, or all services rollback.

**Scenario:**

Imagine an e-commerce system where placing an order involves multiple services:

1.  **Inventory Service:** Reserves the required quantity of items.
2.  **Payment Service:** Processes the payment.
3.  **Shipping Service:** Creates a shipping order.

A distributed transaction is needed to ensure that if any of these steps fail, all changes are rolled back, preventing inconsistencies like deducting inventory without receiving payment.

**Requirements:**

1.  **Transaction Coordination:** Implement a central coordinator (the DTM) that manages the transaction lifecycle. This coordinator should support the following operations:
    *   `begin()`: Starts a new distributed transaction and returns a unique transaction ID.
    *   `enlist(transactionId, service)`: Registers a service with the specified transaction. The `service` is an interface described below.
    *   `commit(transactionId)`: Initiates the commit process for all enlisted services.
    *   `rollback(transactionId)`: Initiates the rollback process for all enlisted services.

2.  **Two-Phase Commit (2PC) Protocol:** The DTM should implement the 2PC protocol to ensure atomicity. The protocol consists of two phases:
    *   **Prepare Phase:** The DTM sends a `prepare()` request to all enlisted services. Each service attempts to perform its local transaction and returns a "vote" (either commit or rollback).
    *   **Commit/Rollback Phase:** Based on the votes received during the prepare phase, the DTM sends either a `commit()` or `rollback()` request to all services.

3.  **Service Interface:** Define a `Service` interface with the following methods:
    *   `prepare(transactionId)`: Attempts to perform the service's local transaction. Returns `true` to vote commit, `false` to vote rollback. This method should be designed to be idempotent. It might be called multiple times.
    *   `commit(transactionId)`: Commits the service's local transaction. This method should also be idempotent.
    *   `rollback(transactionId)`: Rolls back the service's local transaction. This method should also be idempotent.

4.  **Fault Tolerance:** Implement basic fault tolerance to handle service failures during the transaction lifecycle. If a service fails to respond during the prepare phase, assume a rollback vote. If a service fails to respond during the commit/rollback phase, retry the operation a reasonable number of times (e.g., 3 retries with exponential backoff). Log these failures.

5.  **Concurrency:** The DTM should support concurrent transactions. Ensure that transactions are isolated from each other.

6.  **Idempotency:** The `prepare`, `commit`, and `rollback` methods of the `Service` interface *must* be idempotent. Implementations must ensure that executing the same operation multiple times has the same effect as executing it once. This is critical for handling retries due to failures.

**Constraints:**

*   You can use standard Java libraries. External libraries for transaction management are disallowed to increase the difficulty. Focus on implementing the core logic yourself.
*   Simulate service behavior (e.g., reserve inventory, process payment) with simple operations. Don't implement actual external service calls. Use in-memory data structures.
*   Focus on the transaction management aspects, not on the specific business logic of the services.
*   Keep the code concise and well-structured.
*   Prioritize correctness and robustness over performance in this exercise, but keep algorithmic efficiency in mind.
*   Handle potential `Exceptions` gracefully within your DTM and service implementations.

**Example Usage:**

```java
DTM dtm = new DTM();
String transactionId = dtm.begin();

InventoryService inventory = new InventoryService();
PaymentService payment = new PaymentService();
ShippingService shipping = new ShippingService();

dtm.enlist(transactionId, inventory);
dtm.enlist(transactionId, payment);
dtm.enlist(transactionId, shipping);

try {
    dtm.commit(transactionId);
    System.out.println("Transaction committed successfully!");
} catch (TransactionException e) {
    dtm.rollback(transactionId);
    System.err.println("Transaction rolled back: " + e.getMessage());
}
```

**Evaluation Criteria:**

*   Correctness of the 2PC implementation.
*   Handling of service failures and retries.
*   Concurrency support and transaction isolation.
*   Idempotency of service operations.
*   Code structure, readability, and adherence to the requirements.
*   Proper exception handling and logging.

This problem requires a solid understanding of distributed systems concepts, concurrency, and error handling. Good luck!
