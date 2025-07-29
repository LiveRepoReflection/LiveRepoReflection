## Problem: Distributed Transaction Manager with Conflict Resolution

**Description:**

You are tasked with designing and implementing a simplified distributed transaction manager (DTM) for a system involving multiple independent database shards. Imagine a scenario where a social media application distributes its user data across several database shards based on user ID.  A single user action (e.g., transferring credits from one user to another) might involve updating records in multiple shards. To ensure data consistency, these updates must be performed atomically – either all shards successfully update, or none do.

Your DTM must coordinate transactions across these shards. Each transaction will involve a set of operations, where each operation modifies data within a specific shard. The DTM must ensure the ACID properties (Atomicity, Consistency, Isolation, Durability) are maintained, focusing particularly on atomicity and isolation.

**Specific Requirements:**

1.  **Transaction Representation:** A transaction `T` is defined as a list of operations. Each operation `O` consists of:
    *   `shardId`: An integer identifying the target database shard.
    *   `operationType`: An enum representing the type of operation (`READ`, `WRITE`).
    *   `key`: A string representing the data key to be accessed within the shard.
    *   `value`: (Only for `WRITE` operations) A string representing the new value to be written.

2.  **Shard Interface:** Assume you have a `Shard` interface with the following methods:
    *   `read(key: String): String` - Reads the value associated with the given key. Returns `null` if the key does not exist.
    *   `write(key: String, value: String): Boolean` - Writes the given value to the given key. Returns `true` if successful, `false` otherwise.
    *   `prepare(transactionId: String, operations: List<Operation>): Boolean` - Prepares the shard for the given transaction, verifying that the operations in the list can be successfully executed. Returns `true` if preparation succeeds, `false` otherwise.
    *   `commit(transactionId: String): Boolean` - Commits the transaction on the shard. Returns `true` if successful, `false` otherwise.
    *   `rollback(transactionId: String): Boolean` - Rolls back the transaction on the shard. Returns `true` if successful, `false` otherwise.

3.  **DTM Implementation:** Implement a class `DistributedTransactionManager` with the following methods:
    *   `begin(): String` - Starts a new transaction and returns a unique transaction ID (String).
    *   `execute(transactionId: String, operations: List<Operation>): Boolean` - Executes the given operations within the given transaction.  This method must implement a two-phase commit (2PC) protocol to ensure atomicity.
    *   `commit(transactionId: String): Boolean` - Commits the transaction with the given ID.
    *   `rollback(transactionId: String): Boolean` - Rolls back the transaction with the given ID.

4.  **Conflict Resolution:** Implement a basic conflict resolution mechanism.  If a shard detects a conflict during the prepare phase (e.g., another transaction has already modified the data being accessed), it should return `false` from the `prepare` method.  Your DTM should handle this scenario gracefully by rolling back the transaction on all shards. To simulate concurrent transaction, you can use Thread.sleep() in Shard's method.

5.  **Concurrency:** Your DTM must be thread-safe, allowing multiple transactions to execute concurrently. Use appropriate synchronization mechanisms (e.g., locks) to prevent race conditions and ensure data integrity.

6.  **Optimizations (Optional but highly encouraged):**
    *   **Read-Only Optimization:** If a shard only contains `READ` operations for a given transaction, skip the prepare phase for that shard and directly commit the reads during the commit phase.
    *   **Batching:** Batch multiple operations for the same shard in the `prepare`, `commit`, and `rollback` phases to reduce the number of network calls (simulated within your implementation).

**Constraints:**

*   Number of shards: 1 to 10.
*   Number of operations per transaction: 1 to 100.
*   Length of `key` and `value` strings: 1 to 100 characters.
*   Implement robust error handling and logging.
*   Minimize the total execution time, especially when handling conflicts.

**Judging Criteria:**

*   Correctness: Your solution must correctly implement the 2PC protocol and ensure data consistency across all shards.
*   Concurrency Safety: Your solution must be thread-safe and handle concurrent transactions without data corruption.
*   Efficiency: Your solution should be optimized for performance, minimizing the overhead of transaction management.
*   Conflict Resolution: Your DTM should handle conflicts gracefully and roll back transactions when necessary.
*   Code Quality: Your code should be well-structured, readable, and maintainable. The use of design patterns is encouraged.

This problem requires a strong understanding of distributed systems concepts, concurrency control, and data structures. Good luck!
