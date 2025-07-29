## Project Name

**Distributed Transaction Coordinator**

## Question Description

You are tasked with designing and implementing a simplified distributed transaction coordinator. This coordinator manages transactions across multiple independent services (simulated as functions in your code). The goal is to ensure ACID properties (Atomicity, Consistency, Isolation, Durability) for transactions that span these services.

Each service exposes an API with two primary operations: `prepare(transaction_id, data)` and `commit(transaction_id)`.  The `prepare` function tentatively applies the changes associated with the transaction using the input `data` but does **not** durably persist them. It returns `True` if the service is ready to commit and `False` otherwise (e.g., due to data conflicts, resource unavailability, or other application-specific reasons). The `commit` function durably persists the changes made by the `prepare` phase. If a service fails to commit, it is assumed to have rolled back its prepared changes.

Your coordinator must implement the following functionality using the Two-Phase Commit (2PC) protocol:

1.  **`begin_transaction()`**:  Assigns a unique transaction ID and returns it.

2.  **`enlist_service(transaction_id, service, data)`**: Registers a service to participate in a transaction. `service` is a callable function that mimics the `prepare` and `commit` API (see service definition below). `data` is the input that will be passed to the service's `prepare` function during the prepare phase.

3.  **`commit_transaction(transaction_id)`**: Executes the 2PC protocol.  It must:
    *   First, invoke the `prepare` function of **all** enlisted services concurrently (e.g., using threads, asyncio, or a similar mechanism) with the given `transaction_id` and respective data.
    *   If **all** `prepare` calls return `True`, then invoke the `commit` function of **all** enlisted services concurrently with the given `transaction_id`.
    *   If **any** `prepare` call returns `False`, then the transaction must be aborted.  No `commit` calls should be made. Aborted transactions leave the services in their original states.
    *   Handle potential service failures during both `prepare` and `commit` phases. If a service fails (raises an exception) during the prepare phase, the transaction must be aborted. If a service fails during the commit phase, retry the commit operation a fixed number of times before giving up.
    *   Return `True` if the transaction commits successfully (all services prepared and committed), and `False` otherwise (any prepare failed, or commit failed after retries).
    *   Ensure that transaction IDs are unique and prevent duplicate commits.
    *   The `commit_transaction` function must be idempotent. That is, calling it multiple times with the same transaction ID should produce the same result as calling it once.

4.  **Service Definition**: The `service` argument passed to `enlist_service` must be a callable object (e.g., a function or a class with a `__call__` method) with the following structure:

    ```python
    class MyService:
        def __init__(self):
            # Initialize service state
            pass

        def prepare(self, transaction_id, data):
            # Tentatively apply changes based on data
            # Return True if ready to commit, False otherwise
            pass

        def commit(self, transaction_id):
            # Durably persist changes
            # Should handle potential failures and be idempotent
            pass

        # Optional rollback method (not directly called by the coordinator,
        #  but useful for testing)
        def rollback(self, transaction_id):
            # Rollback changes made by prepare
            pass
    ```

**Constraints and Considerations:**

*   **Concurrency:**  The `prepare` and `commit` phases must be executed concurrently to maximize performance.
*   **Error Handling:** Your coordinator must gracefully handle service failures and network issues.  Implement retry logic for commit operations.
*   **Idempotency:**  Ensure that the `commit` operation can be called multiple times without causing issues.
*   **Uniqueness:** Ensure that each transaction ID is unique.
*   **Scalability:** While a full-fledged distributed transaction coordinator would require complex mechanisms for scalability and fault tolerance, focus on correctness and handling failures within the given constraints.
*   **Timeouts:** Implement reasonable timeouts for `prepare` and `commit` operations to prevent indefinite blocking in case of service failures. Assume a default timeout of 5 seconds unless otherwise specified.
*   **Logging:** Include basic logging to track the progress of transactions (begin, prepare, commit/abort). This is essential for debugging and understanding the system's behavior.
*   **Resource Management:**  Pay attention to managing resources (e.g., threads, network connections) efficiently to avoid resource exhaustion.
*   **No External Libraries**: Except for threading, time related and logging libraries, you are forbidden to use external libraries.

This problem is designed to assess your understanding of distributed transaction management, concurrency, error handling, and system design principles.  The difficulty lies in coordinating multiple independent services while ensuring data consistency and fault tolerance. Optimization of performance under high load is a secondary concern, but reasonable efficiency is expected.
