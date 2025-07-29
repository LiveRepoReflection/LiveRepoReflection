## Question: Distributed Transaction Coordinator

### Question Description:

You are tasked with building a simplified, in-memory distributed transaction coordinator. This coordinator is responsible for managing transactions that span across multiple independent services.  Each service can perform operations related to a single transaction, and the coordinator ensures either all operations across all services succeed (commit) or all operations are rolled back (abort).

The core functionalities you need to implement are:

1.  **Transaction Initiation:** The coordinator should be able to start a new transaction, assigning it a unique transaction ID (UUID).

2.  **Operation Registration:** Services participating in a transaction need to register their operations with the coordinator. For each operation, the service provides:
    *   The transaction ID.
    *   A `prepare` function (asynchronous). This function represents the service's attempt to prepare the operation for commitment. It can succeed or fail.
    *   A `commit` function (asynchronous). This function represents the service's action to permanently commit the operation.
    *   An `abort` function (asynchronous). This function represents the service's action to undo the operation in case of a rollback.
    *   A timeout value (in milliseconds). If a service doesn't respond within the timeout during prepare, commit, or abort phase, the coordinator should consider the operation failed.

3.  **Two-Phase Commit (2PC) Protocol:** The coordinator must implement the 2PC protocol:
    *   **Prepare Phase:**  After all operations are registered (or after a timeout period since the transaction started, assuming no more operations will be registered), the coordinator initiates the prepare phase.  It calls the `prepare` function for each registered operation *concurrently*. If *any* `prepare` function fails or times out, the entire transaction must be aborted.
    *   **Commit/Abort Phase:** If all `prepare` functions succeed, the coordinator initiates the commit phase, calling the `commit` functions for each operation *concurrently*. If the coordinator detects a failure during the prepare phase, the coordinator initiates the abort phase, calling the `abort` functions for each operation *concurrently*. Any failures or timeouts during commit or abort phases should be logged but *should not* halt the process for other services. The coordinator should continue attempting to commit or abort other registered services.

4.  **Concurrency and Error Handling:** Your implementation must handle concurrent transaction requests and potential errors gracefully.

5.  **Idempotency:**  The prepare, commit, and abort functions *may* be called multiple times.  Your implementation should handle this scenario appropriately.  Think about how to ensure correct behavior even if a service crashes and restarts during the 2PC process.

6.  **Timeout Handling:** Implement proper timeout mechanisms for all asynchronous operations (`prepare`, `commit`, `abort`). If an operation times out, the coordinator should proceed as if the operation failed.

**Constraints:**

*   **Asynchronous Operations:**  All `prepare`, `commit`, and `abort` functions are asynchronous (return Promises).
*   **Concurrency:** Your coordinator should handle multiple concurrent transactions.
*   **No External Libraries (Mostly):** You are encouraged to use built-in Javascript functionality or very minimal libraries to handle concurrency/timeouts (e.g., `setTimeout`, `Promise.all`, `async/await`). Avoid large external libraries for core logic.  You *can* use a UUID library for generating unique transaction IDs.
*   **Memory-Bound:** This is an in-memory coordinator; you don't need to persist state to disk.
*   **Scalability (Conceptual):** Although this is an in-memory solution, consider how your design could be adapted to scale horizontally in a distributed environment.

**Evaluation Criteria:**

*   Correctness: Does the coordinator correctly implement the 2PC protocol?
*   Concurrency Handling: Does the coordinator handle concurrent transactions without race conditions?
*   Error Handling: Does the coordinator handle failures and timeouts gracefully?
*   Idempotency: Are the prepare, commit, and abort functions handled idempotently?
*   Code Quality: Is the code well-structured, readable, and maintainable?
*   Efficiency:  Is the coordinator reasonably efficient in terms of resource usage?

This problem requires a strong understanding of asynchronous programming, concurrency, and distributed systems concepts. Good luck!
