## Problem: Distributed Transaction Coordinator

**Description:**

You are tasked with designing a distributed transaction coordinator for a simplified database system. This system consists of multiple database shards, each responsible for storing a subset of the total data. Transactions can involve multiple shards, requiring a mechanism to ensure atomicity and consistency across all involved shards.

Your goal is to implement a transaction coordinator that adheres to the Two-Phase Commit (2PC) protocol, with extensions to handle node failures and optimize commit decisions.

**System Architecture:**

*   **Transaction Coordinator (TC):** Your implementation will act as the TC. It receives transaction requests from clients, coordinates the transaction execution across the shards, and makes the final commit or rollback decision.
*   **Database Shards (Participants):**  Each shard is a database instance that can perform local operations (read/write) and vote to commit or abort a transaction. You can simulate the behavior of the shards using data structures within your solution; actual database interaction is not required.

**Transaction Flow:**

1.  **Request:** A client sends a transaction request to the TC, specifying the operations to be performed on various shards. Each operation is represented as a shard ID and a simple read/write action on a key-value pair stored in that shard (e.g., `(shard_id, operation_type, key, value)`).
2.  **Prepare Phase:** The TC sends a "prepare" message to all shards involved in the transaction. Each shard attempts to tentatively execute the operations specified for it, logs the changes it would make, and replies with a "vote" (either "commit" or "abort").  Shards must be able to undo these tentative changes if a rollback is necessary. Shards MUST use a write-ahead log (WAL) to ensure durability.
3.  **Commit/Rollback Phase:**
    *   If all shards vote "commit," the TC sends a "commit" message to all shards. Each shard then makes the changes permanent.
    *   If any shard votes "abort," or if the TC doesn't receive a response from a shard within a specified timeout, the TC sends a "rollback" message to all shards. Each shard then undoes the tentative changes.
4.  **Acknowledgement:** After completing the commit or rollback, each shard sends an acknowledgment to the TC.
5.  **Response:** The TC sends a final response to the client indicating the success or failure of the transaction.

**Requirements:**

1.  **Atomicity:**  All involved shards must either commit or rollback the transaction consistently.
2.  **Durability:** Once a transaction is committed, the changes must survive even if the TC or shards crash.  Use a write-ahead log (WAL) to ensure that the shards can recover their state after a crash. The WAL entries only need to store enough information to redo or undo the tentative changes, not a full database snapshot.
3.  **Failure Handling:**
    *   **Shard Failure:**  If a shard fails during the prepare or commit/rollback phase, the TC should handle the failure gracefully.  Implement a timeout mechanism. If a shard doesn't respond within a reasonable time, the TC should consider the shard to have failed and initiate a rollback. Upon shard recovery, it should consult a persistent log to determine the outcome of any in-flight transactions and complete them accordingly (commit or rollback).
    *   **TC Failure:** If the TC fails after sending prepare message but before sending the final commit/rollback message, the shards should be able to resolve the transaction state upon TC recovery. Shards must store the transaction ID and their vote persistently to achieve this.
4.  **Optimization:**  Implement an optimization to reduce the latency of the commit phase in the common case where all shards vote "commit". The TC can send the commit message concurrently to all shards, rather than waiting for acknowledgments from each shard before sending to the next. However, the TC still needs to ensure that the transaction has been durably committed on all shards before responding to the client.
5.  **Concurrency:** The TC should be able to handle multiple concurrent transactions.
6.  **Logging:** Implement proper logging to track transaction progress, shard votes, and any failures that occur. This will aid in debugging and recovery.
7.  **Idempotency:** The prepare, commit, and rollback operations on the shards should be idempotent. This means that if a shard receives the same message multiple times (due to network issues or TC retries), it should only process it once and not cause any unintended side effects.

**Constraints:**

*   The number of shards can be up to 100.
*   The number of concurrent transactions can be up to 1000.
*   The size of each key-value pair is limited to 1KB.
*   The timeout for shard responses is 5 seconds.
*   Memory usage should be optimized to avoid excessive memory consumption when handling a large number of concurrent transactions.

**Evaluation Criteria:**

*   Correctness: Does the solution correctly implement the 2PC protocol and guarantee atomicity and durability?
*   Failure Handling: Does the solution gracefully handle shard and TC failures?
*   Performance: Does the solution efficiently manage concurrent transactions and optimize the commit phase?
*   Code Quality: Is the code well-structured, readable, and maintainable?
*   Logging: Does the solution provide sufficient logging for debugging and recovery?

This problem challenges you to apply advanced data structures and algorithms, handle complex failure scenarios, and optimize for performance in a distributed environment. Good luck!
