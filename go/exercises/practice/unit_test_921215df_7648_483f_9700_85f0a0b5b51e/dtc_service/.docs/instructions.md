## Project Name

`Distributed Transaction Coordinator`

## Question Description

You are tasked with building a highly scalable and reliable Distributed Transaction Coordinator (DTC) service. This service is responsible for orchestrating transactions across multiple independent services (participants) in a distributed system. The goal is to ensure atomicity – either all participants commit their changes, or all roll back, even in the face of failures (network partitions, service crashes, etc.).

Specifically, implement the Two-Phase Commit (2PC) protocol. Your DTC should handle a large number of concurrent transactions, each potentially involving different sets of participants. Each participant exposes a simple HTTP API with two endpoints: `prepare` and `commit/rollback`.

**Participants API:**

*   **`POST /prepare`**:  The DTC calls this on each participant in the transaction's first phase.  The participant should attempt to tentatively apply the changes associated with the transaction and respond with either `200 OK` (meaning it is prepared to commit) or `409 Conflict` (meaning it cannot commit, for example due to resource constraints or data conflicts). The participant should persist its prepared state (e.g., using a write-ahead log) to survive crashes.

*   **`POST /commit`** or **`POST /rollback`**: The DTC calls one of these on each participant in the second phase, depending on the outcome of the first phase. On `commit`, the participant should permanently apply the changes. On `rollback`, the participant should undo any tentative changes made during the prepare phase. Both operations should be idempotent (safe to execute multiple times). Returns `200 OK` if successful.

**DTC Requirements:**

1.  **Correctness:**  Implement the 2PC protocol correctly to guarantee atomicity. All or nothing should occur.

2.  **Concurrency:** Handle a high volume of concurrent transactions. Implement efficient locking or other concurrency control mechanisms to prevent race conditions and ensure data integrity within the DTC itself.

3.  **Durability:** The DTC must persist transaction state (participants, status, etc.) to durable storage (e.g., a file-based store or embedded database) to recover from crashes. The state should be serializable/deserializable. This ensures that ongoing transactions can be resumed after a restart.

4.  **Fault Tolerance:** Handle participant failures during the prepare and commit/rollback phases. Implement retry logic with exponential backoff to tolerate transient network issues. If a participant remains unavailable after a configured number of retries, the DTC should unilaterally rollback the transaction.

5.  **Idempotency:** Ensure all operations within the DTC are idempotent where appropriate, allowing for safe retries.

6.  **Timeout:** If a participant fails to respond to the prepare or commit/rollback message within a specified timeout, the DTC should consider the participant failed and proceed with a rollback.

7.  **Scalability:** Design the DTC to be horizontally scalable. While you don't need to implement actual distribution, consider how you would shard the transaction state across multiple DTC instances. Think about the data structures and algorithm usage.

8.  **API:**  Provide a simple HTTP API for clients to start transactions. The request body should contain a list of participant URLs.

    *   **`POST /transactions`**: Starts a new transaction.  Request body: `["http://participant1/prepare", "http://participant2/prepare", ...]`. Response: `201 Created` with the transaction ID in the `Location` header.

    *   **`GET /transactions/{transactionId}`**: Retrieves the status of a transaction. Response: `200 OK` with a JSON payload indicating the transaction status (`pending`, `committed`, `rolledback`).

**Constraints:**

*   You are free to choose your preferred Go libraries for HTTP handling, data persistence, and concurrency.
*   Assume that participant URLs are unique.
*   Assume that participants are well-behaved and will always respond with a valid HTTP status code (200 OK or 409 Conflict) within a reasonable time, or not at all.
*   Error handling and logging should be robust and informative.
*   Focus on correctness, concurrency, and durability first. Performance optimization is secondary.
*   The number of participants is limited.

**Bonus Points:**

*   Implement a mechanism for detecting and resolving orphaned transactions (transactions that were in progress when the DTC crashed and are now in an inconsistent state).
*   Implement a distributed lock manager to coordinate access to shared resources across participants.

This problem tests your understanding of distributed systems concepts, concurrency, fault tolerance, and data persistence. It requires careful consideration of edge cases and trade-offs between performance and reliability. Good luck!
