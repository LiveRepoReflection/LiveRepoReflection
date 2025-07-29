## Project Name

`Distributed Transaction Coordinator`

## Question Description

You are tasked with designing and implementing a distributed transaction coordinator for a simplified banking system. This system involves multiple independent bank services (simulated as Python classes), each responsible for managing accounts on a single shard. Transactions often require transferring funds between accounts residing on different shards. Your coordinator must ensure ACID (Atomicity, Consistency, Isolation, Durability) properties across these distributed transactions.

Specifically, you need to implement the following:

1.  **`BankService` Class:** Represents a single bank shard. It should have methods for:
    *   `deposit(account_id, amount)`: Deposits `amount` into `account_id`.
    *   `withdraw(account_id, amount)`: Withdraws `amount` from `account_id`. Raises an exception if insufficient balance.
    *   `get_balance(account_id)`: Returns the current balance of `account_id`.
    *   `prepare(transaction_id, operations)`: Attempts to reserve the resources (funds) necessary for the transaction's operations on this shard. `operations` is a list of tuples `(account_id, amount, type)`, where type can be 'deposit' or 'withdraw'. Should return `True` if prepared successfully, `False` otherwise (e.g., due to insufficient funds).
    *   `commit(transaction_id)`: Permanently applies the prepared changes for a given `transaction_id`.
    *   `rollback(transaction_id)`: Reverts any prepared changes for a given `transaction_id`.
    *   Internally the `BankService` should maintain a log of prepared operations indexed by `transaction_id`.

2.  **`TransactionCoordinator` Class:** This class orchestrates the distributed transactions. It should have methods for:
    *   `begin_transaction()`: Generates a unique `transaction_id` and starts a new transaction.
    *   `transfer(from_account, to_account, amount)`: Adds a transfer operation to the current transaction. It needs to determine which bank services are involved based on the account IDs.
    *   `end_transaction()`: Attempts to commit the current transaction. This involves:
        *   **Prepare Phase:** Sends `prepare` requests to all involved bank services. If *all* services respond with `True`, the transaction proceeds. If *any* service responds with `False` (or times out), the transaction is aborted.
        *   **Commit Phase (if all prepared successfully):** Sends `commit` requests to all involved bank services.
        *   **Rollback Phase (if any prepare failed):** Sends `rollback` requests to all involved bank services.
    *   `get_transaction_status(transaction_id)`: Returns the status of the transaction (e.g., "pending", "committed", "aborted").

**Constraints and Edge Cases:**

*   **Atomicity:** All operations within a transaction must either succeed or fail together.
*   **Isolation:** Transactions must be isolated from each other. Concurrent transactions should not interfere with each other's state. You can assume a single coordinator instance, but multiple concurrent calls to transfer and end_transaction.
*   **Durability:** Once a transaction is committed, the changes must be permanent, even in the face of service failures (assume services don't fail during commit or rollback, but might have prepared successfully and then crash before commit/rollback. Your implementation needs to handle this scenario).
*   **Concurrency:**  Implement thread safety measures where necessary, using locks or other synchronization primitives, to handle concurrent `transfer` and `end_transaction` calls.
*   **Deadlock avoidance:** Avoid deadlocks when acquiring locks on multiple bank services.
*   **Account Distribution:** You are given a function `get_bank_service(account_id)` that returns the `BankService` instance responsible for a given `account_id`. Assume this function is readily available.
*   **Timeouts:** Implement timeouts for `prepare` requests. If a bank service doesn't respond within a reasonable time (e.g., 1 second), the transaction should be aborted.
*   **Idempotency:** Ensure that `commit` and `rollback` operations are idempotent.  A service might receive the same `commit` or `rollback` request multiple times due to network issues.
*   **Error Handling:** Handle potential exceptions gracefully and ensure that they don't compromise the ACID properties.
*   **Optimization:** Minimize the time it takes to complete a transaction, considering network latency. The prepare phase can run in parallel.

**Bonus Challenges:**

*   Implement a simple recovery mechanism. If a `BankService` crashes after preparing but before committing/rolling back, it should be able to determine the outcome of the transaction upon restart (e.g., by consulting a persistent log).
*   Implement a two-phase commit protocol with a separate "Voting" phase to make the overall system more robust.

This problem requires careful consideration of concurrency, error handling, and distributed system principles. Aim for a clean, well-structured, and efficient solution.
