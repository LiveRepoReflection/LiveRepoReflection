## Question: Distributed Transaction Manager

### Question Description

You are tasked with designing and implementing a simplified, in-memory distributed transaction manager for a system of microservices. This system involves multiple services (Service A, Service B, Service C, etc.), each managing its own data and capable of performing independent operations. The goal is to ensure atomicity across these services; that is, either all operations across all participating services succeed, or none do.

Your transaction manager should support the following:

1.  **Transaction Initiation:** A client can initiate a transaction by contacting the transaction manager. The transaction manager assigns a unique transaction ID (UUID) to the transaction.
2.  **Service Registration:** Services must register with the transaction manager before participating in transactions. Each service registers its endpoint (e.g., URL) and a set of operations it can perform.
3.  **Two-Phase Commit (2PC) Protocol:** Implement a 2PC protocol to coordinate the transaction across participating services.

    *   **Phase 1 (Prepare):** The transaction manager sends a "prepare" request to all participating services, instructing them to tentatively execute their assigned operations and acknowledge whether they are ready to commit.  Services should perform the operation and hold resources (e.g., database locks) until the transaction outcome is known. Services must be idempotent in this phase (i.e., receiving the same prepare request multiple times doesn't cause issues).
    *   **Phase 2 (Commit/Rollback):** Based on the responses from the prepare phase, the transaction manager makes a global decision to either commit or rollback the transaction.
        *   If all services respond positively (ready to commit), the transaction manager sends a "commit" request to all participating services, instructing them to permanently apply the changes.
        *   If any service responds negatively (refuses to commit), or if the transaction manager times out waiting for a response, the transaction manager sends a "rollback" request to all participating services, instructing them to undo the changes.
4.  **Transaction Participation:** A client requests the transaction manager to include specific operations in a transaction.  The request includes the transaction ID, the target service, and the operation to be performed, and the data required to execute the operation.
5.  **Concurrency Handling:** The transaction manager must handle concurrent transactions.
6.  **Fault Tolerance:** Consider the following failure scenarios and implement mechanisms to handle them:
    *   **Service Failure:** A service might crash or become unavailable during the prepare or commit/rollback phase.
    *   **Transaction Manager Failure:** The transaction manager might crash during the prepare or commit/rollback phase.  Upon recovery, it should be able to resume and complete any in-flight transactions.  Persisting state to disk is not required; assume a simple, in-memory recovery mechanism is sufficient.
7. **Idempotency:** Services must be able to handle duplicate commit or rollback requests without causing unintended side effects.
8. **Timeouts**: The transaction manager must implement timeouts for both the prepare and commit/rollback phases. If a service does not respond within the timeout period, the transaction manager should initiate a rollback.

**Constraints:**

*   Implement the core logic of the transaction manager and the 2PC protocol. You don't need to implement actual microservices or network communication. Simulate service operations using simple data structures (e.g., in-memory maps).
*   Focus on correctness, concurrency, and fault tolerance.
*   Assume a maximum number of participating services per transaction.
*   Assume all operations are short-lived and do not require long-running processes.
*   Error handling and logging are important.
*   The solution should be designed to be scalable and efficient, considering the potential for a large number of concurrent transactions and services.

**Bonus:**

*   Implement a mechanism for services to proactively notify the transaction manager if they encounter an issue that requires a transaction to be rolled back.
*   Implement a retry mechanism for failed commit or rollback requests.
*   Consider how to handle transactions that are "orphaned" due to failures, where the transaction manager loses track of the transaction state.

This problem requires a solid understanding of distributed systems, concurrency, and fault tolerance. It also demands careful consideration of edge cases and potential failure scenarios. Good luck!
