## Problem: Distributed Transaction Coordinator

### Description

You are tasked with designing and implementing a simplified distributed transaction coordinator for a system that manages financial transactions across multiple independent banking services. This system aims to ensure the ACID properties (Atomicity, Consistency, Isolation, Durability) in a distributed environment.

Imagine a scenario where a user wants to transfer funds from their account in Bank A to another user's account in Bank B. Each bank operates as an independent service with its own database and API. A distributed transaction is necessary to ensure that either both the debit from Bank A and the credit to Bank B succeed, or neither happens.

Your transaction coordinator will manage the transaction lifecycle, ensuring consistency even if failures occur at any point.

### Core Functionality

1.  **Transaction Initiation:**
    *   The coordinator receives a request to initiate a transaction involving multiple banking services (participants).
    *   The request contains a unique transaction ID (UUID), and a list of participant bank service details (e.g., endpoint URLs).

2.  **Two-Phase Commit (2PC) Protocol:**
    *   **Phase 1 (Prepare):** The coordinator sends a "prepare" message to each participant, asking them to tentatively perform their part of the transaction (e.g., reserve the funds in Bank A, prepare to credit the funds in Bank B). Participants must respond with either "prepared" (if successful) or "abort" (if they cannot proceed).
    *   **Phase 2 (Commit/Rollback):**
        *   If *all* participants respond with "prepared", the coordinator sends a "commit" message to all participants, instructing them to permanently apply the changes.
        *   If *any* participant responds with "abort", or if the coordinator doesn't receive a response from a participant within a reasonable timeout, the coordinator sends a "rollback" message to all participants, instructing them to undo any tentative changes.

3.  **Failure Handling:**
    *   **Timeout:** Implement timeouts for participant responses. If a participant doesn't respond within the timeout, the coordinator should consider the transaction as failed and initiate a rollback.
    *   **Crash Recovery:** The coordinator needs to be able to recover its state after a crash. This means persisting the state of ongoing transactions (transaction ID, participants, their prepare status) to a durable storage (e.g., a file or in-memory database) before sending out prepare messages. Upon restart, the coordinator should reload its state and resume any interrupted transactions. For simplicity, assume only the coordinator can crash, not the participants. The participants are reliable and will eventually respond.

4.  **Idempotency:** The coordinator should handle duplicate commit or rollback requests gracefully. Participants might receive the same commit/rollback message multiple times due to network issues or coordinator restarts.

5.  **Logging:** The coordinator should log all significant events (transaction start, prepare sent, responses received, commit/rollback decisions, recovery events) for debugging and auditing purposes.

### Constraints & Requirements

*   **Concurrency:** The coordinator must be able to handle multiple concurrent transactions.
*   **Scalability:** While not the primary focus, consider how your design could be scaled to handle a large number of concurrent transactions.
*   **Performance:** Optimize for reasonable performance. Minimize the time it takes to complete a transaction, considering network latency and participant processing time.
*   **Error Handling:** Implement robust error handling to gracefully handle unexpected situations, such as network errors, participant failures, and invalid input.
*   **Participant Interaction:** Assume a simple HTTP-based API for communication with the participant banking services.  They expose endpoints for prepare, commit, and rollback. You can represent these with dummy implementations.
*   **Durable Storage:** For simplicity, use an in-memory data structure (e.g., a `HashMap`) for persisting the transaction states. However, design your code in a way that it can easily be plugged into a persistent storage mechanism (e.g., a file or a database) later on.  Consider using a suitable interface.
*   **Testability:** Your code should be well-structured and testable. Design your classes and methods to be easily mocked and unit-tested.

### Input

The coordinator will receive transaction requests in the following format:

```json
{
    "transactionId": "UUID",
    "participants": [
        {
            "serviceName": "BankA",
            "prepareEndpoint": "http://banka.example.com/prepare",
            "commitEndpoint": "http://banka.example.com/commit",
            "rollbackEndpoint": "http://banka.example.com/rollback"
        },
        {
            "serviceName": "BankB",
            "prepareEndpoint": "http://bankb.example.com/prepare",
            "commitEndpoint": "http://bankb.example.com/commit",
            "rollbackEndpoint": "http://bankb.example.com/rollback"
        }
    ]
}
```

### Output

The coordinator doesn't directly return a value. Its success is measured by the correct execution of the 2PC protocol, ensuring that all participants either commit or rollback the transaction consistently. The logs will provide evidence of the coordinator's behavior.

### Judging Criteria

*   **Correctness:** Does the coordinator correctly implement the 2PC protocol, ensuring atomicity and consistency?
*   **Robustness:** Does the coordinator handle failures (timeouts, crashes) gracefully?
*   **Concurrency:** Can the coordinator handle multiple concurrent transactions without data corruption or race conditions?
*   **Performance:** Is the coordinator reasonably efficient?
*   **Code Quality:** Is the code well-structured, readable, and maintainable?
*   **Testability:** Is the code designed in a way that it can be easily tested?

This problem requires a good understanding of distributed systems concepts, concurrency, and error handling. Successfully implementing a robust and efficient transaction coordinator is a challenging but rewarding task. Good luck!
