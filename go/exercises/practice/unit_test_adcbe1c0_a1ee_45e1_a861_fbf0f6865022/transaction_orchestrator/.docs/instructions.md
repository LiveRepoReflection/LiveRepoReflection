## Problem: Distributed Transaction Orchestrator

**Description:**

You are tasked with designing and implementing a simplified distributed transaction orchestrator. This orchestrator manages transactions across multiple independent services. Each service exposes an API with `Prepare`, `Commit`, and `Rollback` endpoints. A single transaction involves calls to multiple services to perform a logical unit of work.

Your orchestrator should ensure ACID (Atomicity, Consistency, Isolation, Durability) properties for these distributed transactions. Due to the inherent limitations of real-world systems, we'll focus on eventual consistency and minimizing the impact of failures.

**Scenario:**

Imagine an e-commerce system where placing an order involves the following services:

1.  **Inventory Service:** Reserves items from stock.
2.  **Payment Service:** Processes the payment.
3.  **Shipping Service:** Creates a shipping order.

A successful order placement requires all three services to successfully complete their respective operations. If any service fails, all other services must roll back their changes to maintain data consistency.

**Requirements:**

1.  **Transaction Definition:** Implement a mechanism for defining transactions. A transaction consists of a list of services to be called and the order in which they should be executed.
2.  **Two-Phase Commit (2PC) Implementation:** Implement a 2PC protocol to coordinate the transaction.
    *   **Prepare Phase:** The orchestrator sends a `Prepare` request to each service in the transaction. Each service attempts to perform its operation and returns a success or failure indication.
    *   **Commit/Rollback Phase:** If all services successfully prepared, the orchestrator sends a `Commit` request to each service. If any service failed during the prepare phase, the orchestrator sends a `Rollback` request to all services.
3.  **Idempotency:** Ensure that `Commit` and `Rollback` operations are idempotent. Services should be able to handle duplicate `Commit` or `Rollback` requests without adverse effects.
4.  **Fault Tolerance:**
    *   **Retry Mechanism:** Implement a retry mechanism for failed `Prepare`, `Commit`, and `Rollback` requests.  Introduce a maximum number of retries and an exponential backoff strategy.
    *   **Timeout Handling:**  Implement timeouts for `Prepare`, `Commit`, and `Rollback` requests. If a service does not respond within the timeout, consider the request as failed and initiate a rollback.
5.  **Concurrency:** The orchestrator should be able to handle multiple concurrent transactions.
6.  **Logging:** Implement detailed logging to track the progress of transactions, including all `Prepare`, `Commit`, and `Rollback` requests and responses.  This logging is crucial for debugging and auditing.
7.  **Deadlock Prevention:** Assume the services may have internal locking mechanisms. Design the orchestrator to minimize the risk of deadlocks across services.  Consider the order in which services are called, and whether there's a natural ordering to exploit.
8.  **Optimistic Concurrency Control:** The orchestrator should implement optimistic concurrency control.  Each service call should include a version number or timestamp of the data being modified.  The service should reject the request if the version number is outdated (meaning the data has been modified by another transaction). This helps prevent lost updates.
9. **Service Discovery:** Implement a simple service discovery mechanism. Assume you have a configuration file that maps service names to their respective URLs. The orchestrator should read this configuration and use it to communicate with the services.

**Constraints:**

*   Assume the services are black boxes. You do not have access to their internal implementation.
*   You can simulate service failures (e.g., by randomly returning errors or introducing delays).
*   Focus on the core transaction orchestration logic.  You do not need to implement the actual business logic within the services.
*   All communication between the orchestrator and services should be done over HTTP (you can use Go's `net/http` package).
*   The orchestrator should be implemented as a standalone Go application.
*   The number of services involved in a transaction is limited to a maximum of 10.
*   The orchestrator should efficiently handle a large number of concurrent transactions (up to 1000).

**Evaluation Criteria:**

*   Correctness: The orchestrator should correctly implement the 2PC protocol and ensure ACID properties.
*   Fault Tolerance: The orchestrator should be resilient to service failures and network issues.
*   Concurrency: The orchestrator should be able to handle multiple concurrent transactions efficiently.
*   Code Quality: The code should be well-structured, readable, and maintainable.
*   Performance: The orchestrator should minimize the latency of transactions.
*   Logging: The logging should be comprehensive and informative.
*   Deadlock Prevention: The design should minimize the risk of deadlocks.
*   Optimistic Concurrency Control: The orchestrator should effectively implement OCC to prevent lost updates.

This problem requires a deep understanding of distributed systems concepts, concurrency, error handling, and algorithm design. Good luck!
