## Question: Distributed Transaction Coordinator

**Question Description:**

You are tasked with designing and implementing a simplified, in-memory Distributed Transaction Coordinator (DTC) in Rust. This DTC is responsible for managing two-phase commit (2PC) transactions across multiple participating services (participants).

**System Architecture:**

Imagine a system where multiple services (participants) need to perform operations that must either all succeed or all fail together. The DTC acts as the central coordinator to ensure atomicity. Each participant will register with the DTC.

**Core Requirements:**

1.  **Transaction Management:** The DTC must be able to initiate, manage, and finalize transactions. Each transaction will be assigned a unique transaction ID (UUID).
2.  **Two-Phase Commit (2PC) Protocol:** Implement the 2PC protocol. This involves a "prepare" phase where the DTC asks all participants to prepare to commit, and a "commit" or "rollback" phase based on the responses from participants.
3.  **Participant Registration:** Participants must be able to register with the DTC, providing their address (e.g., a simple String identifier).
4.  **Prepare Phase:** The DTC sends a "prepare" message to all participants in a transaction. Participants respond with either "ACK" (prepared to commit) or "NAK" (cannot commit).
5.  **Commit/Rollback Phase:**
    *   If all participants respond with "ACK", the DTC sends a "commit" message to all participants.
    *   If any participant responds with "NAK", the DTC sends a "rollback" message to all participants.
6.  **Timeout Handling:** If a participant doesn't respond within a specified timeout (e.g., 5 seconds) during the prepare phase, the DTC should consider it a "NAK" and initiate a rollback.
7.  **Idempotency:** Participants must handle commit and rollback requests idempotently.  Receiving the same commit or rollback request multiple times should not cause any issues.
8.  **Concurrency:** The DTC must handle multiple concurrent transactions correctly.
9.  **Logging:** Implement basic logging for transaction state transitions, participant responses, and any errors. You can use `println!` for simplicity.

**Constraints:**

*   **In-Memory:** All data (transaction state, participant information) should be stored in memory.
*   **Simplified Communication:** You don't need to implement actual network communication.  Instead, simulate communication by having participants be represented by structs/enums and using function calls for sending and receiving messages.
*   **Error Handling:** Implement robust error handling.  Return appropriate error types when things go wrong (e.g., participant not found, transaction already completed).
*   **Performance:** While correctness is the primary goal, consider the performance implications of your design.  Minimize unnecessary locking and data copying.  The DTC should be able to handle a moderate number of concurrent transactions without significant performance degradation.
*   **Scalability:** While you don't need to build a fully scalable system, your design should be reasonably extensible.  Consider how you might adapt your design to handle a larger number of participants and transactions in the future.
*   **Resource Management:** The DTC should manage resources efficiently, preventing memory leaks or excessive CPU usage.

**Input/Output:**

The problem doesn't involve standard input/output.  Instead, you need to implement a set of functions/methods that allow you to:

*   Register participants.
*   Initiate a new transaction.
*   Simulate participant responses (ACK/NAK).
*   Check the final status of a transaction (committed/rolled back).

**Example Usage (Conceptual):**

```rust
// Assume DTC is an instance of your DTC implementation.

// Register participants
dtc.register_participant("service1".to_string());
dtc.register_participant("service2".to_string());

// Start a transaction
let transaction_id = dtc.start_transaction().unwrap();

// Simulate service1 acknowledging
dtc.participant_ack(transaction_id, "service1".to_string()).unwrap();

// Simulate service2 acknowledging
dtc.participant_ack(transaction_id, "service2".to_string()).unwrap();

// Wait for the transaction to complete (in a real system, this would be handled asynchronously)
// and then check the status.  For this example, you might need to add a function to
// explicitly drive the transaction to completion.
dtc.drive_transaction_completion(transaction_id).unwrap();

// Check the status
let status = dtc.get_transaction_status(transaction_id).unwrap();
assert_eq!(status, TransactionStatus::Committed);

```

**Evaluation Criteria:**

*   **Correctness:** Does your solution correctly implement the 2PC protocol and handle all the specified scenarios?
*   **Concurrency Safety:** Is your code thread-safe and able to handle multiple concurrent transactions without data corruption or race conditions?
*   **Error Handling:** Does your solution handle errors gracefully and provide informative error messages?
*   **Efficiency:** Is your solution reasonably efficient in terms of memory usage and CPU usage?
*   **Code Quality:** Is your code well-structured, readable, and maintainable?
*   **Completeness:** Does your solution address all the requirements outlined in the problem description?

This problem requires a good understanding of concurrency, distributed systems concepts, and careful attention to detail. Good luck!
