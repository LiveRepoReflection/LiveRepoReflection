Okay, here is a challenging Rust programming competition problem, designed to be difficult and requiring careful consideration of data structures, algorithms, and optimization.

### Project Name

```
distributed-transaction-manager
```

### Question Description

You are tasked with implementing a simplified, distributed transaction manager (DTM) for a key-value store. The key-value store is distributed across `N` nodes, where `N` is a configuration parameter.  Each node holds a subset of the keys. Your DTM must ensure ACID (Atomicity, Consistency, Isolation, Durability) properties across these nodes.  The DTM will use a two-phase commit (2PC) protocol.

**Simplified Key-Value Store:**

*   The key-value store supports only `GET` and `PUT` operations.
*   Each node has a unique ID from 0 to N-1.
*   Key distribution is determined by a simple hash function: `node_id = hash(key) % N`, where `hash(key)` is a provided hash function (you don't need to implement the hash function itself).
*   Nodes do not crash.

**Your Task:**

Implement a `TransactionManager` struct with the following methods:

1.  `begin_transaction()`:  Starts a new transaction and returns a unique transaction ID (TID). The TID should be monotonically increasing.
2.  `put(tid: u64, key: String, value: String)`:  Stages a `PUT` operation within the transaction identified by `tid`. The operation is NOT immediately applied to the key-value store. This method needs to determine which node should handle the key and store the intended update.
3.  `get(key: String)`: Retrieves the value associated with the given key. This method must bypass the DTM and directly read from the key-value store on the appropriate node. All reads are considered to be performed outside of any transactions.
4.  `commit_transaction(tid: u64)`: Attempts to commit the transaction identified by `tid`. This involves the 2PC protocol.
5.  `abort_transaction(tid: u64)`: Aborts the transaction identified by `tid`.  This requires discarding all staged changes associated with the TID.

**Two-Phase Commit (2PC) Protocol:**

1.  **Phase 1 (Prepare):**  The transaction manager sends a "prepare" message to all nodes involved in the transaction (i.e., nodes that have staged `PUT` operations for that transaction). Each node checks if it can commit the changes (e.g., sufficient resources, no conflicts). If a node can commit, it logs the changes to durable storage (simulated in memory for this problem) and sends a "vote-commit" message back to the transaction manager. If a node cannot commit, it sends a "vote-abort" message.
2.  **Phase 2 (Commit/Abort):** If the transaction manager receives "vote-commit" from all involved nodes, it sends a "commit" message to all involved nodes.  Each node then applies the changes to its key-value store. If the transaction manager receives at least one "vote-abort" message, it sends an "abort" message to all involved nodes. Each node then discards the logged changes.

**Constraints and Requirements:**

*   **Atomicity:**  All changes within a transaction must be applied, or none at all.
*   **Consistency:**  Transactions must leave the system in a valid state.  (This is largely handled by the key-value store itself, but your DTM must not violate it).
*   **Isolation:**  Reads should not be affected by ongoing transactions. (Since reads bypass the DTM, this is implicitly satisfied).
*   **Durability:**  Once a transaction is committed, the changes must be permanent (simulated via logging before the commit).
*   **Concurrency:**  Multiple transactions may be active concurrently. You must ensure proper synchronization to prevent race conditions.
*   **Scalability:**  Your solution should be reasonably efficient.  Avoid unnecessary locking or copying of data. The number of nodes, N, can be up to 100, and the number of concurrent transactions can be up to 1000.
*   **Error Handling:**  Handle potential errors gracefully.  For example, if a transaction ID is invalid, return an appropriate error.
*   **Simulated Key-Value Store:** You do not need to implement the actual key-value store on each node. Instead, you will receive a trait `KeyValueStore` that will simulate the get/put operations on a particular node.

**Provided Trait:**

```rust
pub trait KeyValueStore {
    fn get(&self, key: &str) -> Option<String>;
    fn put(&mut self, key: &str, value: String);
}
```

**Important Notes:**

*   You are responsible for designing the data structures to store staged changes, transaction states, and node communication.
*   You can assume that the `hash(key)` function is provided and has constant time complexity.
*   Focus on correctness, concurrency, and efficiency.
*   You need to implement synchronization mechanisms (e.g., Mutexes, RwLocks) to handle concurrent transactions safely. Consider which type of lock is most suitable to use for each synchronization point.
*   The actual implementation of the durable log (used during the prepare phase) can be simulated in memory.
* The actual implementation of the node id is provided.

This problem requires a solid understanding of distributed systems concepts, concurrency, data structures, and algorithms. Good luck!
