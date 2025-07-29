## Problem: Distributed Transactional Key-Value Store

### Question Description

You are tasked with designing and implementing a simplified, in-memory, distributed transactional key-value store. This store will be used in a highly concurrent environment where data consistency and atomicity are paramount. Your implementation must support the following operations:

1.  **`begin_transaction(client_id)`:** Starts a new transaction for a given client. Each client can only have one active transaction at a time. Returns a unique transaction ID (`tx_id`).

2.  **`put(tx_id, key, value)`:**  Within the transaction identified by `tx_id`, associates the `key` with the `value`. The `value` is only visible after the transaction is committed.

3.  **`get(tx_id, key)`:** Within the transaction identified by `tx_id`, retrieves the value associated with the `key`. If the `key` is not found in the current transaction's pending changes, it should retrieve the most recently committed value. If the key is not found in the committed values either, return `None`.

4.  **`commit_transaction(tx_id)`:**  Atomically commits the transaction identified by `tx_id`, making all its changes visible to subsequent operations.

5.  **`rollback_transaction(tx_id)`:**  Rolls back (aborts) the transaction identified by `tx_id`, discarding all its changes.

**Constraints:**

*   **Atomicity:** All changes within a transaction must be applied as a single, indivisible unit. Either all changes are committed, or none are.

*   **Consistency:** The system must maintain a consistent state at all times.  No partial transaction results should be visible outside of the transaction itself.

*   **Isolation:** Concurrent transactions must not interfere with each other.  A transaction should see a consistent snapshot of the data, unaffected by concurrent modifications from other transactions.

*   **Durability:** While this is an in-memory store and persistence is not strictly required, you should design the system to minimize the risk of data loss in case of unexpected failures (e.g., leveraging snapshots).

*   **Concurrency:** The system must handle multiple concurrent transactions efficiently. Aim for minimal locking and contention.

*   **Optimizations:**  Prioritize read performance.  `get` operations should be as fast as possible.

*   **Key/Value Types:** Both keys and values are strings.

*   **Error Handling:** Implement basic error handling. For example, return appropriate error codes or raise exceptions when a transaction is already active for a client, or when trying to operate on a non-existent transaction.

*   **Scalability Considerations:** While you don't need to implement actual distribution, describe how your design could be extended to handle a distributed environment (e.g., sharding, replication, consensus). Discuss the challenges and trade-offs involved.

*   **Memory Usage:** Be mindful of memory usage, especially when dealing with large datasets and numerous concurrent transactions. Consider techniques for minimizing memory footprint.

**Example Usage:**

```python
store = KeyValueStore()

tx1_id = store.begin_transaction("client1")
tx2_id = store.begin_transaction("client2")

store.put(tx1_id, "x", "1")
store.put(tx2_id, "x", "2")

print(store.get(tx1_id, "x"))  # Output: 1
print(store.get(tx2_id, "x"))  # Output: 2

store.commit_transaction(tx1_id)

print(store.get(tx2_id, "x"))  # Output: 2

store.commit_transaction(tx2_id)

print(store.get(tx2_id, "x")) #Output: 2

tx3_id = store.begin_transaction("client3")
print(store.get(tx3_id, "x")) # Output: 2

store.rollback_transaction(tx3_id)
```

**Bonus Challenges:**

*   Implement a garbage collection mechanism to reclaim memory from completed transactions.
*   Add support for more complex data types beyond strings (e.g., lists, dictionaries).
*   Implement a basic conflict detection mechanism to prevent concurrent updates to the same key within different transactions.
