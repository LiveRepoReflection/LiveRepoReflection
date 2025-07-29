## Question: Distributed Transaction Simulator

### Question Description

You are building a simplified simulator for distributed transactions across multiple database shards. Your task is to implement a system that can process a series of transactions, each potentially involving multiple shards, and determine if the overall series of transactions can be committed without violating consistency.

**System Setup:**

*   You have `N` database shards, numbered from 0 to N-1.
*   Each shard stores a single integer value. Initially, all shards have a value of 0.
*   Transactions are atomic; they either fully succeed (commit) or fully fail (rollback).
*   Transactions can read and write to multiple shards.

**Input:**

You are given a list of transactions. Each transaction is represented as a list of operations. Each operation is a tuple: `(shard_id, operation_type, value)`.

*   `shard_id`: An integer representing the ID of the shard involved in the operation (0 <= shard_id < N).
*   `operation_type`: A string, either `"read"` or `"write"`.
*   `value`: An integer. If `operation_type` is `"read"`, this is the expected value of the shard for the read to be valid. If `operation_type` is `"write"`, this is the new value to be written to the shard.

**Constraints:**

*   **Atomicity:** All operations within a transaction must succeed for the transaction to commit. If any operation fails (e.g., a read operation finds a different value than expected), the entire transaction must roll back, leaving all shards unchanged.
*   **Consistency:** Reads must return the current value of the shard at the time of the read within the transaction. A read operation fails if the current value of the shard doesn't match the expected `value` specified in the operation.
*   **Concurrency:** Transactions are processed sequentially in the order they appear in the input list. Each transaction must execute in isolation. There is no need to handle concurrent transactions.
*   **Isolation:** Each transaction operates on a consistent snapshot of the database. No intermediate state of a transaction is visible to other transactions.
*   **Rollback:** If a transaction fails (due to a read operation failing), the values of all shards must be restored to their state before the transaction began.

**Output:**

Your function should return a boolean value: `True` if all transactions can be successfully committed in the given order, and `False` if any transaction fails and causes the entire process to halt (i.e., no further transactions are attempted after the first failure).

**Example:**

Let's say you have 2 shards (N=2).

```python
transactions = [
    [(0, "read", 0), (0, "write", 1)],  # Transaction 1: Read shard 0 (expecting 0), then write 1 to shard 0.
    [(1, "read", 0), (1, "write", 2)],  # Transaction 2: Read shard 1 (expecting 0), then write 2 to shard 1.
    [(0, "read", 1), (1, "read", 2), (0, "write", 3), (1, "write", 4)],  # Transaction 3: Read shard 0 (expecting 1), Read shard 1 (expecting 2), then write 3 to shard 0 and 4 to shard 1.
]
```

In this case, all transactions can be committed successfully. Your function should return `True`.

Now, consider this example:

```python
transactions = [
    [(0, "read", 0), (0, "write", 1)],
    [(1, "read", 0), (1, "write", 2)],
    [(0, "read", 2), (1, "read", 2), (0, "write", 3), (1, "write", 4)],  # Transaction 3: Fails because shard 0 has value 1, not 2.
    [(0, "read", 3), (1, "read", 4)], #Transaction 4 is never executed
]
```

In this case, Transaction 3 fails because it expects shard 0 to have a value of 2, but it actually has a value of 1. Your function should return `False`. Transaction 4 will never be executed.

**Optimization Requirements:**

*   Minimize the number of shard value copies and state management.
*   Aim for efficient read and write operations.

**Edge Cases to Consider:**

*   Empty transaction list.
*   Empty transaction.
*   Transactions with only reads or only writes.
*   Transactions reading the same shard multiple times.
*   Transactions writing to the same shard multiple times.
*   Invalid shard IDs.
*   Invalid operation types.

**Clarifications:**

*   Assume the input list `transactions` is well-formed (i.e., no syntax errors, correct data types). Focus on the logic of transaction processing and consistency.
*   If there are any invalid inputs (like incorrect shard ID, incorrect operation type), the whole process should halt immediately, returning `False`.

Good luck!
