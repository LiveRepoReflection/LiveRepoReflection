## Question: Distributed Transaction Coordinator

### Question Description

You are tasked with designing and implementing a simplified distributed transaction coordinator service in Rust. This coordinator is responsible for ensuring the atomicity and consistency of transactions spanning multiple independent data services (think databases, message queues, etc.). The system should support the two-phase commit (2PC) protocol.

**Scenario:**

Imagine a scenario where a user wants to transfer funds from one bank account to another. This operation requires modifications to two separate database services: the source account database and the destination account database. To guarantee that either both operations succeed or both fail, a distributed transaction is necessary.

**Requirements:**

1.  **Transaction Management:** Your coordinator must be able to initiate, track, and finalize distributed transactions. Each transaction should be assigned a unique transaction ID (UUID).

2.  **Two-Phase Commit (2PC):** Implement the 2PC protocol. This involves the following phases:

    *   **Prepare Phase:** The coordinator sends a "prepare" message to all participating data services (participants). Each participant attempts to perform its part of the transaction and responds with either a "vote commit" (if successful and the participant is ready to commit) or a "vote abort" (if any error occurred or the participant cannot commit). Each participant must persist its "prepared" state to stable storage before responding.

    *   **Commit/Abort Phase:**
        *   If the coordinator receives "vote commit" from all participants, it sends a "commit" message to all participants. Participants then permanently commit their changes.
        *   If the coordinator receives a "vote abort" from any participant or a timeout occurs during the prepare phase, it sends an "abort" message to all participants. Participants then rollback any changes made during the prepare phase.
        *   Participants must persistently log the commit or abort decision before executing it.

3.  **Concurrency:** The coordinator must handle multiple concurrent transactions efficiently.

4.  **Failure Handling:** The system must be resilient to failures. Consider the following scenarios:

    *   **Coordinator Failure:** If the coordinator fails during the commit/abort phase, participants must be able to resolve the transaction state upon coordinator recovery. Participants should periodically check in with the coordinator or implement a timeout mechanism to detect coordinator failures. When the coordinator recovers, it reads the transaction log to determine the outcome of the transaction and notifies the participants accordingly.
    *   **Participant Failure:** If a participant fails after voting to commit but before receiving the final decision (commit or abort), it must recover its state from its persistent log and complete the transaction according to the coordinator's decision.

5.  **Persistence:** Implement persistent storage for the transaction log (coordinator) and participant transaction states. You can use a simple file-based storage for this purpose, but consider the performance implications of writing to disk frequently.

6.  **Timeout:** Implement reasonable timeouts for each phase of the 2PC protocol. If a participant doesn't respond within the timeout period, the coordinator should abort the transaction.

7.  **Optimization:** Minimize network round trips and latency where possible. Consider batching operations or using asynchronous communication.

**Constraints:**

*   You are not required to implement the actual data services (databases, message queues). Instead, you can simulate them with mock implementations that simply record whether a commit or abort operation was performed.
*   Assume a maximum of 10 participants per transaction.
*   Minimize external crate dependencies. Focus on using standard Rust libraries where possible.
*   The system must be able to handle at least 100 concurrent transactions.

**Evaluation Criteria:**

*   Correctness: Does the system correctly implement the 2PC protocol and guarantee atomicity?
*   Resilience: How well does the system handle failures and recover from them?
*   Concurrency: Can the system handle multiple concurrent transactions efficiently?
*   Performance: Is the system optimized for minimal latency and resource usage?
*   Code Quality: Is the code well-structured, readable, and maintainable?

This problem requires a deep understanding of distributed systems concepts, concurrency, and error handling. A robust and well-optimized solution will be highly challenging to implement. Good luck!
