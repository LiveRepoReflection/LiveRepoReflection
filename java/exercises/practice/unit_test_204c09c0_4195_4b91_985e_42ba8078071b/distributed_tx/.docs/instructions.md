## Problem Title: Distributed Transaction Manager

### Problem Description

You are tasked with designing and implementing a simplified, in-memory Distributed Transaction Manager (DTM) for a microservices architecture. This DTM will coordinate transactions across multiple services to ensure atomicity, consistency, isolation, and durability (ACID) properties.

Imagine a scenario where you have multiple independent services (e.g., `InventoryService`, `PaymentService`, `NotificationService`). A single business operation (e.g., placing an order) might require updates to multiple services. To ensure data consistency, these updates need to be performed within a distributed transaction.

Your DTM will be responsible for the following:

1.  **Transaction Initiation:** A client initiates a distributed transaction by contacting the DTM. The DTM generates a unique transaction ID (TXID).
2.  **Participant Registration:** Each service involved in the transaction registers itself as a participant with the DTM, providing its transaction-specific action endpoint (URL or method reference) to commit and rollback its changes.
3.  **Two-Phase Commit (2PC) Protocol:**
    *   **Phase 1 (Prepare):** Once all participants have registered and the client signals the transaction to proceed, the DTM initiates the prepare phase. It sends a "prepare" request to each participant. Each participant attempts to perform its local operation, logs the changes it *would* make (the "redo" and "undo" logs), and responds to the DTM with either "prepared" (if successful) or "abort" (if an error occurred).
    *   **Phase 2 (Commit/Rollback):** If all participants respond with "prepared", the DTM initiates the commit phase. It sends a "commit" request to each participant. Each participant applies its previously logged changes and responds with "committed". If any participant responded with "abort" in the prepare phase, the DTM initiates the rollback phase, sending a "rollback" request to each participant. Each participant reverts its state using its undo logs and responds with "rolled back".
4.  **Transaction Completion:** Once all participants have either committed or rolled back, the DTM marks the transaction as completed and informs the client.

**Constraints & Requirements:**

*   **Concurrency:** The DTM must be thread-safe and handle concurrent transaction requests.
*   **Idempotency:**  Participants must handle commit/rollback requests idempotently.  The DTM might send the same request multiple times due to network issues.
*   **Timeout:**  The DTM should implement timeouts for participant responses in the prepare phase. If a participant does not respond within a specified timeout, the DTM should consider the participant as having aborted.
*   **Failure Handling:** The DTM must handle service failures. If a participant fails after sending "prepared" but before receiving the commit/rollback request, the DTM should retry sending the commit/rollback request until the participant recovers or a maximum retry count is reached.
*   **Logging:** The DTM itself should log all significant events (transaction initiation, participant registration, prepare requests, commit requests, rollback requests, participant responses, timeouts, failures, transaction completion) for debugging and auditing purposes.
*   **Optimization:** Minimize the latency of the 2PC protocol. Consider strategies such as asynchronous communication where applicable.
*   **Scalability:** While this is an in-memory implementation, consider how the design could be extended to handle a large number of concurrent transactions and participants in a distributed environment (e.g., using a distributed consensus algorithm for DTM state management).
*   **Data Structure Choice:** Carefully select appropriate data structures for storing transaction metadata, participant information, and logs to ensure efficiency and scalability. Consider the trade-offs between different data structures (e.g., HashMap vs. ConcurrentHashMap).

**Input:**

The problem does not involve direct input reading from standard input. The DTM will be used programmatically by other services. The key input is the registration of participants and the signal to initiate the 2PC protocol.

**Output:**

The problem does not involve direct output to standard output. The DTM's success is measured by its ability to correctly coordinate distributed transactions and maintain data consistency across services, as well as its ability to handle failures and timeouts gracefully. Logging is crucial for verification.

**Judging Criteria:**

Your solution will be judged based on the following criteria:

*   **Correctness:** Does the DTM correctly implement the 2PC protocol, ensuring atomicity and consistency?
*   **Robustness:** Does the DTM handle concurrency, timeouts, and service failures gracefully?
*   **Efficiency:** Is the DTM optimized for low latency?
*   **Scalability (Design):** Is the design scalable to handle a large number of concurrent transactions and participants?
*   **Code Quality:** Is the code well-structured, readable, and maintainable? Is it properly documented?
*   **Logging:** Are all significant events logged appropriately?
