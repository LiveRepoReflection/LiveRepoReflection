## Problem: Distributed Transaction Coordinator

**Description:**

You are tasked with designing and implementing a simplified distributed transaction coordinator (DTC) for a microservices architecture. This DTC will orchestrate transactions across multiple independent services, ensuring atomicity (all services commit or all services rollback).

Imagine a scenario where an e-commerce platform needs to update inventory in the `InventoryService`, create an order record in the `OrderService`, and charge the customer in the `PaymentService` as part of a single order placement. If any of these operations fail, the entire transaction must be rolled back.

**Core Requirements:**

1.  **Transaction Initiation:** Your DTC should be able to initiate a distributed transaction, assigning it a unique transaction ID (UUID).

2.  **Service Registration:** Services participating in a transaction must register with the DTC, providing their unique service ID and the URLs for their `prepare`, `commit`, and `rollback` endpoints.

3.  **Two-Phase Commit (2PC) Protocol:** Implement the 2PC protocol:
    *   **Prepare Phase:** The DTC sends a `prepare` request to all registered services. Each service attempts to perform its part of the transaction and responds with `OK` if successful or `ABORT` if it encounters an error.
    *   **Commit/Rollback Phase:**
        *   If all services respond with `OK`, the DTC sends a `commit` request to all services.
        *   If any service responds with `ABORT` (or doesn't respond within a timeout), the DTC sends a `rollback` request to all services.

4.  **Idempotency:** Services MUST implement idempotent `commit` and `rollback` operations. The DTC might send these requests multiple times due to network issues.

5.  **Timeout Handling:** The DTC should handle timeouts. If a service doesn't respond within a specified time limit (e.g., during the `prepare` phase), the DTC should consider it an `ABORT` and initiate a rollback.

6.  **Concurrency:** The DTC must handle multiple concurrent transactions.

7.  **Logging:** Implement logging to track transaction status, service responses, and any errors encountered. This will be crucial for debugging and auditing.

**Constraints:**

*   Assume reliable message delivery *within* a single service. However, communication *between* the DTC and the services might be unreliable.
*   Services cannot directly communicate with each other; all coordination must happen through the DTC.
*   The number of participating services per transaction can vary.
*   The DTC must handle service failures and network partitions gracefully.
*   Focus on core DTC logic; you don't need to implement the actual microservices themselves (e.g., the InventoryService). You can simulate them with simple mock implementations.

**Optimization Requirements:**

*   Minimize the overall transaction latency. Consider strategies for parallelizing `prepare`, `commit`, and `rollback` requests where possible.
*   Design the DTC to be horizontally scalable to handle a large number of concurrent transactions.
*   Avoid deadlocks and race conditions in the DTC's internal state management.

**Real-World Practical Scenarios:**

*   E-commerce order placement (as described above).
*   Financial transactions involving multiple bank accounts.
*   Data migration across multiple databases.

**System Design Aspects:**

*   Consider the architecture of the DTC: How will you store transaction metadata? How will you manage concurrent requests?
*   Think about error handling and recovery mechanisms: What happens if the DTC crashes in the middle of a transaction?
*   How will you monitor the health and performance of the DTC?

**Algorithmic Efficiency Requirements:**

*   The DTC should be efficient in terms of CPU and memory usage.
*   The time complexity of the 2PC protocol should be considered, especially as the number of participating services increases.

**Multiple Valid Approaches:**

There are several ways to design and implement a DTC. Some possible approaches include:

*   Using a state machine to track the transaction lifecycle.
*   Employing a message queue to handle asynchronous communication with services.
*   Using a distributed consensus algorithm (e.g., Raft) for fault tolerance.

Different approaches will have different trade-offs in terms of complexity, performance, and scalability. Choose an approach that best balances these factors.

**Expected Output:**

The solution should provide a working DTC implementation in Java that meets all the specified requirements and constraints. While a full GUI is not required, demonstrate how to initiate transactions, register services, and observe the transaction progress (e.g., through logs or a simple command-line interface).  The solution should be well-documented, explaining the design choices, implementation details, and any limitations.
