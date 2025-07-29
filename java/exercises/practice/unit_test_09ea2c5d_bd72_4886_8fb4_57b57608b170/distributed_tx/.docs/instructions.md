## Problem: Distributed Transaction Coordinator

**Description:**

You are tasked with designing a distributed transaction coordinator for a system of microservices. This system involves multiple independent services that need to participate in atomic transactions. Imagine a scenario where a user wants to transfer funds between two accounts residing on different database servers (managed by different microservices). To maintain data consistency, this transfer must be atomic: either both accounts are updated, or neither is.

Your goal is to implement a coordinator service that manages these distributed transactions using the Two-Phase Commit (2PC) protocol. The coordinator will orchestrate the participating services (participants) to ensure atomicity, consistency, isolation, and durability (ACID properties).

**System Architecture:**

*   **Coordinator Service:** The central service responsible for initiating, coordinating, and finalizing transactions.
*   **Participant Services:** Independent microservices that perform operations as part of a distributed transaction. Each participant has a local transaction manager that interacts with its local database.
*   **Communication:** Services communicate over a reliable network (e.g., using HTTP or gRPC).

**Requirements:**

1.  **2PC Implementation:** Implement the Two-Phase Commit protocol to manage distributed transactions. The coordinator must:
    *   Send a `PREPARE` message to all participants.
    *   Collect votes (`COMMIT` or `ABORT`) from all participants.
    *   Send a `COMMIT` message to all participants if all voted `COMMIT`.
    *   Send an `ABORT` message to all participants if any voted `ABORT`.
    *   Handle timeouts and failures during both phases.

2.  **Participant Interface:** Define a clear interface for participant services to interact with the coordinator. This interface should include endpoints for:
    *   Receiving `PREPARE` requests.
    *   Submitting votes (`COMMIT` or `ABORT`).
    *   Receiving `COMMIT` or `ABORT` commands.

3.  **Transaction Logging:** Implement a persistent transaction log in the coordinator to record the state of each transaction. This log should be durable and used to recover from coordinator failures. The log should contain enough information to guarantee that, after a crash and restart, the coordinator can complete any in-flight transactions in a consistent state.

4.  **Concurrency Control:** Handle concurrent transactions efficiently. The coordinator must ensure that transactions do not interfere with each other and that data consistency is maintained. Use appropriate locking or other concurrency control mechanisms.

5.  **Failure Handling and Recovery:** The system must be resilient to failures of both the coordinator and participant services. Implement mechanisms for:
    *   **Participant Failure:** If a participant fails during the prepare phase, the coordinator should abort the transaction. If a participant fails during the commit phase, the coordinator should retry the commit operation until the participant recovers and completes the commit.
    *   **Coordinator Failure:** If the coordinator fails, upon recovery, it must be able to determine the status of all in-flight transactions from the transaction log and complete them accordingly (either by committing or aborting). Use idempotent operations to ensure that retries do not lead to inconsistencies.

6.  **Optimistic Concurrency Control for Participants**: Participants should implement optimistic concurrency control (e.g., using versioning) to prevent lost updates and ensure data consistency. This is crucial because the duration of the distributed transaction can be long, increasing the chances of conflicts.

**Constraints:**

*   **Scalability:** The coordinator service should be designed to handle a large number of concurrent transactions.
*   **Performance:** Minimize the latency of distributed transactions. Consider the trade-offs between consistency and performance.
*   **Idempotency:** All operations performed by the coordinator and participants must be idempotent to ensure that retries do not cause inconsistencies.
*   **Isolation**:  While 2PC provides atomicity and durability, it can lead to long-duration locks. Consider strategies to minimize lock contention and maintain a reasonable level of isolation.

**Evaluation Criteria:**

*   Correctness of the 2PC implementation.
*   Robustness of failure handling and recovery mechanisms.
*   Efficiency of concurrency control.
*   Scalability and performance of the coordinator service.
*   Clarity and maintainability of the code.
*   Consideration of the trade-offs between consistency, performance, and isolation.
