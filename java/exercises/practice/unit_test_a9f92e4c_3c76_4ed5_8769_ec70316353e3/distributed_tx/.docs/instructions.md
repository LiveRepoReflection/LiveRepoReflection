## Problem: Distributed Transaction Coordinator

**Description:**

You are building a distributed database system that guarantees ACID properties for transactions spanning multiple nodes. Your task is to implement a simplified version of a transaction coordinator that handles the "prepare," "commit," and "rollback" phases of a two-phase commit (2PC) protocol.

**System Model:**

*   You have `N` nodes in your distributed system, identified by unique integer IDs from `0` to `N-1`.
*   Each transaction involves a subset of these `N` nodes.
*   The transaction coordinator (TC) is a central service (you are implementing this) responsible for managing the transaction's lifecycle.
*   Each node can either vote to "commit" or "abort" a transaction.
*   Nodes are unreliable and may fail at any point in the process.
*   The network is also unreliable and messages can be lost, delayed, or duplicated.

**Requirements:**

Implement a `TransactionCoordinator` class with the following methods:

1.  `startTransaction(transactionId: UUID, involvedNodes: Set<Integer>): void` - Initiates a new transaction. `transactionId` is a unique identifier for the transaction (use UUID). `involvedNodes` is the set of node IDs participating in the transaction.

2.  `receiveVote(transactionId: UUID, nodeId: Integer, vote: boolean): void` - Called by a node to cast its vote. `vote` is `true` for "commit," `false` for "abort."

3.  `handleNodeFailure(nodeId: Integer): void` - Called when a node fails.  The TC must react appropriately if the node was involved in any ongoing transaction.

4.  `getTransactionState(transactionId: UUID): TransactionState` - Returns the current state of the transaction.

**TransactionState Enum:**

```java
enum TransactionState {
    INITIATED,  // Transaction started, waiting for votes
    PREPARED,   // All nodes voted to commit
    COMMITTED,  // Transaction committed
    ABORTED     // Transaction aborted (due to node failure or negative vote)
}
```

**Constraints:**

*   **Atomicity:** If any node votes to abort, the entire transaction must be aborted. If a node fails before voting, the transaction must be aborted.  If all nodes vote to commit and no nodes fail, the transaction must be committed.
*   **Durability:** Once a transaction is committed or aborted, the decision must be persistent, even if the TC restarts. You **do not** need to implement actual persistence to disk, but your design should consider how the TC would recover its state after a crash. Consider the data structures you will use to keep track of the state of a transaction.
*   **Idempotency:**  `receiveVote` and `handleNodeFailure` might be called multiple times for the same transaction and node. Your implementation must handle duplicate calls gracefully.
*   **Timeout:** Implement a timeout mechanism. If the TC does not receive votes from all involved nodes within a specified timeout (e.g., 10 seconds), the transaction should be automatically aborted.
*   **Efficiency:**  Your solution should be reasonably efficient in terms of memory usage and processing time. Consider the time complexity of each method.
*   **Concurrency:**  Assume multiple transactions can be running concurrently. Ensure your implementation is thread-safe.
*   **Scalability:** While you don't need to implement distributed coordination of multiple TCs, consider how your design could be extended to handle a large number of concurrent transactions and nodes. What are the potential bottlenecks?

**Assumptions:**

*   You can assume that `transactionId` is always unique.
*   You do not need to handle network partitions or Byzantine failures.
*   You do not need to implement actual data operations on the nodes; you only need to manage the 2PC protocol.

**Complexity Considerations:**

*   This problem requires a good understanding of distributed systems principles, concurrency, and data structures.
*   The timeout and node failure handling introduce significant complexity.
*   Designing a thread-safe and scalable solution requires careful consideration of synchronization and data structures.
*   The durability requirement forces you to think about how to persist the transaction state.
*   The idempotency requirement adds another layer of complexity to the vote and failure handling.
