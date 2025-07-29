Okay, here's a challenging problem for a programming competition:

**Problem Title:** Distributed Transaction Manager (DTM) Consistency

**Problem Description:**

You are tasked with implementing a simplified, in-memory version of a Distributed Transaction Manager (DTM). The DTM is responsible for ensuring atomicity and consistency across multiple participating services during distributed transactions.

Each participating service is represented by a unique integer ID.  A transaction involves updating data across a subset of these services. The DTM must ensure that either all updates within a transaction are committed successfully, or none are.

Your DTM needs to handle the following requests:

1.  **`begin_transaction(transaction_id)`:**  Starts a new transaction with the given `transaction_id` (an integer).  Transaction IDs are unique.

2.  **`prepare(transaction_id, service_id)`:**  A service with `service_id` indicates that it is ready to commit its portion of the transaction `transaction_id`.  This action should be idempotent (i.e., calling `prepare` multiple times for the same transaction and service should have the same effect as calling it once).

3.  **`commit(transaction_id)`:**  Instructs the DTM to commit the transaction `transaction_id`.  If all participating services have prepared, the commit should succeed. Otherwise, the commit should fail.

4.  **`rollback(transaction_id)`:** Instructs the DTM to rollback the transaction `transaction_id`.  This should effectively undo any `prepare` calls associated with the transaction.

5.  **`get_transaction_state(transaction_id)`:**  Returns the current state of the transaction as a string. The possible states are: "ACTIVE", "PREPARED", "COMMITTED", "ROLLED_BACK", "NON_EXISTENT".

**Constraints and Requirements:**

*   **Atomicity:** Either all prepared services in a transaction must be committed, or all must be rolled back.  Partial commits/rollbacks are not allowed.
*   **Consistency:** The system must maintain a consistent view of transaction states.
*   **Concurrency:** The DTM must be thread-safe. Multiple requests can arrive concurrently from different threads or processes. Use appropriate locking mechanisms to prevent race conditions.
*   **Durability (Simulated):** While this is an in-memory DTM, simulate durability by ensuring that transaction state transitions (e.g., from ACTIVE to PREPARED or COMMITTED) are recorded in a log file on disk *before* returning from the corresponding function call. This log file should be readable on startup for recovery (you do *not* need to implement recovery). The log should contain enough information to reconstruct the state of the DTM, so that the simulated durability is maintained on shutdown.
*   **Performance:** Optimize for minimal latency in handling requests, especially `prepare` and `commit`.  Consider efficient data structures and algorithms for managing transaction states and service participation.  Minimize lock contention.
*   **Error Handling:**  Handle invalid transaction IDs, duplicate transaction IDs, and other potential errors gracefully.  Return appropriate error codes or exceptions (choose one and be consistent).
*   **Scalability Considerations:** Though you are implementing an in-memory solution, consider how your design choices might impact scalability if the DTM were to manage a large number of transactions and services.

**Input/Output:**

You should implement a class or set of functions that provide the API described above.  The specific input and output format is up to you, but it should be well-defined and documented.  Assume that the input is well-formed. The class must support thread-safe operations.

**Evaluation Criteria:**

*   **Correctness:**  Does the DTM correctly implement the required functionality and satisfy the constraints?
*   **Concurrency Safety:** Is the DTM thread-safe and free from race conditions?
*   **Performance:** How efficiently does the DTM handle requests, especially under load?
*   **Code Quality:** Is the code well-structured, readable, and maintainable?
*   **Durability Simulation:** Is the durability simulation implemented correctly using the log file?
*   **Scalability Considerations:** Are the design choices appropriate for a potentially large-scale distributed system?

This problem requires a solid understanding of distributed systems concepts, concurrency, and data structures.  It encourages the use of appropriate design patterns and optimization techniques. Good luck!
