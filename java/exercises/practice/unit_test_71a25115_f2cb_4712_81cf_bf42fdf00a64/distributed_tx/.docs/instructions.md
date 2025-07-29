## Question: Distributed Transaction Manager

### Question Description

You are tasked with designing and implementing a simplified, in-memory Distributed Transaction Manager (DTM) in Java. This DTM is responsible for coordinating transactions across multiple independent services. Each service has its own local database and can perform operations within its own data context.

**Scenario:**

Imagine an e-commerce system where placing an order involves multiple services:

1.  **Inventory Service:** Checks if the requested items are in stock and reserves them.
2.  **Payment Service:** Processes the payment for the order.
3.  **Shipping Service:** Creates a shipping label and schedules the shipment.

All these operations should happen within a single transaction. If any service fails, the entire transaction must be rolled back to maintain data consistency.

**Requirements:**

1.  **Transaction Coordination:** Implement a `TransactionManager` class with `begin()`, `commit()`, and `rollback()` methods. The `begin()` method should return a unique transaction ID.

2.  **Service Registration:** Services should be able to register with the `TransactionManager`. Each service provides a `prepare()` and `commit()`/`rollback()` function. The `prepare()` function is called to check if the service is ready to commit. If `prepare()` returns `false`, the transaction must be rolled back.

3.  **Two-Phase Commit (2PC) Protocol:** Implement the 2PC protocol for coordinating the transaction.

    *   **Phase 1 (Prepare Phase):** The `TransactionManager` calls the `prepare()` function of all registered services. If all services return `true`, the transaction can proceed to the commit phase.
    *   **Phase 2 (Commit/Rollback Phase):** If all services prepared successfully, the `TransactionManager` calls the `commit()` function of all registered services. If any service failed during prepare, the `TransactionManager` calls the `rollback()` function of all registered services.

4.  **Idempotency:** Ensure that the `commit()` and `rollback()` operations are idempotent.  That is, calling them multiple times has the same effect as calling them once.

5.  **Concurrency:** The `TransactionManager` should handle concurrent transactions safely.  Multiple transactions can be initiated and processed concurrently.

6.  **Timeout Handling:** Implement a timeout mechanism. If a service takes longer than a specified timeout to prepare, commit, or rollback, the `TransactionManager` should consider the service failed and initiate a rollback.

7.  **Failure Handling:**  Handle potential exceptions during `prepare()`, `commit()`, and `rollback()` calls. Log these exceptions and ensure they don't halt the entire transaction process.  If a service fails to commit, the DTM should retry a configurable number of times with exponential backoff before giving up and marking the transaction as failed.

8.  **Logging:** Maintain a log of transaction events, including transaction ID, service names, and the status of each phase (prepare, commit, rollback).  The log should be thread-safe.

**Constraints:**

*   The solution should be implemented in Java.
*   Use appropriate data structures and algorithms to ensure efficiency.
*   Consider thread safety and synchronization when dealing with concurrent transactions.
*   Minimize external dependencies. Focus on core Java libraries.
*   Services are simulated with simple interfaces; no actual database interaction is required.
*   The number of services participating in a transaction is not fixed.

**Bonus Challenges:**

*   Implement a mechanism for detecting and resolving deadlocks between concurrent transactions.
*   Persist the transaction log to disk for recovery purposes.
*   Implement a distributed lock manager to coordinate access to shared resources across services.
*   Allow services to dynamically join and leave the transaction management system.
