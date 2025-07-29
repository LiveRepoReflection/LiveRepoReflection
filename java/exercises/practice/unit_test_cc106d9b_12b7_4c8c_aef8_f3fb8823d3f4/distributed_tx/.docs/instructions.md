## Problem: Distributed Transaction Coordinator

### Question Description

You are tasked with designing and implementing a distributed transaction coordinator (DTC) for a simplified banking system. This system involves multiple independent banking services (referred to as "participants") that need to coordinate to perform atomic transactions, such as transferring funds between accounts held at different banks.

Each participant service manages its own database and can perform local transactions. However, to ensure data consistency across the entire system, inter-bank transactions must adhere to the ACID properties (Atomicity, Consistency, Isolation, Durability).

Your DTC must implement a two-phase commit (2PC) protocol to guarantee atomicity. The system involves one coordinator and multiple participants.

**Participants:** Each participant is a banking service that can either commit or rollback a local transaction based on the coordinator's instructions. Participants communicate directly with the coordinator. Participants are unreliable and might crash anytime.

**Coordinator:** The coordinator is responsible for managing the global transaction. It communicates with all participants to ensure that either all participants commit the transaction or all rollback. Coordinator is unreliable and might crash anytime.

**Requirements:**

1.  **Two-Phase Commit (2PC):** Implement the 2PC protocol to ensure atomicity. The protocol should include the following phases:

    *   **Phase 1 (Prepare Phase):** The coordinator sends a "prepare" message to all participants, asking them to tentatively execute the transaction and vote whether they can commit or not. Participants respond with either "commit-vote" (yes) or "rollback-vote" (no). A participant should write its vote to stable storage (e.g., disk) before responding. The participant might crash after the prepare phase and needs to recover to its pre-crash state.
    *   **Phase 2 (Commit/Rollback Phase):**
        *   If the coordinator receives "commit-vote" from all participants, it sends a "commit" message to all participants.
        *   If the coordinator receives at least one "rollback-vote" or a timeout occurs, it sends a "rollback" message to all participants.
        *   Participants execute the commit or rollback action and acknowledge the coordinator. Participants should write its commit or rollback state to stable storage (e.g., disk) before responding. The participant might crash after the decision phase and needs to recover to its pre-crash state.

2.  **Crash Recovery:** Implement crash recovery mechanisms for both the coordinator and participants. The system should be able to recover from crashes during any phase of the 2PC protocol. This involves:

    *   **Logging:** Participants must log their actions (prepare vote, commit, rollback) to stable storage so they can recover to a consistent state. Coordinator must log the global decision (commit or rollback).
    *   **Recovery Procedure:** Upon restart, the coordinator and participants must examine their logs to determine the state of any in-flight transactions and take appropriate actions to complete or undo them. If the crash occurs before the coordinator sends the commit or rollback message (before Phase 2), the default action must be rollback.

3.  **Timeout Handling:** Implement timeout mechanisms to handle unresponsive participants. If a participant does not respond within a reasonable time during the prepare phase, the coordinator should assume a "rollback-vote".

4.  **Idempotency:** Ensure that commit and rollback operations are idempotent. Participants should be able to handle duplicate commit or rollback messages without causing errors.

5.  **Concurrency:** Implement concurrency control to allow multiple transactions to be processed concurrently. Use appropriate locking mechanisms to prevent data corruption and ensure isolation. Assume a shared-nothing architecture where each participant has its own database.

6.  **Optimization:** Design your solution to minimize the number of messages exchanged between the coordinator and participants. Consider ways to optimize the logging process to reduce disk I/O. Aim to minimize the latency of the transaction commit.

**Constraints:**

*   You can use in-memory storage for simulation purposes, but you should design your logging mechanism to be easily adaptable to persistent storage (e.g., file system).
*   Assume a maximum number of participants per transaction (e.g., 10).
*   Assume a maximum transaction size (e.g., a limited number of operations per transaction).
*   You are free to choose the messaging protocol (e.g., TCP, HTTP).
*   Error handling and edge cases should be considered thoroughly.
*   Assume that network communication is reliable (no message loss or corruption, but delays are possible).

**Deliverables:**

1.  Java code implementing the DTC, including the coordinator and participant components.
2.  A clear explanation of your design choices, including the logging mechanism, crash recovery procedure, and concurrency control strategy.
3.  A demonstration of the system's functionality, including successful commit and rollback scenarios, crash recovery scenarios, and timeout handling scenarios.
4.  A discussion of the trade-offs in your design and potential optimizations.

**Judging Criteria:**

*   Correctness: The DTC must correctly implement the 2PC protocol and ensure atomicity.
*   Robustness: The DTC must be able to handle crashes and timeouts gracefully.
*   Efficiency: The DTC should minimize message exchanges and logging overhead.
*   Design: The design should be well-structured, modular, and easy to understand.
*   Documentation: The explanation of the design and demonstration of functionality should be clear and concise.

This problem requires a strong understanding of distributed systems concepts, transaction processing, concurrency control, and fault tolerance. Good luck!
