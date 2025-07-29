## Problem Title: Distributed Transaction Manager

### Question Description:

You are tasked with designing and implementing a simplified distributed transaction manager. This system manages transactions that span multiple independent data shards (databases). Each data shard can commit or rollback its portion of the transaction independently, but the goal is to ensure atomicity across all shards – either all shards commit, or all shards rollback.

Your transaction manager should handle a series of transaction requests. Each transaction involves updates to data distributed across `N` different shards (numbered 0 to N-1). Due to network latency and shard load, the shards might not process updates in the same order.

**Input:**

The input is a sequence of transaction operations. Each operation is one of the following:

1.  **BEGIN <transaction_id>**: Starts a new transaction with the given `<transaction_id>` (an integer).  Transaction IDs are unique.
2.  **UPDATE <transaction_id> <shard_id> <data>**:  Represents an update operation within the transaction `<transaction_id>` on shard `<shard_id>` with the data `<data>`. `<data>` is a string.
3.  **PREPARE <transaction_id>**:  Instructs the transaction manager to initiate the prepare phase for the transaction `<transaction_id>`. The prepare phase involves asking each shard involved in the transaction whether it is ready to commit.
4.  **COMMIT <transaction_id>**:  Instructs the transaction manager to commit the transaction `<transaction_id>`.  This command should only be executed if all shards involved in the transaction have successfully prepared.
5.  **ROLLBACK <transaction_id>**:  Instructs the transaction manager to rollback the transaction `<transaction_id>`. This command should be executed if any shard fails to prepare, or if explicitly requested.
6.  **GET <shard_id>**: Retrieves the current data stored in shard `<shard_id>`.

**Shard Behavior:**

*   Each shard maintains its own data storage (a simple key-value store where the key is implicitly associated with the `UPDATE` command, and the value is the `<data>` string).  Initially, each shard's storage is empty (no keys exist).
*   When a shard receives an `UPDATE` request for a transaction, it tentatively applies the update but does *not* commit it to persistent storage *yet*. This update is only visible within the context of that transaction.
*   When a shard receives a `PREPARE` request for a transaction, it checks if it can successfully commit the tentative updates for that transaction.
    *   If the shard *can* commit (e.g., no conflicts, sufficient resources), it responds positively (it "votes" to commit) and transitions to a "prepared" state for that transaction.  The shard *must* persist the tentative update to durable storage.
    *   If the shard *cannot* commit (e.g., conflicts, insufficient resources), it responds negatively (it "votes" to rollback) and discards the tentative updates for that transaction. The shard *must* revert to the state before receiving the `UPDATE` commands for this transaction.
*   When a shard receives a `COMMIT` request for a transaction that it has prepared, it permanently applies the updates to its persistent storage.
*   When a shard receives a `ROLLBACK` request for a transaction, it discards the tentative updates for that transaction and reverts to the state before receiving the `UPDATE` commands for this transaction.  If a shard is in the "prepared" state, it *must* still rollback.

**Output:**

For each `GET <shard_id>` operation, output the current data stored in the specified shard. If no data exists for that shard (it's empty), output "NULL".

**Constraints:**

*   `1 <= N <= 100` (Number of shards)
*   Transaction IDs are unique integers within the range `[1, 100000]`.
*   Shard IDs are integers within the range `[0, N-1]`.
*   The `<data>` string can contain alphanumeric characters and spaces, and its length is at most 100 characters.
*   The number of operations can be up to 100,000.
*   The system must ensure atomicity: all shards involved in a transaction either commit, or all rollback.
*   The system should be reasonably efficient.  Naive solutions that repeatedly iterate through all updates will likely time out. Consider using appropriate data structures to track transaction state and updates.
*   The system must be thread-safe. Multiple operations can be performed concurrently across different shards.

**Example:**

```
Input:
BEGIN 123
UPDATE 123 0 "initial data"
UPDATE 123 1 "more data"
PREPARE 123
COMMIT 123
GET 0
GET 1
BEGIN 456
UPDATE 456 0 "new data"
PREPARE 456
ROLLBACK 456
GET 0
GET 1

Output:
initial data
more data
NULL
more data
```

**Judging Criteria:**

*   Correctness: The system must correctly implement distributed transactions with atomicity.
*   Efficiency: The system should handle a large number of operations within a reasonable time limit.
*   Concurrency: The system should be thread-safe and handle concurrent operations correctly.
*   Code Clarity: The code should be well-structured and easy to understand.
