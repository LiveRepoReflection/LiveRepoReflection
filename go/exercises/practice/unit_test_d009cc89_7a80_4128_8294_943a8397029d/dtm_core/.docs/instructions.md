## Problem Title: Distributed Transaction Manager

### Question Description

You are tasked with designing and implementing a simplified, yet robust, distributed transaction manager (DTM) for a microservices architecture. This DTM must ensure atomicity across multiple service calls, adhering to the ACID properties.

Imagine a scenario where an e-commerce platform orchestrates transactions across several services: `InventoryService`, `PaymentService`, and `OrderService`. A single order placement involves reserving inventory, processing payment, and creating the order record. Failure in any of these steps should roll back the entire transaction.

Your DTM should provide the following functionalities:

1.  **Transaction Coordination:** Initiate, track, and finalize distributed transactions.
2.  **Two-Phase Commit (2PC) Protocol:** Implement the 2PC protocol to ensure atomicity.
    *   **Prepare Phase:** The DTM sends a "prepare" request to all participating services. Each service attempts to perform its part of the transaction and responds with either a "commit" or "rollback" vote.
    *   **Commit/Rollback Phase:** Based on the votes received, the DTM sends a "commit" or "rollback" command to all services. Services then execute the command.
3.  **Idempotency:** Ensure that all operations (prepare, commit, rollback) are idempotent.  Services might receive the same command multiple times due to network issues or DTM retries.
4.  **Crash Recovery:** The DTM must be able to recover from crashes and complete or rollback transactions that were in progress. Assume a persistent storage mechanism (e.g., a database) is available for the DTM.
5.  **Timeout Handling:** Implement timeout mechanisms.  If a service does not respond within a reasonable time during the prepare phase, the DTM should trigger a rollback.

**Constraints:**

*   Assume the `InventoryService`, `PaymentService`, and `OrderService` expose simple HTTP endpoints for `prepare`, `commit`, and `rollback` operations.  You don't need to implement these services; you only need to interact with them. The endpoints return a JSON response with a `status` field that can be either `"commit"` or `"rollback"`. In case of success, `"commit"` must be returned, otherwise `"rollback"` must be returned. Example: `{"status": "commit"}`.
*   The number of participating services in a transaction is variable and can be configured dynamically.
*   The DTM should be designed for concurrency. Multiple transactions can run simultaneously.
*   You should minimize the impact of the DTM on the performance of the individual services.
*   The DTM should be highly available. Assume a load balancer is used in front of the DTM nodes.

**Specific Requirements:**

*   Implement the core logic of the DTM in Go.
*   Provide clear and well-structured code.
*   Consider using appropriate data structures for tracking transaction states and participant information.
*   Implement appropriate logging and error handling.
*   The solution should demonstrate how the 2PC protocol is implemented to ensure atomicity.
*   The solution should handle scenarios where services are temporarily unavailable during the prepare or commit/rollback phases.

**Bonus (Optional):**

*   Implement a mechanism for detecting and resolving long-running transactions (e.g., transactions that are stuck in the "prepare" state for an extended period).
*   Implement a command-line interface (CLI) for monitoring and managing transactions within the DTM.

This problem requires a deep understanding of distributed systems concepts, transaction management, and concurrency control. It also demands careful consideration of error handling, fault tolerance, and performance optimization. Good luck!
