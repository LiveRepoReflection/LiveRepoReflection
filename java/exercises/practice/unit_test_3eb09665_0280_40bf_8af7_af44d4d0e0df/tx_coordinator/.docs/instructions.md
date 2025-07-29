## Problem: Distributed Transaction Coordinator

**Description:**

You are tasked with building a simplified distributed transaction coordinator for a microservices architecture. In this system, multiple independent services need to participate in atomic transactions. The goal is to ensure that either all services commit their changes or all services roll back, even in the face of failures.

**System Architecture:**

*   **Transaction Coordinator (TC):** This is the central component you will implement. It manages the transaction lifecycle.
*   **Participant Services (PS):** These are the individual microservices that perform the actual work and hold data relevant to the transaction. Each service exposes an API for the TC to interact with.
*   **Message Queue (MQ):** Assume there's a reliable message queue (e.g., Kafka, RabbitMQ) for asynchronous communication between the TC and PS.

**Transaction Lifecycle:**

1.  **Begin:** A client requests a new transaction. The TC generates a unique transaction ID (TXID) and logs the transaction start.
2.  **Prepare:** The TC sends a "prepare" message (containing the TXID) to each participating PS. Each PS attempts to perform its part of the transaction and signals success or failure to the TC. The PS must hold the result of its operation (e.g. by creating a staging table) until the TC tells it to commit or rollback.
3.  **Commit/Rollback Decision:**
    *   If all PSs signal success, the TC sends a "commit" message to all PSs.
    *   If any PS signals failure, or if the TC times out waiting for a response from a PS, the TC sends a "rollback" message to all PSs.
4.  **Commit/Rollback Execution:**  Each PS executes the commit or rollback operation. The PS needs to handle duplicate commit/rollback messages.
5.  **End:** The TC logs the transaction completion (success or failure).

**Your Task:**

Implement the core logic of the **Transaction Coordinator (TC)** in Java.  The TC needs to:

1.  **Generate Unique Transaction IDs:** Create unique TXIDs for each new transaction.
2.  **Manage Transaction State:** Track the state of each transaction (e.g., `BEGIN`, `PREPARING`, `COMMIT_PENDING`, `ROLLBACK_PENDING`, `COMMITTED`, `ROLLED_BACK`).
3.  **Communicate with Participant Services:**
    *   Simulate sending "prepare," "commit," and "rollback" messages to PSs.  You don't need to set up a real MQ; instead, use a simplified interface (provided below).
    *   Handle responses (success/failure) from PSs.
    *   Implement a timeout mechanism for responses from PSs.
4.  **Implement Commit/Rollback Logic:** Based on the responses from PSs, decide whether to commit or rollback the transaction and send the appropriate messages.
5.  **Ensure Idempotency:** Make sure all operations can withstand duplicate messages or retries.
6.  **Handle Failures:**  Simulate PS failures (e.g., a PS doesn't respond to the "prepare" message).
7.  **Logging:** Implement basic logging to track the transaction lifecycle and decisions made by the TC.

**Constraints:**

*   **Scalability:** Consider the potential for a high volume of transactions.  Optimize for efficient memory usage and processing.
*   **Concurrency:** The TC should be able to handle multiple concurrent transactions. Use appropriate synchronization mechanisms.
*   **Error Handling:** Implement robust error handling to deal with unexpected situations (e.g., network issues, PS crashes).
*   **Timeout:** Implement a configurable timeout for the prepare phase. If a PS doesn't respond within the timeout, the transaction should be rolled back.
*   **Idempotency:** The prepare, commit, and rollback operations in PSs must be idempotent. The TC should be able to retry sending these messages without causing unintended side effects.
*   **Avoid Deadlocks:** Carefully consider locking strategies to prevent deadlocks in a multi-threaded environment.

**Simplified Interface for Participant Services (PS):**

Assume you have a `ParticipantService` interface with the following methods:

```java
interface ParticipantService {
    boolean prepare(String txId); // Returns true on success, false on failure. Can take time to simulate work
    boolean commit(String txId);  // Returns true on success, false on failure.
    boolean rollback(String txId); // Returns true on success, false on failure.
}
```

You don't need to implement the PSs themselves; you only need to interact with them through this interface. You can simulate PS behavior for testing.

**Bonus Challenges:**

*   **Recoverability:** Implement a mechanism to recover the TC's state after a crash. This might involve persisting transaction state to a durable storage.
*   **Two-Phase Commit (2PC) Optimization:** Explore ways to optimize the 2PC protocol, such as early voting or parallel execution.
*   **Deadlock Detection:** Implement a deadlock detection mechanism to identify and resolve deadlocks that may occur in the PSs.
*   **Implement a custom exception** for transaction failures that provides information about the reason for the failure, and the list of services which failed.

This problem requires a good understanding of distributed systems concepts, concurrency, and error handling. The solution should be well-structured, efficient, and robust. Good luck!
