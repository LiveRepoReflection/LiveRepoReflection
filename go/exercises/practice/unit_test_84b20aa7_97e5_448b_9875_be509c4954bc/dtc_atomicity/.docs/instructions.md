## Project Name

```
Distributed Transaction Coordinator
```

## Question Description

You are tasked with designing and implementing a simplified, in-memory distributed transaction coordinator (DTC) that ensures atomicity across multiple independent services. Assume a microservices architecture where each service manages its own data. The DTC must guarantee that a transaction either commits successfully on all participating services or rolls back on all of them, even in the presence of failures.

**Scenario:**

Imagine an e-commerce platform where a single order creation involves multiple services:

*   **Order Service:** Creates the initial order record.
*   **Inventory Service:** Reserves the ordered items in the inventory.
*   **Payment Service:** Processes the payment.

A distributed transaction ensures that all three operations either succeed (order created, inventory reserved, payment processed) or none of them do (e.g., if the payment fails, the order should not be created, and the inventory reservation should be cancelled).

**Requirements:**

1.  **Two-Phase Commit (2PC) Protocol:** Implement the 2PC protocol for coordinating transactions across the services.
2.  **Transaction States:** The DTC must track the state of each transaction (e.g., `PREPARING`, `READY`, `COMMITTING`, `ABORTING`, `COMMITTED`, `ABORTED`).
3.  **Service Registration:** Services must be able to register with the DTC and provide methods to prepare, commit, and rollback a transaction.
4.  **Fault Tolerance:** Handle service failures during the transaction process. If a service fails to respond during the prepare phase, the transaction should be aborted. If a service fails during the commit/rollback phase, the DTC should retry until the operation succeeds or a maximum retry limit is reached.
5.  **Concurrency:** The DTC should handle concurrent transaction requests efficiently.
6.  **Idempotency:**  Assume that the prepare, commit, and rollback operations on each service are idempotent.  The DTC may need to retry operations, and the services must handle duplicate requests gracefully.
7.  **Timeout:** Implement a timeout mechanism for both the prepare and commit/rollback phases. If a service takes too long to respond, the transaction should be aborted.
8. **Data Durability:** Assume the services have their own mechanism to persist their local operations, focus on the in-memory co-ordination aspect of the DTC.
9.  **Logging:** Implement basic logging to track transaction events and aid debugging.

**Constraints:**

*   The DTC and the services are all running in the same environment (single machine for simplicity, although the design should consider distributed deployment).
*   Communication between the DTC and the services can be done using in-memory function calls or channels.
*   Assume a maximum of 10 participating services per transaction.
*   The time spent in prepare, commit and rollback per service is non-deterministic.
*   You can use standard Go libraries for concurrency, data structures, and logging.

**Challenge:**

The primary challenge is to design a robust and efficient DTC that can handle concurrent transactions, service failures, and timeouts while ensuring atomicity. Consider the trade-offs between performance, fault tolerance, and complexity when making design decisions. Optimize for minimal latency and resource consumption while maintaining data consistency.
