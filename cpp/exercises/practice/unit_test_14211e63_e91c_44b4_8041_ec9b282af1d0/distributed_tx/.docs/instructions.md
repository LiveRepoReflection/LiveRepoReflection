## Question: Distributed Transaction Coordinator

**Description:**

You are tasked with designing and implementing a simplified distributed transaction coordinator. This coordinator is responsible for ensuring atomicity and consistency across multiple independent service nodes during a transaction.

Imagine a system where multiple microservices need to update their local databases as part of a single business transaction (e.g., booking a flight involves updating the seat availability service, the payment service, and the user profile service). If any of these services fail, the entire transaction must be rolled back to maintain data consistency.

Your coordinator should implement a two-phase commit (2PC) protocol to manage these distributed transactions. The system consists of:

1.  **Coordinator:** A central node that manages the transaction lifecycle.
2.  **Participants:** Independent service nodes that perform operations within the transaction.

**Requirements:**

1.  **Transaction Initiation:** The coordinator receives a request to initiate a new transaction involving a set of participants.

2.  **Phase 1 (Prepare Phase):**
    *   The coordinator sends a "prepare" message to all participants, asking them to tentatively perform their part of the transaction and indicate whether they are ready to commit.
    *   Each participant must either:
        *   Successfully prepare (e.g., tentatively update its local database) and send a "ready" message back to the coordinator. The participant must guarantee that it can commit the transaction if instructed to do so.
        *   Encounter an error, rollback its tentative changes, and send a "abort" message back to the coordinator.
    *   Participants must handle potential network timeouts and retry prepare operations a reasonable number of times before sending an "abort".

3.  **Phase 2 (Commit/Rollback Phase):**
    *   If the coordinator receives "ready" messages from all participants, it sends a "commit" message to all participants.
    *   If the coordinator receives one or more "abort" messages, or if it times out waiting for responses from all participants, it sends a "rollback" message to all participants.
    *   Upon receiving a "commit" message, each participant must permanently commit its changes.
    *   Upon receiving a "rollback" message, each participant must rollback its tentative changes.
    *   Participants must handle potential network timeouts during the commit/rollback phase and retry operations until they succeed. They must log errors and, if possible, alert an administrator if operations cannot complete.

4.  **Failure Handling:** The system must be resilient to the following failures:
    *   **Participant failure:** A participant crashes or becomes unresponsive during the prepare or commit/rollback phase.
    *   **Coordinator failure:** The coordinator crashes during the prepare or commit/rollback phase. (Assume the coordinator has persistent storage to recover transaction state).
    *   **Network partitions:** Temporary network outages prevent communication between the coordinator and participants.

5.  **Concurrency:** The coordinator must be able to handle multiple concurrent transactions.

6.  **Optimization:** Minimize the latency and resource usage of the coordinator. Consider how to optimize communication and data storage for efficiency.

**Constraints:**

*   Implement the coordinator and participant logic in C++.
*   Use threads or asynchronous programming to handle concurrency.
*   Use a simple message passing mechanism (e.g., sockets, message queues) for communication between the coordinator and participants.
*   Focus on correctness and robustness over raw performance.
*   Assume a maximum number of participants per transaction.
*   Assume the coordinator has access to persistent storage (e.g., a file or in-memory database with persistence capabilities) to recover transaction state after a crash.
*   Handle the "lost update" and "dirty read" problems by implementing proper locking mechanism.

**Evaluation Criteria:**

*   **Correctness:** Does the system correctly implement the 2PC protocol and ensure atomicity and consistency?
*   **Robustness:** How well does the system handle failures (participant crashes, coordinator crashes, network partitions)?
*   **Concurrency:** Can the system handle multiple concurrent transactions efficiently?
*   **Optimization:** How efficient is the system in terms of latency and resource usage?
*   **Code Quality:** Is the code well-structured, readable, and maintainable?
*   **Error Handling:** Is error handling comprehensive and informative?

This problem requires a solid understanding of distributed systems concepts, concurrency, and failure handling. It challenges the solver to design a robust and efficient distributed transaction coordinator using C++. Good luck!
