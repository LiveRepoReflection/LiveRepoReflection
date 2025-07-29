Okay, here's a challenging Rust coding problem designed to test a variety of skills, without providing any code.

**Problem Title:**  Concurrent Transactional Key-Value Store with Snapshot Isolation

**Problem Description:**

You are tasked with implementing a concurrent, in-memory key-value store that supports transactional operations with snapshot isolation.  The store must allow multiple clients to read and write data concurrently, while maintaining data consistency and preventing common concurrency issues like dirty reads, non-repeatable reads, and phantom reads.

The key-value store should provide the following functionality:

1.  **`begin_transaction() -> TransactionId`:**  Starts a new transaction and returns a unique `TransactionId`.  Transaction IDs are monotonically increasing.
2.  **`read(transaction_id: TransactionId, key: String) -> Option<String>`:** Reads the value associated with the given `key` within the context of the specified `transaction_id`.  The read must reflect the state of the key-value store at the time the transaction started (snapshot isolation). If the key does not exist, return `None`.
3.  **`write(transaction_id: TransactionId, key: String, value: String)`:** Writes the given `value` to the specified `key` within the context of the specified `transaction_id`.  Writes are local to the transaction until it is committed.  Multiple writes to the same key within a single transaction should result in the last write taking precedence.
4.  **`commit_transaction(transaction_id: TransactionId) -> Result<(), TransactionError>`:**  Attempts to commit the transaction associated with the given `transaction_id`.
    *   If no conflicting writes have occurred since the transaction started, the changes are applied to the main key-value store, and the function returns `Ok(())`.
    *   If conflicting writes have occurred (another transaction has committed changes to the same keys that this transaction has modified), the commit fails, and the function returns `Err(TransactionError::Conflict)`.  The transaction's changes are discarded.
    *   If the transaction id is not found, the function returns `Err(TransactionError::NotFound)`.
5.  **`abort_transaction(transaction_id: TransactionId)`:** Discards all changes made within the transaction associated with the given `transaction_id`. No error needs to be reported if the transaction is not found.
6.  **`garbage_collect(min_transaction_id: TransactionId)`:**  Garbage collects older snapshots to reclaim memory. Snapshots older than or equal to `min_transaction_id` can be safely discarded. This function should be efficient and not block the main operations for extended periods.

**Constraints and Considerations:**

*   **Concurrency:**  The key-value store must be thread-safe and handle concurrent read, write, commit, and abort operations from multiple clients.  Use appropriate synchronization primitives (e.g., Mutexes, RwLocks, Atomic types) to ensure data consistency.
*   **Snapshot Isolation:**  Each transaction must operate on a consistent snapshot of the data, taken at the time the transaction started.  Reads within a transaction must always return the same value for a given key, regardless of concurrent writes by other transactions.
*   **Conflict Detection:**  The system must accurately detect conflicting writes during commit operations. A conflict occurs when two transactions modify the same key, and at least one of the transactions commits first.
*   **Memory Management:**  The system must efficiently manage memory usage.  Avoid unnecessary copying of data and implement a garbage collection mechanism to reclaim memory from completed transactions.  The garbage collection must be non-blocking and efficient.
*   **Performance:**  Optimize for read performance, as read operations are expected to be more frequent than write operations.  Minimize lock contention and use appropriate data structures to support efficient lookups.
*   **Error Handling:**  Implement robust error handling and provide informative error messages when commit operations fail.
*   **Atomicity:** All operations within a transaction are atomic. Either all changes are applied to the main key-value store, or none are.
*   **Durability:** Data is stored in-memory only, so durability is not required.

**TransactionError Enum:**

```rust
enum TransactionError {
    Conflict,
    NotFound,
}
```

**Assumptions:**

*   Keys and values are strings.
*   The number of concurrent transactions is bounded.
*   The total number of keys is large.
*   Transactions are short-lived.

This problem requires a good understanding of concurrency, data structures, and transactional concepts. Good luck!
