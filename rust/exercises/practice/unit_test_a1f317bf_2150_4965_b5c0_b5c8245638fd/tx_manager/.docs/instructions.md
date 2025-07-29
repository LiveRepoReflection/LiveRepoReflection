Okay, here's a challenging Rust coding problem designed to be LeetCode Hard level, focusing on algorithmic efficiency and complex constraints.

### Project Name

```
distributed-transaction-manager
```

### Question Description

You are tasked with implementing a simplified, in-memory, distributed transaction manager. This transaction manager is responsible for coordinating transactions across multiple independent "resource managers".  Think of these resource managers as independent databases or services that need to operate atomically as part of a larger transaction.

Your transaction manager must support the following operations:

1.  **`begin_transaction()`:**  Initiates a new transaction and returns a unique transaction ID (TID).  Transaction IDs are integers and must be unique and monotonically increasing (e.g., 1, 2, 3,...).

2.  **`enlist_resource(tid: u64, resource_id: u64)`:** Enlists a resource manager (identified by `resource_id`) in a transaction identified by `tid`.  A resource manager can be enlisted in multiple concurrent transactions, but only once per transaction.  If the transaction `tid` does not exist, this operation should return an error.

3.  **`prepare_transaction(tid: u64)`:**  Initiates the "prepare" phase of the two-phase commit (2PC) protocol for the transaction `tid`. This signals to all enlisted resource managers that they should prepare to commit the changes associated with the transaction.  Each resource manager has a `prepare()` function that your transaction manager needs to call **concurrently** (e.g., using threads or an async runtime). The `prepare()` function returns a boolean indicating whether the resource manager is ready to commit (`true`) or wants to abort (`false`). This function returns true if all resources respond `true` (ready to commit), else returns `false`. If the transaction `tid` does not exist, this operation should return an error.

4.  **`commit_transaction(tid: u64)`:**  If `prepare_transaction()` returned `true`, this function commits the transaction `tid`. The transaction manager needs to call the `commit()` function of each enlisted resource manager **concurrently**. If any resource manager fails during the commit phase (throws an error), the transaction manager must log the failure but continue attempting to commit the remaining resources. The function will return `true` if all resources committed successfully and `false` otherwise. If the transaction `tid` does not exist, or if `prepare_transaction()` was not previously called and returned `true`, this operation should return an error.

5.  **`abort_transaction(tid: u64)`:**  Aborts the transaction `tid`. The transaction manager needs to call the `rollback()` function of each enlisted resource manager **concurrently**. Similar to commit, if any resource manager fails during rollback, log the failure and continue attempting to rollback the remaining resources. The function will return `true` if all resources rolled back successfully and `false` otherwise.  If the transaction `tid` does not exist, this operation should return an error.

6.  **`get_transaction_status(tid: u64) -> TransactionStatus`:** Returns the current status of the transaction. Possible statuses are `Active`, `Prepared`, `Committed`, `Aborted`, and `NotFound`.

**Resource Manager Interface:**

You will be provided with a trait (interface) that defines the resource manager:

```rust
trait ResourceManager {
    fn prepare(&self) -> bool;
    fn commit(&self) -> Result<(), String>;
    fn rollback(&self) -> Result<(), String>;
    fn get_resource_id(&self) -> u64;
}
```

**Constraints and Edge Cases:**

*   **Concurrency:**  The transaction manager must handle multiple concurrent transactions and concurrent calls to `prepare()`, `commit()`, and `rollback()`.  Use appropriate synchronization primitives (e.g., mutexes, read-write locks, channels, atomics) to ensure data consistency and prevent race conditions.
*   **Error Handling:**  Properly handle errors, especially during `commit()` and `rollback()`. Log failures without halting the entire process.
*   **Idempotency:** The `commit` and `rollback` operations should ideally be idempotent. Although you don't need to *guarantee* idempotency in your code, your design should consider the implications if these operations are called multiple times.
*   **Deadlock Prevention:**  Be mindful of potential deadlocks when multiple transactions are accessing the same resource managers.
*   **Resource Manager Failures:** Simulate resource manager failures in your unit tests (e.g., by making `prepare()`, `commit()`, or `rollback()` sometimes return an error or panic). Your transaction manager should be resilient to these failures.
*   **Efficiency:**  Minimize latency. Concurrent operations should truly run in parallel. Avoid unnecessary locking or blocking.
*   **Transaction Timeout:** Consider how you might implement transaction timeouts in a real system.  You don't need to implement actual timeouts, but your design should be extensible to support them.
*   **Large Number of Resources:** Your transaction manager should scale reasonably well to transactions involving a large number of resource managers.
*   **Correctness:** Ensure atomicity. Either all enlisted resource managers commit, or all roll back.

**Transaction Status Enum:**

```rust
enum TransactionStatus {
    Active,
    Prepared,
    Committed,
    Aborted,
    NotFound,
}
```

This problem requires a solid understanding of concurrency, error handling, and distributed systems concepts. The solution should be well-structured, efficient, and resilient to failures.  Good luck!
