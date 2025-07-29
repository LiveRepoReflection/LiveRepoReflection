## Problem: Distributed Transaction Coordinator

**Description:**

You are tasked with designing and implementing a simplified distributed transaction coordinator. This system needs to ensure the ACID properties (Atomicity, Consistency, Isolation, Durability) across multiple independent database shards.

Imagine a large e-commerce platform where user data (profiles, addresses, payment methods) is sharded across `N` databases. When a user updates their profile, the changes might affect multiple shards. Your system must ensure that either all shards successfully commit the changes, or none of them do (atomicity).

**Specific Requirements:**

1.  **Two-Phase Commit (2PC) Protocol:** Implement the 2PC protocol to coordinate transactions across the `N` shards. Your coordinator should manage the transaction lifecycle:
    *   **Prepare Phase:** Send a "prepare" request to each shard. Each shard should attempt to apply the changes tentatively and respond with either "prepared" (ready to commit) or "abort" (unable to commit).
    *   **Commit/Abort Phase:** Based on the responses from the prepare phase, the coordinator decides whether to commit or abort the transaction. It then sends a "commit" or "abort" request to all shards.
    *   **Acknowledgement:** Each shard, upon receiving the commit or abort message, must execute the command and send an acknowledgement back to the coordinator.
2.  **Shard Interface:** Define a simple interface for the database shards. This interface should include methods for:
    *   `prepare(transactionId, data)`: Receive and tentatively apply changes. Return `true` if prepared, `false` otherwise. Simulate failures and return false randomly (e.g., 10% chance).
    *   `commit(transactionId)`: Permanently apply prepared changes.
    *   `abort(transactionId)`: Rollback prepared changes.
    *   `getStatus(transactionId)`: Return the shard's current status for a specific transaction (e.g., `PREPARED`, `COMMITTED`, `ABORTED`, `NONE`).
3.  **Concurrency:** The coordinator should handle multiple concurrent transactions. Use appropriate synchronization mechanisms to prevent race conditions and ensure data integrity.
4.  **Failure Handling:** Implement basic failure handling:
    *   **Timeout:** If a shard does not respond within a reasonable timeout period during either the prepare or commit/abort phase, the coordinator should assume the shard has failed and abort the transaction.
    *   **Recovery (Simple):** When a shard restarts after a failure, it should be able to determine the status of any incomplete transactions (transactions in `PREPARED` state) by examining its local transaction logs. Implement a simple recovery mechanism where the shard requests the coordinator to determine whether to commit or abort the transaction based on the coordinator's transaction log.
5.  **Logging:** The coordinator should maintain a transaction log. This log should record the state of each transaction (e.g., `INITIATED`, `PREPARED`, `COMMITTED`, `ABORTED`) and the decisions made during the 2PC protocol.  The log must be persisted to disk to enable recovery of the coordinator.

**Constraints:**

*   The number of shards, `N`, is configurable.
*   The simulated database shards are memory-based. Data does not need to survive JVM restarts beyond the recovery scenario mentioned above.
*   The transaction data (`data` in the `prepare` method) can be a simple string.
*   Assume a partially synchronous network - messages are not guaranteed to be delivered, but the probability of message loss is low.
*   Focus on the core 2PC logic and failure handling. You do not need to implement complex features like deadlock detection or sophisticated recovery mechanisms.
*   **Performance Requirement:** The coordinator should be able to handle at least 100 concurrent transactions without significant performance degradation (e.g., average transaction completion time should remain below 1 second).

**Evaluation Criteria:**

*   **Correctness:** Does the system correctly implement the 2PC protocol and ensure ACID properties across all shards?
*   **Concurrency Handling:** Does the system handle concurrent transactions correctly and efficiently?
*   **Failure Handling:** Does the system handle shard failures and coordinator restarts gracefully and recover to a consistent state?
*   **Code Quality:** Is the code well-structured, readable, and maintainable?
*   **Performance:** Does the system meet the performance requirements for concurrent transaction processing?
*   **Completeness:** Does the solution implement all the required functionalities described in the problem statement?
