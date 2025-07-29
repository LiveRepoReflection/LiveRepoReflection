## Question Title: Distributed Transactional Key-Value Store with Conflict Resolution

### Question Description

You are tasked with designing and implementing a simplified, in-memory, distributed key-value store that supports ACID (Atomicity, Consistency, Isolation, Durability) properties, with a focus on handling concurrent transactions and resolving conflicts.

The key-value store consists of `N` nodes (where `N` is a configurable parameter).  Each node holds a complete copy of the data (full replication). The system must support the following operations:

*   **`begin_transaction()`**:  Initiates a new transaction and returns a unique transaction ID (TXID). TXIDs are integers.
*   **`get(TXID, key)`**:  Retrieves the value associated with a given key within the context of a specific transaction. If the key doesn't exist, return `None`. Reads within a transaction should always return the same value, even if other transactions modify the key concurrently.
*   **`put(TXID, key, value)`**:  Updates the value associated with a key within the context of a specific transaction.  Updates are staged locally to the node until the transaction is committed.  The value can be any string.
*   **`commit_transaction(TXID)`**:  Attempts to commit the transaction with the given TXID.  If the transaction can be successfully committed without violating isolation (no conflicts with other concurrent transactions), the changes are applied to the in-memory store and the function returns `True`.  If a conflict is detected, the transaction is rolled back (changes discarded), and the function returns `False`.
*   **`abort_transaction(TXID)`**:  Aborts (rolls back) the transaction with the given TXID, discarding any staged changes.
*   **`recover()`**: Recovers the state of the key-value store. The state includes the committed data and the transaction IDs, and is stored in the `state.json` file. This simulates restarting a node.

**Conflict Detection:**

A conflict occurs if two concurrent transactions modify the same key.  Your system should use optimistic concurrency control with a timestamp-based conflict resolution strategy.  Each key stores its last modification timestamp (a simple integer counter incremented on each successful commit). Transactions are assigned a start timestamp when they begin.  A transaction can only commit if, for all keys it has modified, the key's current modification timestamp is the same as the transaction's start timestamp when it first read or wrote to the key.

**Concurrency:**

The system must handle multiple concurrent transactions. Use appropriate locking mechanisms to ensure data consistency and isolation.  Minimize lock contention to maximize throughput.

**Persistence:**

The system should persist the committed data and the current maximum transaction ID (to avoid ID collisions after restarts) to a file named `state.json` after each successful commit. The `recover()` method should load this data on startup. The format of `state.json` is up to you.

**Constraints:**

*   The system should be implemented in Python.
*   The solution should be thread-safe.
*   The system should be designed to handle a large number of concurrent transactions.
*   Assume that network communication between nodes is reliable (no packet loss).  You don't need to implement actual networking; focus on the data structures and algorithms for transaction management and conflict resolution.
*   The solution should be optimized for read-heavy workloads.
*   The system should be able to recover from crashes.

**Edge Cases:**

*   Multiple `put` operations on the same key within the same transaction.
*   `get` operations on non-existent keys.
*   Concurrent transactions modifying different keys.
*   `commit_transaction` or `abort_transaction` called on a non-existent TXID.
*   `commit_transaction` called multiple times on the same TXID.
*   Empty values for keys.
*   Recover from a crash when there are ongoing transactions.

**Optimization Requirements:**

*   Minimize the time taken to commit transactions, especially in scenarios with low contention.
*   Optimize `get` operations for read-heavy workloads.

**Bonus (Optional):**

*   Implement a mechanism to prevent long-running transactions from starving other transactions.
*   Add a configurable timeout for transactions.  Transactions that exceed the timeout are automatically aborted.
