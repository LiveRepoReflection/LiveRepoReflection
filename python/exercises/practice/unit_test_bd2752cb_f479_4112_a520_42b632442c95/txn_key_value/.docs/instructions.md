## Question: Distributed Transactional Key-Value Store with Conflict Resolution

**Problem Description:**

You are tasked with designing and implementing a simplified, distributed, transactional key-value store. The store consists of `N` nodes, where `N` can be a relatively large number (e.g., 1000). Each node stores a subset of the key-value pairs. You will be given a series of transactions to execute. Each transaction involves reading and writing multiple key-value pairs.

Your system must provide ACID (Atomicity, Consistency, Isolation, Durability) properties. Because of the distributed nature, achieving strong consistency is difficult. Therefore, you will implement a serializable snapshot isolation (SSI) level of consistency.

However, network partitions and concurrent transactions can lead to conflicts. You need to implement a mechanism for conflict detection and resolution using a centralized timestamp oracle. Each transaction will be assigned a unique timestamp by the oracle at the beginning of the transaction.

**Specifically, you need to implement the following functionalities:**

1.  **`get_timestamp()`:** A function that retrieves a unique, monotonically increasing timestamp from a central timestamp oracle. You can assume the oracle is reliable and highly available.

2.  **`begin_transaction()`:** A function that initiates a transaction. It should retrieve a timestamp from the `get_timestamp()` function and return a transaction ID (which is the timestamp itself).

3.  **`read(transaction_id, key)`:** A function that reads the value associated with a given `key` within the context of a specific `transaction_id`. The read should be performed against a consistent snapshot. If the key does not exist or the transaction is invalid, return `None`.

4.  **`write(transaction_id, key, value)`:** A function that writes a `value` associated with a given `key` within the context of a specific `transaction_id`. The write should be buffered locally until the transaction is committed.

5.  **`commit_transaction(transaction_id)`:** A function that attempts to commit a transaction. This involves checking for conflicts (described below) and applying the buffered writes if the transaction can be committed. If a conflict is detected, the transaction should be rolled back, and the function should return `False`. If the transaction is successfully committed, the function should return `True`.

6.  **`abort_transaction(transaction_id)`:** A function that aborts a transaction and discards any buffered writes.

**Conflict Detection and Resolution:**

A conflict occurs when two concurrent transactions (T1 and T2) access the same key and at least one of them is a write. More specifically:

*   **Write-Write Conflict:** If T1 writes to key K and T2 also writes to key K.
*   **Read-Write Conflict:** If T1 reads key K, and T2 writes to key K, and the commit timestamp of T2 is earlier than the commit timestamp of T1.

To detect conflicts, you must maintain:

*   A read set for each transaction, tracking all keys read by the transaction.
*   A write set for each transaction, tracking all keys written by the transaction.
*   The latest committed timestamp for each key.

When `commit_transaction()` is called:

1.  Check for any conflicts between the current transaction and any other committed or committing transactions based on their read and write sets, and the latest committed timestamp for each key.

2.  If a conflict is detected, roll back the transaction (discard buffered writes) and return `False`.

3.  If no conflicts are detected, apply the buffered writes to the key-value store, update the latest committed timestamp for each written key, and return `True`.

**Constraints:**

*   The number of nodes, keys, and transactions can be very large (up to 10<sup>6</sup>).
*   The key-value store must be scalable and performant.  Consider how the data is distributed and accessed.
*   Transactions can be interleaved (multiple transactions can be active simultaneously).
*   You are allowed to use in-memory data structures for the key-value store and transaction management (for simplicity).
*   You are responsible for implementing the core logic of the distributed transaction management, conflict detection, and resolution. You don't need to implement the actual network communication between nodes. Just simulate the behavior of a distributed system.
*   Your solution should be thread-safe to handle concurrent transactions.

**Optimization Requirements:**

*   Minimize the latency of `read()` and `commit_transaction()` operations.
*   Optimize conflict detection to avoid unnecessary rollbacks.
*   Consider using appropriate data structures for efficient lookup and update of read/write sets and committed timestamps.

**Input:**

The input will be a series of operations, each specifying a transaction ID, operation type (read, write, commit, abort), key, and value (for write operations).

**Output:**

The output should be the result of each operation (the value read, or True/False for commit/abort).

**Example:**

```
begin_transaction() -> 1
read(1, "A") -> None
write(1, "A", "value1")
commit_transaction(1) -> True
begin_transaction() -> 2
read(2, "A") -> "value1"
write(2, "A", "value2")
commit_transaction(2) -> True
read(2, "A") -> "value2"
begin_transaction() -> 3
read(3, "A") -> "value2"
write(3, "B", "value3")
commit_transaction(3) -> True
```

This problem requires a good understanding of distributed systems concepts, concurrency control, and data structures. It also demands careful consideration of performance and scalability issues. Good luck!
