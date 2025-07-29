Okay, here's a problem designed to be challenging and complex, fitting the LeetCode Hard difficulty.

### Project Name

```
distributed-transaction-coordinator
```

### Question Description

You are tasked with implementing a simplified, in-memory distributed transaction coordinator (DTC) in Go. This DTC will manage transactions across multiple services. These services expose simple HTTP endpoints for performing operations and confirming or canceling operations.

**Scenario:**

Imagine an e-commerce system where placing an order involves multiple services: `InventoryService`, `PaymentService`, and `ShippingService`. To ensure data consistency, the order placement process must be atomic: either all services successfully process their part of the order, or none do.

**Requirements:**

1.  **Transaction Coordination:** Implement a DTC that can initiate, commit, and rollback distributed transactions across the services.
2.  **Two-Phase Commit (2PC):** Use the 2PC protocol to ensure atomicity. The DTC acts as the coordinator, and the services act as participants.
3.  **Service Discovery:** Assume services register with the DTC by providing their URLs for the `Prepare`, `Commit`, and `Rollback` operations.  Implement a simple, in-memory service registry within the DTC.
4.  **Concurrency:**  The DTC must handle concurrent transaction requests safely and efficiently. Use appropriate synchronization mechanisms (e.g., mutexes, channels) to prevent race conditions.
5.  **Timeout:** Implement a timeout mechanism. If a service doesn't respond to a `Prepare`, `Commit`, or `Rollback` request within a specified timeout, the transaction should be rolled back.
6.  **Idempotency:** Each service must guarantee that the `Prepare`, `Commit`, and `Rollback` operations are idempotent.  The DTC may retry requests in case of network failures or timeouts.  (This is more of a design constraint, but it impacts how services are called).
7.  **Error Handling:**  Implement robust error handling. The DTC should gracefully handle service failures, network errors, and invalid responses.  Log errors appropriately.
8.  **Transaction Status:** The DTC should maintain a record of each transaction's status (e.g., `PENDING`, `PREPARED`, `COMMITTED`, `ROLLEDBACK`).
9. **Deadlock Prevention**: Implement a strategy to detect and resolve deadlocks. The coordinator should maintain a dependency graph of transactions that are waiting on each other, and resolve deadlocks by aborting the transaction with the fewest number of participants.

**Service Interface:**

Each participating service must expose the following HTTP endpoints:

*   `/prepare`:  Receives a transaction ID.  The service attempts to tentatively perform its part of the transaction and responds with `200 OK` if successful, or a `500 Internal Server Error` if it cannot prepare.  It should hold any resources required for the transaction until a commit or rollback is received.
*   `/commit`: Receives a transaction ID. The service permanently commits its part of the transaction. Responds with `200 OK` on success, `500` on failure.
*   `/rollback`: Receives a transaction ID. The service rolls back its part of the transaction, releasing any held resources. Responds with `200 OK` on success, `500` on failure.

**Constraints:**

*   The DTC and services should be implemented as separate Go packages or files.
*   Use standard Go libraries for HTTP requests and concurrency primitives.  No external transaction management libraries are allowed.
*   Focus on correctness, robustness, and concurrency safety. Performance is secondary, but avoid obvious inefficiencies.
*   Assume a relatively small number of services and transactions.  Scalability to thousands of services and transactions is not a primary concern.
*   The system should be resilient to temporary network failures.

**Input:**

The input consists of the registration of services with the DTC, followed by requests to initiate transactions.  The DTC's configuration (e.g., timeout duration) may also be provided.  The specific format of the input (e.g., command-line arguments, configuration file) is left to the solver's discretion.

**Output:**

The output should be the status of each transaction (e.g., `COMMITTED`, `ROLLEDBACK`) and any relevant error messages logged by the DTC.  The output format is also left to the solver's discretion, but it should be clear and informative.

**Judging Criteria:**

*   Correctness: Does the DTC correctly implement the 2PC protocol and ensure atomicity?
*   Concurrency Safety: Does the DTC handle concurrent transaction requests without race conditions?
*   Robustness: Does the DTC handle service failures, network errors, and timeouts gracefully?
*   Error Handling: Are errors handled and logged appropriately?
*   Code Quality: Is the code well-structured, readable, and maintainable?
*   Deadlock prevention: Does the DTC correctly implement deadlock prevention?

This problem requires a good understanding of distributed systems concepts, concurrency, error handling, and the 2PC protocol. It also requires careful design and implementation to ensure correctness and robustness. Good luck!
