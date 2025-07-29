## Question: Distributed Transaction Coordinator

**Description:**

You are tasked with implementing a simplified, distributed transaction coordinator (similar in principle to a two-phase commit protocol) for a banking system. The system consists of multiple independent bank servers (nodes), each managing a subset of user accounts and their balances. A transaction may involve transferring funds between accounts located on different bank servers.

Your goal is to implement a central coordinator service that ensures atomicity and consistency across these distributed transactions. The coordinator must orchestrate the transaction execution and guarantee that either all participating bank servers commit the changes or all of them rollback, even in the face of network failures or server crashes.

**Specifics:**

1.  **Bank Server Interface:** Assume the existence of a `BankServer` interface (you don't need to implement this).  Each `BankServer` exposes the following methods:

    *   `boolean prepare(Transaction transaction)`:  Called by the coordinator. The server validates that it can perform the transaction (e.g., sufficient funds, accounts exist). If it can, it locks the necessary resources (e.g., account balances) and returns `true`. If not, it returns `false`.  This is an *idempotent* operation.
    *   `void commit(Transaction transaction)`: Called by the coordinator. The server applies the changes specified in the transaction and releases the locks. This is an *idempotent* operation.
    *   `void rollback(Transaction transaction)`: Called by the coordinator. The server undoes any changes made during the `prepare` phase and releases the locks. This is an *idempotent* operation.

2.  **Transaction Class:** Assume the existence of a `Transaction` class (you don't need to implement this). A `Transaction` object contains the following information:

    *   `String transactionId()`: A unique identifier for the transaction.
    *   `List<Operation> operations()`: A list of operations to be performed. Each `Operation` specifies the account, the amount to transfer, and whether it's a debit or credit.
    *   `Set<BankServer> participatingServers()`: Returns a set of `BankServer` instances involved in this transaction.

3.  **Coordinator Implementation:** You must implement a `TransactionCoordinator` class with the following methods:

    *   `boolean executeTransaction(Transaction transaction, int timeoutMillis)`: This is the main method. It takes a `Transaction` object and a timeout value (in milliseconds) as input. The method should:

        *   **Phase 1 (Prepare):** Send a `prepare` request to all participating `BankServer`s concurrently.
        *   **Phase 2 (Commit/Rollback):**
            *   If all `prepare` requests succeed (return `true`) within the given `timeoutMillis`, send a `commit` request to all participating `BankServer`s concurrently.
            *   If any `prepare` request fails (returns `false`) or times out, send a `rollback` request to all participating `BankServer`s concurrently.

        *   The method should return `true` if the transaction was successfully committed (all `prepare` and `commit` calls succeeded within the timeout) and `false` otherwise (if any `prepare` failed or timed out, or the rollback failed).  If any `commit` call fails, the system is in an inconsistent state, so rollback should be attempted, and the method should return `false`.

4.  **Constraints and Considerations:**

    *   **Concurrency:** The `prepare`, `commit`, and `rollback` calls to the `BankServer`s must be performed concurrently using a thread pool.
    *   **Timeouts:**  Implement timeouts for all network operations (e.g., `prepare`, `commit`, `rollback` calls). If a server doesn't respond within the given `timeoutMillis`, consider it a failure.
    *   **Idempotency:**  The `prepare`, `commit`, and `rollback` operations on the `BankServer`s are idempotent.  This means that if a server receives the same request multiple times, it should only execute it once. Your coordinator should not exploit this directly but be aware of it.
    *   **Error Handling:** Handle exceptions gracefully (e.g., network errors, server crashes). Log errors appropriately.
    *   **Resource Management:** Properly manage threads and resources to avoid leaks.
    *   **Deadlock Avoidance:** Ensure your coordinator doesn't introduce deadlocks.
    *   **Optimization:** The solution should be efficient in terms of execution time and resource usage. Consider the number of threads used and the overhead of context switching.
    *   **Scalability:** Although not explicitly tested, consider how your design could scale to a large number of bank servers and transactions.

5.  **Testing:** You will be provided with a testing environment that simulates network failures, server crashes, and slow responses. Your solution must pass these tests to be considered correct.

**This problem tests your ability to:**

*   Implement a distributed algorithm with concurrency.
*   Handle timeouts and failures gracefully.
*   Design a robust and scalable system.
*   Understand the principles of two-phase commit.

Good luck!
