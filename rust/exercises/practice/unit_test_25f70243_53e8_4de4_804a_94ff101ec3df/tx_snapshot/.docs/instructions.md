Okay, here's a highly challenging Rust coding problem designed to test advanced skills and optimization techniques:

**Problem Title:** Concurrent Transaction Processing with Snapshot Isolation

**Problem Description:**

You are tasked with building a simplified, in-memory database system that supports concurrent transaction processing with snapshot isolation. This means multiple transactions can read and write data concurrently, but each transaction operates on a consistent snapshot of the database at the time it started.

**Data Model:**

The database consists of a collection of key-value pairs, where both keys and values are strings.

**Requirements:**

1.  **Transaction Management:** Implement a `Transaction` struct/class with the following methods:
    *   `begin()`: Starts a new transaction. Returns a unique transaction ID (u64).
    *   `read(transaction_id: u64, key: String) -> Option<String>`: Reads the value associated with a given key within the context of the transaction with the given ID. If the key doesn't exist, return `None`. The read *must* be from the snapshot of the database as it existed when the transaction started.
    *   `write(transaction_id: u64, key: String, value: String)`: Writes a new value for the specified key within the context of the transaction with the given ID.  These writes are *not* immediately visible to other transactions.
    *   `commit(transaction_id: u64) -> Result<(), String>`: Commits the transaction with the given ID. All writes performed by this transaction become visible to subsequent transactions (those starting *after* the commit).  If another transaction has already written to the same key that this transaction modified *after* this transaction began, the commit should fail and return an error message indicating a write conflict (serialization error).
    *   `rollback(transaction_id: u64)`: Rolls back the transaction with the given ID, discarding all its changes.

2.  **Concurrency:**  The `read`, `write`, `commit`, and `rollback` methods *must* be thread-safe. Multiple threads should be able to call these methods concurrently without causing data corruption or race conditions.

3.  **Snapshot Isolation:** Each transaction must operate on a consistent snapshot of the database at the time it began. Reads within a transaction must always return the same value for a given key, even if other transactions commit changes in the meantime.

4.  **Write Conflicts:**  Implement conflict detection.  If two concurrent transactions attempt to modify the same key, the transaction that commits *last* should fail with a write conflict error.

5.  **Performance:**
    *   Minimize the overhead of creating snapshots.  Copy-on-write techniques or similar approaches are highly recommended.
    *   Minimize contention between threads.  Fine-grained locking or lock-free data structures might be necessary.

6.  **Edge Cases and Constraints:**
    *   Handle the case where a transaction attempts to read or write to a key that doesn't exist.
    *   Handle the case where a transaction ID is invalid (e.g., the transaction has already been committed or rolled back, or the ID never existed).
    *   The number of concurrent transactions and the size of the database (number of key-value pairs) can be large. Consider memory usage and scalability.
    *   Ensure that committed data is durable (i.e., not lost due to program crashes). (Optional, but adds significant complexity.  Could be simulated with a simple file-based log).

**Example Usage (Conceptual):**

```rust
let mut db = Database::new();

// Transaction 1
let tx1_id = db.begin();
db.write(tx1_id, "x".to_string(), "10".to_string());
assert_eq!(db.read(tx1_id, "x".to_string()), Some("10".to_string()));

// Transaction 2
let tx2_id = db.begin();
assert_eq!(db.read(tx2_id, "x".to_string()), None); // tx2 sees initial state.

db.write(tx2_id, "x".to_string(), "20".to_string());
assert_eq!(db.read(tx2_id, "x".to_string()), Some("20".to_string()));

// Commit Transaction 1
db.commit(tx1_id).unwrap();

// Transaction 3 starts *after* tx1 commits
let tx3_id = db.begin();
assert_eq!(db.read(tx3_id, "x".to_string()), Some("10".to_string())); // tx3 sees tx1's commit

// Commit Transaction 2 - FAILS because tx1 already wrote to "x" and committed after tx2 began.
assert!(db.commit(tx2_id).is_err());

//Commit Transaction 3 - Success because no write conflict happened after tx3 began.
assert!(db.commit(tx3_id).is_ok());
```

**Evaluation Criteria:**

*   Correctness: Does the solution correctly implement transaction management, snapshot isolation, and write conflict detection?
*   Concurrency: Is the solution thread-safe and does it handle concurrent transactions correctly?
*   Performance: Is the solution efficient in terms of memory usage, CPU usage, and contention between threads?
*   Code Quality: Is the code well-structured, readable, and maintainable?
*   Error Handling: Does the solution handle edge cases and invalid inputs gracefully?

This problem requires a deep understanding of concurrency, data structures, and database concepts. It's a significant challenge that demands careful design and implementation. Good luck!
