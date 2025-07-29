## Problem: Distributed Transaction Coordinator

### Question Description

You are tasked with designing and implementing a simplified distributed transaction coordinator (DTC) for a microservices architecture. This DTC will ensure atomicity across multiple services during a business transaction.

Imagine a scenario where a user wants to transfer funds from their account in Service A to another account in Service B. This transfer requires updates to both services. A naive implementation could lead to inconsistencies if one service succeeds while the other fails. Your DTC aims to solve this.

**Specific Requirements:**

1.  **Transaction Scope:** The DTC must manage a single, flat transaction involving two microservices (Service A and Service B).
2.  **Two-Phase Commit (2PC):** Implement the 2PC protocol. The DTC acts as the coordinator, and Service A and Service B act as participants.
3.  **Service Interaction:**  Assume Service A and Service B expose simple HTTP endpoints for `prepare()` and `commit()/rollback()` operations. The DTC will communicate with these endpoints.
4.  **Concurrency:** The DTC must handle multiple concurrent transactions.
5.  **Failure Handling:** Implement basic failure handling. If a service fails during the prepare phase, the DTC should rollback all participants. If the DTC fails during the commit phase, assume services will eventually resolve themselves, maybe through a recovery process (you don't need to implement recovery).
6.  **Logging:** Implement minimal logging to record transaction states and service interactions. This logging is crucial for debugging and potential recovery strategies.
7.  **Optimistic Locking:** Service A and Service B will use optimistic locking (versioning) on the accounts being updated.  The `prepare()` call should include the expected version of the account. If the version doesn't match on the service side, `prepare()` should return a failure.
8.  **Idempotency:**  The `commit()` and `rollback()` operations in Service A and Service B should be idempotent. The DTC might retry these calls in case of network issues.

**Constraints and Considerations:**

*   **Scalability is NOT a primary concern:** Focus on correctness and clarity over extreme scalability for this challenge.
*   **Keep it simple:** Avoid over-engineering. Focus on the core 2PC logic and failure handling.
*   **Latency is a concern:** Minimize unnecessary communication overhead.

**Input:**

The DTC receives a transaction request containing:

*   `transactionId`: A unique identifier for the transaction.
*   `serviceAAccountId`: The account ID in Service A.
*   `serviceBAccountId`: The account ID in Service B.
*   `amount`: The amount to transfer.
*   `serviceAExpectedVersion`: The expected version number of the account in Service A
*   `serviceBExpectedVersion`: The expected version number of the account in Service B

**Output:**

The DTC should return:

*   `SUCCESS` if the transaction commits successfully.
*   `FAILURE` if any service fails to prepare or if a rollback occurs.

**Example Interaction:**

1.  DTC receives a transaction request.
2.  DTC logs the start of the transaction.
3.  DTC calls `prepare()` on Service A with `transactionId`, `serviceAAccountId`, `amount`, and `serviceAExpectedVersion`.
4.  DTC calls `prepare()` on Service B with `transactionId`, `serviceBAccountId`, `amount`, and `serviceBExpectedVersion`.
5.  If both `prepare()` calls return success:
    *   DTC logs the successful prepare phase.
    *   DTC calls `commit()` on Service A with `transactionId`.
    *   DTC calls `commit()` on Service B with `transactionId`.
    *   DTC logs the successful commit phase.
    *   DTC returns `SUCCESS`.
6.  If either `prepare()` call returns failure:
    *   DTC logs the failure.
    *   DTC calls `rollback()` on Service A with `transactionId`.
    *   DTC calls `rollback()` on Service B with `transactionId`.
    *   DTC logs the rollback.
    *   DTC returns `FAILURE`.

**Bonus:**

*   Implement a timeout mechanism for the `prepare()` phase. If a service doesn't respond within a certain time, assume it has failed and initiate a rollback.
*   Implement a retry mechanism for `commit()` and `rollback()` operations to handle transient network failures.
