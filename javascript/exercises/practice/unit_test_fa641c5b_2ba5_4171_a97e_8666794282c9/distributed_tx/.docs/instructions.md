## Project Name:

`Distributed Transaction Coordinator`

## Question Description:

You are tasked with designing and implementing a distributed transaction coordinator (DTC) service. This service is responsible for ensuring the atomicity and consistency of transactions that span multiple independent services (participants). The DTC must implement a two-phase commit (2PC) protocol, with the ability to handle various failure scenarios.

**Scenario:**

Imagine an e-commerce platform where an order creation involves multiple services: `InventoryService`, `PaymentService`, and `OrderService`. When a user places an order, we need to ensure that either all three services successfully process their part of the transaction (reserve inventory, process payment, create order), or none of them do. This requires a distributed transaction.

**Requirements:**

1.  **2PC Implementation:** Implement the 2PC protocol with the following phases:
    *   **Phase 1 (Prepare Phase):** The DTC sends a `prepare` request to all participants. Each participant attempts to perform its part of the transaction and responds with either `vote_commit` if successful, or `vote_abort` if it fails.
    *   **Phase 2 (Commit/Rollback Phase):**
        *   If all participants voted to commit (`vote_commit`), the DTC sends a `commit` request to all participants.
        *   If any participant voted to abort (`vote_abort`), or if the DTC times out waiting for a response from any participant, the DTC sends a `rollback` request to all participants.
2.  **Failure Handling:** The DTC must handle the following failure scenarios:
    *   **Participant Failure:** A participant fails to respond to the `prepare` request within a reasonable timeout. The DTC must assume `vote_abort` and initiate a rollback.
    *   **DTC Failure:** If the DTC fails *after* sending the `prepare` request but *before* completing the commit/rollback phase, upon recovery, the DTC must determine the state of the transaction (committed or rolled back) based on persisted logs and complete the protocol accordingly. You need to implement a basic logging mechanism for this.
    *   **Message Loss:**  Assume that the underlying communication channel is unreliable, and messages between the DTC and participants can be lost. Implement a retry mechanism with exponential backoff for both `prepare` and `commit/rollback` phases.
3.  **Concurrency:** The DTC must be able to handle multiple concurrent transactions. Ensure thread safety and prevent race conditions.
4.  **Idempotency:**  Participants must handle `commit` and `rollback` requests idempotently.  They should only perform the action once, even if they receive the same request multiple times (e.g., due to retries).
5.  **Optimization:** Design the DTC and participant communication for optimal performance.  Consider minimizing the number of network calls and optimizing data serialization.
6.  **Scalability Considerations:** Briefly document how your design could be scaled horizontally to handle a larger number of concurrent transactions and participants.  This doesn't require code implementation, but a description of the architectural approach is expected.

**Constraints:**

*   Use JavaScript (Node.js is recommended, but not mandatory).
*   Minimize external dependencies.  Focus on implementing the core logic of the 2PC protocol. Libraries for logging, timers, or basic data structures are acceptable.
*   The DTC and participant services can be simulated within a single process for simplicity (e.g., using in-memory data structures and message passing), but the design should be such that they could be easily deployed as separate microservices.
*   Assume that each participant has a unique identifier.
*   The DTC must maintain a log of transaction states (prepare, commit, rollback) and participant votes. This log must be persisted to disk for recovery purposes.  A simple file-based log is sufficient.
*   Implement a configurable timeout for the `prepare` phase.

**Input:**

The input to the DTC is a list of participants and a transaction ID. Each participant is represented by a unique identifier and a function that simulates the participant's action (e.g., reserve inventory, process payment).

**Output:**

The DTC should return a boolean value indicating whether the transaction was successfully committed (true) or rolled back (false).

**Evaluation Criteria:**

*   Correctness of the 2PC implementation, including handling of all failure scenarios.
*   Code quality, readability, and maintainability.
*   Efficiency and performance of the DTC and participant communication.
*   Scalability considerations.
*   Completeness of the logging mechanism and recovery procedure.
*   Adherence to the given constraints.

This problem requires a strong understanding of distributed systems concepts, concurrency, and error handling. It also tests your ability to design and implement a complex system with multiple interacting components. Good luck!
