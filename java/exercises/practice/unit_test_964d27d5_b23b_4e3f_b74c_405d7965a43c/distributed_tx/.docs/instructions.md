## Problem: Distributed Transaction Coordinator

### Question Description

You are tasked with designing a distributed transaction coordinator for a simplified banking system. The system consists of multiple independent bank servers, each managing a subset of customer accounts. To transfer funds between accounts residing on different bank servers, a distributed transaction is required.

Your goal is to implement a coordinator that ensures Atomicity, Consistency, Isolation, and Durability (ACID) properties for these cross-server transactions using a Two-Phase Commit (2PC) protocol.

**System Components:**

1.  **Coordinator:** The central component responsible for initiating, coordinating, and finalizing distributed transactions.
2.  **Participant (Bank Server):** Each bank server acts as a participant in the 2PC protocol. It manages its local transaction state and communicates with the coordinator.

**Assumptions:**

*   Communication between the coordinator and participants is reliable (no message loss).
*   Each participant has its own local transaction management system. You do not need to implement the local transaction management within each participant; you can assume it exists and provides the necessary primitives (`prepare`, `commit`, `rollback`).
*   Participants can unilaterally abort a transaction during the prepare phase.
*   Participants can recover from failures and replay their logs.
*   The system needs to handle concurrent transactions initiated by different users.
*   The system should be resilient to coordinator failures. Upon recovery, the coordinator should be able to determine the status of any in-flight transactions and complete them.

**Requirements:**

Implement the `Coordinator` class with the following methods:

*   `beginTransaction(transactionId: String, participants: List<Participant>):` Starts a new distributed transaction with the given ID and list of participating bank servers.
*   `prepareTransaction(transactionId: String): Boolean` Sends a "prepare" message to all participants. Returns `true` if all participants voted to commit (prepared successfully), `false` otherwise.
*   `commitTransaction(transactionId: String):` Sends a "commit" message to all participants if the prepare phase was successful.
*   `rollbackTransaction(transactionId: String):` Sends a "rollback" message to all participants if the prepare phase failed or if an error occurred.
*   `recover():` Recovers the state of the coordinator after a failure. It should check the logs and complete or rollback any in-flight transactions.

Implement the `Participant` interface with the following methods:

*   `prepare(transactionId: String): Boolean`  Simulates the participant preparing for the transaction. Returns `true` to vote commit, `false` to vote abort.
*   `commit(transactionId: String):` Simulates the participant committing the transaction.
*   `rollback(transactionId: String):` Simulates the participant rolling back the transaction.

**Constraints:**

*   **Concurrency:** The solution must handle multiple concurrent transactions safely.
*   **Durability:** Transaction state changes at the coordinator must be persisted to a durable log (e.g., a simple file) to ensure recovery after a crash.  The log should contain enough information to reconstruct the state of all transactions.
*   **Efficiency:** The implementation should minimize the number of network round trips and the amount of data written to the log.
*   **Error Handling:** The solution must handle potential errors, such as participant failures or network issues, gracefully.
*   **Idempotency:** The `commit` and `rollback` operations on participants should be idempotent.

**Bonus:**

*   Implement a mechanism to handle coordinator failures during the commit/rollback phase.  This requires the participants to be able to determine the final outcome of the transaction even if the coordinator crashes before sending the commit/rollback message.
*   Implement a mechanism for detecting and resolving deadlocks that may occur due to concurrent transactions.
*   Implement an optimization to allow participants to be added or removed from a transaction after the prepare phase, but before the commit phase. This could be useful for handling situations where a new account needs to be involved in the transfer.

This problem requires a strong understanding of distributed systems concepts, concurrency control, and persistent storage. It challenges the solver to design a robust and efficient transaction coordinator that can handle complex failure scenarios. Good Luck!
