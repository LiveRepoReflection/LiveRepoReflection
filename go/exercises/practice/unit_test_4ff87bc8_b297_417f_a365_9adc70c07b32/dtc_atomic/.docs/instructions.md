## Problem: Distributed Transaction Coordinator

**Description:**

You are tasked with building a simplified, in-memory distributed transaction coordinator (DTC) for a microservices architecture.  This DTC must ensure atomicity and consistency across multiple services when performing a single logical transaction.

Imagine a scenario where you have three microservices: `InventoryService`, `PaymentService`, and `ShippingService`. A successful order placement requires:

1.  `InventoryService`: Decreasing the item quantity in inventory.
2.  `PaymentService`: Charging the customer's credit card.
3.  `ShippingService`: Creating a shipping label.

If any of these steps fail, the entire transaction must be rolled back, restoring the system to its original state.

**Requirements:**

1.  **Transaction Management:** Implement the core logic for initiating, committing, and rolling back distributed transactions.  The DTC should be able to orchestrate transactions across an arbitrary number of participating services. Each service action in the transaction should be considered as a 'step' in the transaction.

2.  **Two-Phase Commit (2PC):**  Use the Two-Phase Commit protocol to ensure atomicity.  The DTC acts as the coordinator. The services act as participants.

    *   **Phase 1 (Prepare):** The DTC sends a "prepare" message to all participating services.  Each service attempts to perform its task (e.g., decrease inventory, charge credit card) but *does not commit* the changes.  Instead, it reserves the resources and replies with either "commit-ok" if successful or "rollback-required" if a failure occurs.
    *   **Phase 2 (Commit/Rollback):**  Based on the responses from the prepare phase, the DTC decides whether to commit or rollback the transaction.
        *   If *all* services respond with "commit-ok", the DTC sends a "commit" message to all services.  Each service then permanently applies the changes and acknowledges the commit.
        *   If *any* service responds with "rollback-required" (or the DTC times out waiting for a response), the DTC sends a "rollback" message to all services. Each service then undoes any changes made during the prepare phase and acknowledges the rollback.

3.  **Concurrency & Atomicity:** Your DTC needs to handle concurrent transaction requests. Ensure that transactions are isolated and atomic. Use appropriate synchronization primitives to prevent race conditions and data corruption. Transactions should either fully succeed or have no effect.

4.  **Idempotency:** Each participating service must handle `prepare`, `commit`, and `rollback` requests idempotently. That is, receiving the same request multiple times should have the same effect as receiving it once. This is crucial for handling network issues and potential retries.

5.  **Timeouts:** Implement timeouts for both phases of the 2PC protocol.  If a service fails to respond within a specified time, the DTC should consider it a failure and initiate a rollback.

6.  **Logging:** Implement basic logging to record the progress and outcome of each transaction.  This will be helpful for debugging and auditing.

7.  **Service Simulation:** You are *not* implementing actual microservices. Instead, provide an interface `Service` with `Prepare()`, `Commit()`, and `Rollback()` methods, and simulate the behavior of the microservices. Each service should have a configurable probability of failure during the prepare phase.

**Constraints:**

*   The DTC should be implemented in pure Go, using standard library features as much as possible.  Avoid external dependencies if possible.
*   The system should be designed to handle a moderate number of concurrent transactions.
*   Resource contention should be minimized.
*   Error handling must be robust.

**Optimization Considerations:**

*   Minimize the latency of transaction processing.
*   Optimize resource utilization (e.g., memory, CPU).
*   Consider the scalability of your design.

**Input:**

The input to your program will be a configuration specifying:

*   A list of services, each with:
    *   A unique ID.
    *   A simulated latency for prepare, commit, and rollback operations.
    *   A probability of failure during the prepare phase (e.g., 0.1 for 10% failure rate).
*   The number of concurrent transactions to simulate.
*   The timeout duration for prepare and commit/rollback phases.

**Output:**

Your program should output metrics summarizing the performance of the DTC, including:

*   The number of successful transactions.
*   The number of rolled-back transactions.
*   The average transaction latency.
*   Any errors encountered during transaction processing.
