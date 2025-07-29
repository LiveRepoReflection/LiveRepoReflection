## Problem: Distributed Transaction Manager

### Question Description

Design and implement a simplified distributed transaction manager for a microservices architecture.  This system must ensure atomicity and consistency across multiple independent services when updating data.  Imagine an e-commerce application where placing an order requires updating inventory, processing payment, and creating a shipment record.  Each of these actions is handled by a separate microservice.  Your task is to build a system that guarantees either all three actions succeed, or none of them do, even in the face of network failures or service outages.

The transaction manager will coordinate these actions using the Two-Phase Commit (2PC) protocol with a Coordinator and Participants.

**System Components:**

1.  **Coordinator:** This component is the central transaction manager. It initiates the transaction, coordinates the prepare and commit/rollback phases, and maintains the overall transaction state.

2.  **Participants:** These represent the individual microservices involved in the transaction (e.g., Inventory Service, Payment Service, Shipping Service). Each participant is responsible for performing its part of the transaction and responding to the Coordinator's commands.

**Requirements:**

1.  **Prepare Phase:** The Coordinator sends a "prepare" request to all Participants. Each Participant attempts to tentatively perform its part of the transaction and responds with either a "vote-commit" (if successful) or "vote-abort" (if an error occurs).  The tentative change must be durable (e.g., written to a persistent store, but not yet visible to other transactions).

2.  **Commit/Rollback Phase:**
    *   If all Participants vote to commit, the Coordinator sends a "commit" request to all Participants. Each Participant then permanently applies its changes.
    *   If any Participant votes to abort, the Coordinator sends a "rollback" request to all Participants. Each Participant then reverts any tentative changes.

3.  **Failure Handling:** The system must handle the following failure scenarios:
    *   **Participant Failure:** If a Participant fails to respond to the prepare or commit/rollback request, the Coordinator must assume the worst (abort) and initiate a rollback for all other Participants. Implement a timeout mechanism for detecting unresponsive participants.
    *   **Coordinator Failure:** If the Coordinator fails after the prepare phase but before completing the commit/rollback phase, Participants must be able to recover and complete the transaction consistently. This is the most challenging aspect of the problem.  Assume Participants have logged their vote decision durably.  Upon Coordinator recovery, Participants should query the Coordinator for the final decision.  To simplify this, the Coordinator recovery process can be manually triggered.
    *   **Network Partition:** Consider how the system behaves during network partitions.  While you don't need to fully implement network partition handling, explain your design choices and the potential consequences of partitions.

4.  **Concurrency:**  The transaction manager must support concurrent transactions. Implement appropriate locking or concurrency control mechanisms to prevent data corruption.

5.  **Optimization:** Minimize the duration of locks held by Participants. Participants should release locks as early as possible while ensuring consistency.

6.  **Logging:**  Implement logging for all key events (prepare requests, votes, commit/rollback commands, failures, recoveries) to aid in debugging and auditing.

**Constraints:**

*   Implement the core logic of the Coordinator and Participants. You can simulate the actual microservices (Inventory, Payment, Shipping) with simple data stores (e.g., in-memory maps or simple file-based persistence) and mock operations. Focus on the transaction management aspects.
*   Assume Participants can handle idempotent commit and rollback operations. This means that executing the same commit or rollback command multiple times has the same effect as executing it once.
*   Assume a relatively small number of Participants per transaction (e.g., less than 10).

**Deliverables:**

1.  Well-documented code demonstrating the implementation of the Coordinator and Participants.
2.  A clear explanation of your design choices, including the data structures used, the concurrency control mechanisms, and the failure handling strategies.
3.  A description of how your system handles the Coordinator failure recovery scenario.
4.  A discussion of the limitations of your design and potential improvements.
5.  Consider the case where participants may be slow. How can you guarantee liveness of the transaction without unduly penalizing performance?

**Grading Criteria:**

*   Correctness: Does the system correctly implement the 2PC protocol and guarantee atomicity and consistency?
*   Failure Handling: Does the system gracefully handle Participant and Coordinator failures?
*   Concurrency: Does the system support concurrent transactions without data corruption?
*   Optimization: Is the system designed to minimize lock contention and improve performance?
*   Clarity and Documentation: Is the code well-documented and easy to understand? Is the design clearly explained?
*   Handling Slow Participants

This problem is designed to be challenging and requires a good understanding of distributed systems concepts, concurrency control, and failure handling. Good luck!
