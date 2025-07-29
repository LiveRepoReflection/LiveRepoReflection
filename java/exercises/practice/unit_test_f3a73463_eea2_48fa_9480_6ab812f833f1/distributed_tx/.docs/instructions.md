## Problem: Distributed Transaction Coordinator

**Description:**

You are building a distributed database system. A key requirement is ensuring atomicity across multiple database shards during transactions. To achieve this, you need to implement a distributed transaction coordinator.

Your system consists of multiple database shards (represented as `Shard` objects). Each shard can perform local transactions. However, when a transaction involves multiple shards, a distributed transaction must be coordinated to guarantee the ACID properties (Atomicity, Consistency, Isolation, Durability).

You are tasked with implementing a `TransactionCoordinator` class that manages these distributed transactions using a two-phase commit (2PC) protocol.

**Functionality:**

The `TransactionCoordinator` should provide the following functionalities:

1.  **`beginTransaction(transactionId)`:**  Starts a new distributed transaction with the given `transactionId`.  The `transactionId` is a unique identifier for the transaction.

2.  **`enlistShard(transactionId, shard)`:**  Adds a database `Shard` to the transaction identified by `transactionId`. Each shard will eventually participate in the 2PC protocol.  A shard can only be enlisted once per transaction.

3.  **`prepareTransaction(transactionId)`:**  Initiates the prepare phase of the 2PC protocol for the transaction `transactionId`. For each enlisted shard, the coordinator should call the `prepare()` method on the shard. The `prepare()` method on the shard will attempt to prepare the local transaction and return `true` if successful, `false` otherwise (e.g., due to a conflict, resource unavailability, or shard failure). The coordinator should handle shard failures gracefully.

4.  **`commitTransaction(transactionId)`:**  Initiates the commit phase of the 2PC protocol for the transaction `transactionId`. This can only be called if `prepareTransaction` has completed successfully (all shards voted to commit). For each enlisted shard, the coordinator should call the `commit()` method.  Handle shard failures during commit.

5.  **`rollbackTransaction(transactionId)`:**  Initiates the rollback phase of the 2PC protocol for the transaction `transactionId`.  This should be called if `prepareTransaction` failed (at least one shard voted to abort) or if an error occurs during commit.  For each enlisted shard, the coordinator should call the `rollback()` method. Handle shard failures during rollback.

**Constraints and Requirements:**

*   **Atomicity:**  The transaction must be atomic. Either all enlisted shards commit the transaction, or all shards rollback.
*   **Durability:** Once a transaction is committed, the changes must be durable even if the coordinator or some shards crash.
*   **Isolation:**  The coordinator itself doesn't need to strictly enforce isolation. Assume each `Shard` implementation handles its own isolation at the local level.
*   **Concurrency:**  The coordinator must be thread-safe and handle concurrent transaction requests.  Multiple transactions can be in progress simultaneously.
*   **Idempotency:**  The `commit()` and `rollback()` methods on the `Shard` interface must be idempotent.  The coordinator might call them multiple times in case of failures.
*   **Error Handling:** The coordinator should handle shard failures gracefully during all phases (prepare, commit, rollback). If a shard fails during commit, the coordinator should retry the commit operation (with a reasonable number of retries and backoff) until it succeeds or a maximum retry limit is reached.  If a shard fails during rollback, log the failure and continue rolling back the other shards. It is acceptable for a rollback to eventually require manual intervention if retries are exhausted.
*   **Optimization:** Minimize the latency of the transaction execution. Consider the number of network calls required and potential bottlenecks.  Avoid unnecessary synchronization.
*   **Data Structures:**  Choose appropriate data structures to efficiently store and manage transaction state and enlisted shards.
*   **Logging:** Implement basic logging to record transaction events, such as transaction start, shard enlistment, prepare result, commit/rollback completion, and shard failures.
*   **Shard Interface:** You are provided with a `Shard` interface that defines the `prepare()`, `commit()`, and `rollback()` methods.  You cannot modify this interface.

**Shard Interface (provided):**

```java
interface Shard {
    boolean prepare(String transactionId); // Attempt to prepare the local transaction. Return true if successful, false otherwise.
    void commit(String transactionId);    // Commit the local transaction.
    void rollback(String transactionId);  // Rollback the local transaction.
}
```

**Your Task:**

Implement the `TransactionCoordinator` class, adhering to the functionality, constraints, and requirements outlined above.  Pay close attention to concurrency, error handling, and optimization. The focus should be on ensuring atomicity and durability in the face of potential shard failures and concurrent transaction requests.
