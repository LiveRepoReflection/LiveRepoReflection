## Project Name

`Distributed Transaction Manager`

## Question Description

You are tasked with designing and implementing a simplified, but robust, distributed transaction manager (DTM) in Go. This DTM will be responsible for coordinating transactions across multiple independent services (participants). Think of it as a lightweight, in-memory implementation of a two-phase commit (2PC) protocol with added complexities.

**Scenario:**

Imagine an e-commerce platform where placing an order involves several services:

1.  **Inventory Service:** Reserves items in stock.
2.  **Payment Service:** Processes the payment.
3.  **Shipping Service:** Schedules the shipment.

A successful order requires all three services to complete their actions. If any service fails, the entire order transaction must be rolled back.

**Requirements:**

1.  **Transaction Coordination:** The DTM must provide a mechanism to start, commit, and rollback distributed transactions. Each transaction will have a unique transaction ID (UUID).

2.  **Participant Registration:** Services participating in a transaction must register with the DTM, providing:
    *   Transaction ID.
    *   A `Prepare` function (simulating a "prepare" phase – checking if the service can commit). The prepare function can take some input data.
    *   A `Commit` function (simulating a "commit" phase – performing the actual action).
    *   A `Rollback` function (simulating a "rollback" phase – undoing the action).

3.  **Two-Phase Commit (2PC) Emulation:**
    *   **Prepare Phase:** Upon receiving a `Commit` request, the DTM must invoke the `Prepare` function of all registered participants *concurrently*. If *any* `Prepare` function returns an error, the entire transaction must be rolled back. Each `Prepare` function should also return an output message to the DTM, which the DTM will then pass to the commit function as input data.
    *   **Commit Phase:** If all `Prepare` functions succeed, the DTM must invoke the `Commit` function of all registered participants *concurrently*.

4.  **Rollback Mechanism:** If any `Prepare` function fails, or if the DTM receives an explicit `Rollback` request, the DTM must invoke the `Rollback` function of all registered participants *concurrently*. The DTM must guarantee that rollback will eventually be executed.

5.  **Idempotency:** The `Commit` and `Rollback` functions of the participants may be called multiple times. Your DTM must handle this gracefully, ensuring that calling these functions multiple times has the same effect as calling them once. This is critical for handling network issues and potential DTM failures.

6.  **Concurrency:** The DTM must be able to handle multiple concurrent transactions.

7.  **Timeout:** Implement a timeout mechanism. If a participant's `Prepare`, `Commit`, or `Rollback` function takes longer than a specified timeout (e.g., 5 seconds), the DTM should consider the operation failed and initiate a rollback (if in the Prepare phase) or mark the transaction as failed (if in the Commit phase).

8.  **Error Handling:** Provide meaningful error messages for all possible failure scenarios.

9.  **Data Consistency:** Guarantee that even if the DTM itself crashes during any phase (Prepare, Commit, Rollback), upon restart, the system will eventually reach a consistent state (either all services committed or all services rolled back) even without persistence. You do NOT need to implement crash recovery, but the design must demonstrate the ability to guarantee eventual consistency despite such events.

**Constraints:**

*   All operations must be performed asynchronously and concurrently using goroutines and channels.
*   Minimize the use of global state and locks. Favor message passing and immutable data structures.
*   The DTM should be designed with scalability in mind.
*   The participants are assumed to be unreliable, and the DTM needs to be fault-tolerant.

**Bonus (Optional, but highly encouraged):**

*   **Deadlock Detection/Prevention:**  Implement a mechanism to detect or prevent deadlocks that could occur if participants acquire resources in different orders.
*   **Metrics:** Expose metrics (e.g., number of transactions, commit/rollback rates, average transaction duration) for monitoring and debugging.
*   **Optimistic Concurrency Control:** Explore if optimistic concurrency control can be applied to this problem instead of 2PC. Describe the trade-offs.

This problem requires a good understanding of concurrency, distributed systems, and transaction management principles. The focus should be on building a robust, scalable, and fault-tolerant DTM that can handle complex scenarios. Good luck!
