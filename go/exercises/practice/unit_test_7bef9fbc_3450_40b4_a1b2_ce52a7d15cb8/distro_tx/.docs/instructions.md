Okay, here's a challenging Go coding problem designed to be LeetCode hard.

**Project Name:** `DistributedTransactionCoordinator`

**Question Description:**

You are tasked with implementing a simplified distributed transaction coordinator (DTC) for a microservices architecture.  Imagine a system where multiple independent services need to participate in a single atomic transaction. If any service fails to commit its changes, the entire transaction must be rolled back.

Your DTC needs to manage transactions across these services using a two-phase commit (2PC) protocol. Each participating service (participant) will implement a `Prepare`, `Commit`, and `Rollback` endpoint over HTTP.

**Core Requirements:**

1.  **Transaction Management:** Implement a `TransactionCoordinator` struct with methods to begin a new transaction, register participants, and execute the two-phase commit protocol.  The transaction ID should be a UUID string.

2.  **Participant Registration:**  Provide a mechanism to register participants in a transaction. A participant is defined by its service URL (e.g., `http://service-a:8080`) and a timeout value. The timeout specifies the maximum time the coordinator will wait for a response from the participant.

3.  **Two-Phase Commit:**
    *   **Phase 1 (Prepare):**  The coordinator sends a `Prepare` request to each participant. Each participant should respond with either "ACK" (meaning it's ready to commit) or "NACK" (meaning it cannot commit).
    *   **Phase 2 (Commit/Rollback):**
        *   If *all* participants respond with "ACK" in Phase 1, the coordinator sends a `Commit` request to each participant.
        *   If *any* participant responds with "NACK" or times out in Phase 1, the coordinator sends a `Rollback` request to each participant.

4.  **Error Handling:** Implement robust error handling.  The coordinator must handle network errors, timeouts, and unexpected responses from participants.  It should retry `Commit` or `Rollback` operations a configurable number of times if they initially fail, using exponential backoff.  If a participant continues to fail after retries, log the error and proceed with the transaction as best as possible (i.e., continue to attempt to commit or rollback other participants).

5.  **Concurrency:** The coordinator must be thread-safe and able to handle multiple concurrent transactions. Use appropriate locking mechanisms to prevent race conditions.

6.  **Timeout Management:** Strictly enforce timeouts. If a participant doesn't respond within the specified timeout, consider it a failure ("NACK" in Phase 1).

7.  **Idempotency:** Assume that `Commit` and `Rollback` operations on the participants are idempotent. This means they can be called multiple times without causing unintended side effects.

8.  **Logging:** Implement basic logging to track the progress of transactions, including participant registration, prepare results, commit/rollback decisions, and any errors encountered.

**Constraints:**

*   You *must* use the `net/http` package for making HTTP requests to the participants.
*   You *must* use `context` package for managing timeouts and cancellations.
*   You *must* implement retry logic with exponential backoff.
*   The system should be resilient to temporary network failures.
*   The maximum number of participants in a transaction is limited to 10.
*   The maximum length of a service URL is 256 characters.
*   Participants could be slow and/or unresponsive.

**Participant Service Contract (HTTP Endpoints):**

*   `POST /prepare`:  Returns "ACK" on success, "NACK" on failure, or a timeout/error.
*   `POST /commit`:   Returns "OK" on success, or a timeout/error.
*   `POST /rollback`: Returns "OK" on success, or a timeout/error.

All endpoints should return HTTP status code 200 on success. Other status codes should be considered an error. The request body for each endpoint should be empty.

**Bonus Challenges:**

*   Implement a recovery mechanism to handle coordinator crashes.  On restart, the coordinator should be able to determine the status of in-flight transactions and complete them. (This would require persistence of transaction state).
*   Add support for distributed deadlock detection.
*   Implement compensation transactions for cases where rollback is impossible.

This problem challenges the solver to design a robust, concurrent, and fault-tolerant distributed system component using Go. It requires a strong understanding of concurrency, networking, error handling, and distributed systems concepts.  The constraints force careful consideration of resource management and potential failure scenarios. Good luck!
