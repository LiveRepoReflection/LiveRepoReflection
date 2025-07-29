## Question: Distributed Transaction Manager

### Question Description

You are tasked with designing a simplified distributed transaction manager for a microservices architecture.  Imagine a system where multiple independent services need to participate in a single, atomic transaction.  If any service fails to complete its part of the transaction, the entire transaction must be rolled back across all participating services.

Specifically, you need to implement a system that handles two key operations: *Commit* and *Rollback*.  The system receives requests to perform actions on several microservices. Each action is part of a single distributed transaction and has a unique transaction ID.

Your system should adhere to the following constraints and requirements:

1.  **Microservice Representation:** Each microservice is represented by a simple interface with two methods: `commit(transactionId)` and `rollback(transactionId)`. These methods simulate performing the service's part of the transaction and rolling it back, respectively.  Assume these methods can either succeed or fail (throw an exception).

2.  **Transaction Coordination:** The transaction manager must ensure that all participating services either *all* commit their changes or *all* rollback their changes.

3.  **Two-Phase Commit (2PC):** You need to implement a simplified version of the Two-Phase Commit protocol:

    *   **Phase 1 (Prepare):**  The transaction manager sends a "prepare" message to each participating service, identified by the transaction ID.  Each service attempts to prepare for the commit.  If a service successfully prepares, it should return `true`. If it fails to prepare (e.g., due to resource constraints), it should return `false`.
    *   **Phase 2 (Commit/Rollback):**
        *   If *all* services successfully prepared in Phase 1, the transaction manager sends a "commit" message to each service.
        *   If *any* service failed to prepare in Phase 1, the transaction manager sends a "rollback" message to each service.

4.  **Fault Tolerance:**  The transaction manager should be resilient to failures. If a service fails during the commit or rollback phase, the transaction manager should retry the operation a configurable number of times with exponential backoff before giving up.

5.  **Idempotency:**  The `commit()` and `rollback()` methods on the microservices might be called multiple times for the same transaction ID due to retries.  Ensure your solution handles this gracefully.  (Hint: The microservices themselves do *not* need to be idempotent; your transaction manager should handle ensuring the effects are idempotent).

6.  **Concurrency:** Multiple transactions can be initiated concurrently. Your solution should handle concurrent transactions safely and efficiently.

7.  **Optimization:**  Minimize the overall latency of the transaction. Consider how to parallelize operations where possible.

8.  **Logging:** Implement logging to record the progress of transactions, including prepare, commit, and rollback attempts and their outcomes. Use a standard logging framework.

9.  **Configuration:** The number of retries and the base for the exponential backoff should be configurable.

10. **Scalability:** While you don't need to *actually* deploy this to a large-scale distributed system, consider how your design would scale to handle a large number of services and transactions.  Document any potential bottlenecks and how they might be addressed.

**Input:**

*   A list of `Microservice` instances participating in a transaction.
*   A unique transaction ID (a string).

**Output:**

*   `true` if the transaction committed successfully across all services.
*   `false` if the transaction was rolled back due to a failure in any service.

**Assumptions:**

*   You can assume that the network is reliable (no dropped messages).
*   You do *not* need to handle crash recovery (if the transaction manager itself crashes).

**Evaluation Criteria:**

*   Correctness (passes all test cases).
*   Handling of edge cases and constraints.
*   Efficiency and performance.
*   Code quality, readability, and maintainability.
*   Concurrency safety.
*   Fault tolerance (retry mechanism).
*   Consideration of scalability.
*   Logging quality.
*   Adherence to the Two-Phase Commit protocol.
