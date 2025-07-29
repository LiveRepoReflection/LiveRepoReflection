## Problem: Distributed Transaction Coordinator

### Question Description

You are tasked with designing and implementing a simplified, yet robust, distributed transaction coordinator (DTC) for a system involving multiple independent services (databases, message queues, etc.). This DTC must guarantee the ACID properties (Atomicity, Consistency, Isolation, Durability) across these services, specifically focusing on atomicity.

Imagine you have a series of microservices, each responsible for a specific part of a complex operation. To complete this operation successfully, all services must either commit their changes or rollback entirely, as if the operation never happened.  Your DTC will manage this "all or nothing" behavior.

**System Architecture:**

*   **Services:** Multiple independent services participate in transactions. Each service has its own local transaction management (e.g., database transactions).  Each service exposes an API to `prepare`, `commit`, and `rollback` a transaction. These calls are idempotent.
*   **DTC (Your Implementation):** A single DTC instance is responsible for orchestrating the distributed transactions.
*   **Communication:** Services communicate with the DTC over a reliable network (assume no message loss, but messages may be delayed or arrive out of order). You can use in-memory structures to simulate the network.
*   **Transaction ID:** Every distributed transaction is assigned a unique ID (UUID).

**Requirements:**

1.  **Two-Phase Commit (2PC) Protocol:** Implement the 2PC protocol to ensure atomicity. Your DTC should follow these steps:

    *   **Prepare Phase:** The DTC sends a `prepare` request to all participating services. Each service attempts to prepare the transaction locally (e.g., by writing a tentative record). If a service successfully prepares, it responds with a `prepared` message. If a service fails to prepare (e.g., due to insufficient funds, data conflict), it responds with a `abort` message. If a service fails to respond within a specified timeout, the DTC should treat the response as `abort`.
    *   **Commit/Rollback Phase:** If *all* services respond with `prepared`, the DTC sends a `commit` request to all services. If *any* service responds with `abort` (or times out during prepare), the DTC sends a `rollback` request to all services.
    *   **Idempotency:** All service operations (prepare, commit, rollback) *must* be idempotent. This is crucial to handle potential message retransmissions or DTC failures.

2.  **Logging:** The DTC must maintain a persistent log of its decisions (commit or rollback). This log is crucial for recovery in case of a DTC crash.  For simplicity, use an in-memory representation of the log, but design the code to allow for easy swapping to a file-based log. The log should record at least the transaction ID, the participating services, and the final decision (commit or rollback).

3.  **Timeout Handling:** Implement timeouts for all network calls to services. If a service doesn't respond within a reasonable timeframe, the DTC should consider the service as having failed and proceed with a rollback. The timeout value must be configurable.

4.  **Concurrency:** The DTC must be able to handle multiple concurrent transactions. Ensure thread safety and avoid race conditions.

5.  **Failure Recovery:** Design (but do not implement) a recovery mechanism for the DTC. Clearly describe the steps the DTC would take upon restart to recover its state and ensure the consistency of any in-flight transactions.

**Constraints:**

*   Minimize latency for transaction completion.
*   Maximize throughput of concurrent transactions.
*   Design for scalability (consider how the DTC could be scaled horizontally).
*   The solution should be robust and handle potential errors gracefully.
*   Assume the services themselves do not fail permanently during the transaction.
*   Assume the network is reliable, but messages may be delayed or arrive out of order.

**Input:**

The input will be a list of transactions. Each transaction will consist of a unique transaction ID (UUID) and a list of participating service IDs. You will need to simulate the services and their responses to the DTC's requests.

**Output:**

Your code should output the status of each transaction (committed or rolled back) and any relevant error messages. Also, output the DTC's log.

**Evaluation:**

Your solution will be evaluated based on:

*   Correctness: Does it correctly implement the 2PC protocol and ensure atomicity?
*   Robustness: Does it handle timeouts, concurrency, and potential errors gracefully?
*   Efficiency: Is the solution optimized for latency and throughput?
*   Scalability: Is the design scalable?
*   Code Quality: Is the code well-structured, readable, and maintainable?
*   Recovery Design: Is the recovery mechanism well-thought-out?
