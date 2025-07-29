Okay, here's a problem designed to be challenging and require efficient algorithms and data structures.

**Problem: Distributed Transaction Commit with Conflict Resolution**

**Description:**

You are designing a distributed database system. A critical component is the transaction commit protocol.  Due to network partitions and unpredictable failures, transactions across multiple nodes might enter conflicting states. Your task is to implement a robust and efficient mechanism for resolving these conflicts and ensuring eventual consistency.

Each transaction involves multiple operations across different nodes in the system.  Each node maintains a local log of the operations it performed as part of a transaction. A transaction can be in one of three states on each node: `PREPARED`, `COMMITTED`, or `ABORTED`.

Due to network failures, nodes might not always agree on the final outcome of a transaction.  Some nodes might have prepared a transaction while others have already committed or aborted it.  Your system must handle these inconsistencies and converge to a consistent state.

You are given a list of transactions.  Each transaction is represented by a list of operations performed on different nodes. Each operation includes the node ID, transaction ID, and the final state of the transaction on that node (`PREPARED`, `COMMITTED`, or `ABORTED`).

**Your Task:**

Implement a function `resolve_transactions(transactions)` that takes a list of transactions as input and returns a dictionary representing the final state of each transaction. The dictionary should be keyed by the transaction ID, and the value should be either `COMMITTED` or `ABORTED`.

**Conflict Resolution Rules:**

1.  **Commit Dominance:** If *any* node has committed a transaction, the transaction must be committed globally.  This is to ensure that once a commit is observed, it cannot be rolled back.

2.  **Abort Propagation:** If *any* node has aborted a transaction, and *no* node has committed the transaction, then the transaction must be aborted globally.

3.  **Prepared State:** If all nodes are in the `PREPARED` state for a given transaction, you must simulate a global commit.

**Input Format:**

`transactions` is a list of lists. Each inner list represents a single transaction and contains tuples of the form `(node_id, transaction_id, state)`.

*   `node_id`: An integer representing the ID of the node.
*   `transaction_id`: An integer representing the ID of the transaction.
*   `state`: A string representing the state of the transaction on the node (`"PREPARED"`, `"COMMITTED"`, or `"ABORTED"`).

Example:

```python
transactions = [
    [(1, 101, "PREPARED"), (2, 101, "PREPARED")],
    [(1, 102, "COMMITTED"), (2, 102, "PREPARED")],
    [(1, 103, "ABORTED"), (2, 103, "PREPARED")],
    [(1, 104, "ABORTED"), (2, 104, "ABORTED")],
    [(1, 105, "PREPARED"), (2, 105, "ABORTED")]
]
```

**Output Format:**

A dictionary where keys are transaction IDs and values are either `"COMMITTED"` or `"ABORTED"`.

Example (corresponding to the input above):

```python
{
    101: "COMMITTED",
    102: "COMMITTED",
    103: "ABORTED",
    104: "ABORTED",
    105: "ABORTED"
}
```

**Constraints:**

*   The number of transactions can be large (up to 10<sup>6</sup>).
*   The number of nodes can be large (up to 10<sup>3</sup>).
*   Transaction IDs are integers.
*   Node IDs are integers.
*   Your solution should be efficient in terms of both time and space complexity. Consider using appropriate data structures to optimize performance.

**Bonus Challenges:**

*   Handle the case where the input data is streamed (i.e., you cannot load all transactions into memory at once).
*   Implement a mechanism to detect and handle cycles in the transaction dependencies (e.g., transaction A depends on transaction B, and transaction B depends on transaction A).  While the problem description doesn't *explicitly* create dependencies, imagine a scenario where the *order* of operations within a transaction matters for consistency.  Cycles could then create ambiguity in the commit/abort decision.  (This is a hint towards a more complex graph-based solution).
*   Consider the scenario where a node can be in an `UNCERTAIN` state due to a timeout. In this case, you need to implement a timeout mechanism that eventually resolves the transaction.
