Okay, here's a challenging problem description for a high-level programming competition.

## Question: Distributed Transaction Orchestration

**Scenario:**

You are building a distributed system that manages financial transactions across multiple independent microservices.  Each microservice is responsible for a specific aspect of a transaction (e.g., `AccountService` manages account balances, `PaymentService` processes payments, `NotificationService` sends notifications).  Transactions must be atomic: either all operations succeed, or all operations are rolled back to maintain data consistency.

**Problem:**

Implement a robust and efficient transaction orchestrator that ensures atomicity across these microservices. The orchestrator receives a transaction request, coordinates the execution of operations in each microservice, and handles potential failures, rolling back changes if necessary.

**Specific Requirements:**

1.  **Transaction Request:** The orchestrator receives a transaction request containing a list of operations to be performed by different microservices. Each operation includes the target microservice, the operation type (e.g., "debit", "credit", "send"), and relevant parameters.

2.  **Two-Phase Commit (2PC):** Implement a simplified version of the Two-Phase Commit protocol to coordinate the transaction.
    *   **Phase 1 (Prepare):** The orchestrator sends a "prepare" message to each involved microservice, asking it to tentatively execute its operation and reserve the necessary resources.  Each microservice must respond with either a "commit-ok" or "rollback-required" message. The microservice state must not be updated in this phase.
    *   **Phase 2 (Commit/Rollback):**
        *   If *all* microservices respond with "commit-ok", the orchestrator sends a "commit" message to each microservice, instructing it to permanently apply the changes.
        *   If *any* microservice responds with "rollback-required", or if the orchestrator times out waiting for a response from any microservice, the orchestrator sends a "rollback" message to all microservices, instructing them to undo any tentative changes.

3.  **Microservice Interface:**  Assume each microservice exposes a simple API with two endpoints:
    *   `/prepare`: Receives a prepare request. Returns "commit-ok" or "rollback-required".
    *   `/commit` or `/rollback`: Receives a commit or rollback request.  Returns "success" or "failure".
    Your solution should be able to handle failure responses from these commit and rollback endpoints.

4.  **Failure Handling:**
    *   **Microservice Failure:** If a microservice fails to respond to a prepare, commit, or rollback request within a specified timeout, the orchestrator must assume failure and initiate a rollback.  You must handle cases where a microservice fails *during* the rollback process itself.
    *   **Orchestrator Failure:** Design the orchestrator to be resilient to failures. Consider how the orchestrator can recover from a crash and resume coordinating transactions that were in progress. (Consider writing to a transaction log).

5.  **Concurrency:** The orchestrator must be able to handle multiple concurrent transaction requests efficiently. Use appropriate concurrency mechanisms to avoid race conditions and deadlocks.

6.  **Optimization:** Minimize the latency of transaction processing. Consider how you can optimize the communication between the orchestrator and the microservices. (Parallelization)

7.  **Idempotency:** Ensure that the commit and rollback operations are idempotent. A microservice might receive the same commit or rollback request multiple times due to network issues or orchestrator retries.

**Constraints:**

*   The number of microservices involved in a transaction can vary.
*   Microservices may have dependencies on each other (e.g., one microservice's operation might depend on the successful completion of another's). You do not need to handle dependency resolution. Assume dependencies are handled outside of this system.
*   Network communication is unreliable. Messages can be lost or delayed.
*   Microservices are stateless and rely on external databases for persistence.
*   The orchestrator should use asynchronous communication with microservices (e.g., message queues, asynchronous HTTP requests).

**Evaluation Criteria:**

*   **Correctness:** Does the orchestrator guarantee atomicity under all conditions?
*   **Robustness:** How well does the orchestrator handle failures and recover from crashes?
*   **Performance:** How efficiently does the orchestrator process transactions?
*   **Code Quality:** Is the code well-structured, readable, and maintainable?
*   **Scalability:** Can the orchestrator handle a large number of concurrent transactions?

This problem requires a solid understanding of distributed systems concepts, concurrency, and error handling. Good luck!
