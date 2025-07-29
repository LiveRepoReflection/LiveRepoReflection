Okay, here's a challenging C++ problem description, designed to be difficult and open to multiple optimized solutions, with real-world implications.

## Problem: Distributed Transaction Coordinator Optimization

### Question Description

You are tasked with designing and implementing a highly efficient transaction coordinator for a distributed database system.  The system consists of `N` database shards, each independently managing its own data.  Transactions can involve multiple shards, requiring a two-phase commit (2PC) protocol to ensure atomicity (all shards commit or all shards rollback).

Each transaction is represented by a unique transaction ID (`txID`).  A transaction `txID` can potentially involve any subset of the `N` shards.  The coordinator is responsible for managing the 2PC protocol for each transaction.

The system receives a stream of transaction requests.  Each request specifies:

*   `txID` (unique integer)
*   A list of `shardIDs` (integers from 1 to `N`) involved in the transaction
*   A `commitWeight` (positive integer) representing the importance of committing this transaction successfully.  Higher `commitWeight` means it's more crucial to commit the transaction.

Your task is to implement the transaction coordinator, which must support the following operations:

1.  **`BeginTransaction(txID, shardIDs, commitWeight)`:**  Registers a new transaction. The coordinator must track the shards involved, and the `commitWeight`.

2.  **`Prepare(txID, shardID, vote)`:**  A shard signals its readiness to commit or abort a transaction.  `vote` is a boolean: `true` indicates the shard is ready to commit, `false` indicates it votes to abort.

3.  **`CommitTransaction(txID)`:**  Attempts to commit a transaction. This function should implement the core logic of the 2PC protocol.  A transaction can only commit if *all* involved shards have voted to commit (`true`) in the `Prepare` phase.

4.  **`RollbackTransaction(txID)`:** Forces a transaction to rollback, regardless of shard votes.

5.  **`GetHeaviestUndecidedTransaction()`:** Returns the `txID` of the undecided transaction with the highest `commitWeight`. If no undecided transactions exist, return -1.  A transaction is considered "undecided" if not all involved shards have responded with their `Prepare` votes.  In case of ties for `commitWeight`, return the `txID` of the transaction that began earlier (lower `txID` value).

**Constraints:**

*   `1 <= N <= 1000` (Number of shards)
*   `1 <= txID <= 10^9` (Transaction ID)
*   `1 <= commitWeight <= 10^9`
*   The number of shards involved in a single transaction can vary significantly, from 1 to `N`.
*   The number of concurrent transactions can be large (up to 10^6).
*   Transactions can arrive in any order (i.e., `Prepare` calls might arrive before `BeginTransaction` for a given `txID`, requiring proper handling).
*   The system should be highly efficient in terms of both time and space complexity.  Minimize latency for all operations, especially `CommitTransaction` and `GetHeaviestUndecidedTransaction`.

**Optimization Requirements:**

*   **Minimize Commit Latency:** The `CommitTransaction` operation must be as fast as possible.  Consider how to efficiently determine if all shards have voted to commit.
*   **Efficient `GetHeaviestUndecidedTransaction`:** This operation must be optimized to avoid iterating through all transactions.  Consider using appropriate data structures for efficient retrieval.
*   **Concurrency Considerations:** While you don't need to implement actual threading, design your data structures and logic to be thread-safe (consider how locks would be applied) as this system would likely be running in a concurrent environment.
*   **Memory Management:**  Pay attention to memory usage.  Avoid unnecessary memory allocations and deallocations.

**Edge Cases to Consider:**

*   Duplicate `BeginTransaction` calls for the same `txID`.  The second call should be ignored.
*   `Prepare` calls for a `txID` that doesn't exist.  The call should be ignored.
*   `Prepare` calls from the same `shardID` for the same `txID` multiple times.  Only the first vote should be considered.
*   Calling `CommitTransaction` or `RollbackTransaction` on a `txID` that doesn't exist.  The call should be ignored.
*   Calling `CommitTransaction` or `RollbackTransaction` multiple times on the same `txID`.  Subsequent calls should be ignored.
*   Empty set of shards passed to `BeginTransaction`.

This problem requires a combination of careful data structure selection, algorithmic thinking, and attention to detail to handle edge cases.  Good luck!
