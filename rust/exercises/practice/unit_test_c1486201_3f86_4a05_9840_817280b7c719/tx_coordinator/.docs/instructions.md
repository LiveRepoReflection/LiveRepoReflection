Okay, here's a challenging Rust coding problem.

**Problem Title:** Distributed Transaction Coordinator

**Problem Description:**

You are tasked with implementing a simplified, distributed transaction coordinator.  Imagine a system where multiple independent services (nodes) need to perform operations that must either all succeed or all fail.  Your coordinator will manage the "commit" or "rollback" of these distributed transactions.

Each transaction involves a set of nodes. Each node can either "prepare" to commit a transaction, "commit" the transaction, or "rollback" the transaction. The coordinator orchestrates these operations, ensuring atomicity (all nodes commit or all rollback).

**Specific Requirements:**

1.  **Transaction IDs:** Each transaction is identified by a unique 64-bit unsigned integer (`u64`).

2.  **Nodes:** Each node is identified by a unique string (`String`).

3.  **Coordinator Interface:** Implement a `Coordinator` struct with the following methods:

    *   `new()`: Creates a new, empty coordinator.
    *   `begin_transaction(transaction_id: u64, participating_nodes: Vec<String>)`: Starts a new transaction. The coordinator records the participating nodes. Returns `Ok(())` if successful, or `Err("Transaction already exists")` if the transaction ID is already in use.
    *   `prepare(transaction_id: u64, node_id: &str)`:  A node signals its readiness to commit. Returns `Ok(())` if successful (the node was part of the transaction and hadn't already prepared).  Returns `Err("Transaction not found")` if the transaction ID doesn't exist. Returns `Err("Node not in transaction")` if the node is not part of the specified transaction. Returns `Err("Node already prepared")` if the node has already prepared for this transaction.
    *   `commit_transaction(transaction_id: u64)`:  Instructs all prepared nodes in a transaction to commit. This function should only be called if all participating nodes have prepared. Returns `Ok(())` if successful (all nodes prepared and the commit was initiated). Returns `Err("Transaction not found")` if the transaction ID doesn't exist. Returns `Err("Not all nodes prepared")` if not all participating nodes have prepared.
    *   `rollback_transaction(transaction_id: u64)`: Instructs all participating nodes in a transaction to rollback (regardless of their preparation status). Returns `Ok(())` if successful. Returns `Err("Transaction not found")` if the transaction ID doesn't exist.
    *   `get_transaction_status(transaction_id: u64) -> Result<TransactionStatus, String>`: Returns the current status of the transaction.  Possible `TransactionStatus` values are: `Pending`, `Prepared`, `Committed`, `RolledBack`, `NotFound`.  `Prepared` means all nodes have prepared, but the commit hasn't been initiated yet.
        ```rust
        #[derive(Debug, PartialEq, Eq)]
        enum TransactionStatus {
            Pending,
            Prepared,
            Committed,
            RolledBack,
            NotFound,
        }
        ```

4.  **Concurrency:** The coordinator must be thread-safe.  Multiple threads should be able to concurrently call `prepare`, `commit_transaction`, and `rollback_transaction`.

5.  **Error Handling:**  Return meaningful error messages as described above.  Consider using a custom `enum` for error types if you desire more structured error handling.

6.  **Optimization:**  The coordinator should be reasonably efficient. Consider the time complexity of your operations, especially when dealing with a large number of transactions and nodes.  Minimize locking contention.

7.  **Edge Cases:**
    *   Handling duplicate `prepare` calls from the same node.
    *   Calling `commit_transaction` or `rollback_transaction` multiple times for the same transaction.
    *   Transactions with zero participating nodes.

**Constraints:**

*   You cannot use external crates outside of the standard library (unless specifically approved - and for this exercise, assume no external crates).
*   The number of nodes participating in a transaction can be very large (up to 10,000).
*   The number of concurrent transactions can be very large (up to 100,000).
*   The `prepare`, `commit_transaction`, and `rollback_transaction` methods should ideally have O(1) or O(log n) average time complexity with respect to the number of transactions.
*   The `begin_transaction` method should have O(1) average time complexity.

This problem requires careful consideration of data structures, concurrency primitives (e.g., `Mutex`, `RwLock`, `Arc`), and algorithm design to achieve the desired performance and correctness under concurrent access. Good luck!
