## Problem: Distributed Transaction Coordinator

**Problem Description:**

You are tasked with designing and implementing a simplified, yet robust, distributed transaction coordinator (DTC) for a microservices architecture.  Imagine a scenario where multiple microservices need to update their local databases as part of a single, atomic transaction. If any service fails to update its database, the entire transaction must be rolled back across all participating services.

Your DTC must manage the two-phase commit (2PC) protocol to ensure atomicity and consistency across these distributed transactions.  The participating microservices will interact with your DTC through a defined API.

**Specifically, you need to implement the following:**

1.  **Coordinator:** A central component that orchestrates the distributed transaction. It receives requests to initiate transactions, tracks participating services, and manages the commit/rollback process.

2.  **Transaction ID Generation:** The coordinator must generate unique transaction IDs for each new transaction.

3.  **Participant Registration:** Microservices participating in a transaction must register themselves with the coordinator, providing their service ID and a rollback mechanism (e.g., an endpoint to call for rollback).

4.  **Prepare Phase:**  The coordinator sends a "prepare" message to each registered participant. Participants must attempt to perform their local update and respond with either "vote-commit" or "vote-abort".  The prepare phase must have a timeout mechanism. If a participant doesn't respond within the timeout, the coordinator should assume "vote-abort".

5.  **Commit/Rollback Phase:**
    *   If all participants vote to commit, the coordinator sends a "commit" message to all participants.
    *   If any participant votes to abort, or if a timeout occurs during the prepare phase, the coordinator sends a "rollback" message to all participants.
    *   Participants must acknowledge the "commit" or "rollback" message. The coordinator should retry sending these messages a limited number of times if acknowledgements are not received within a reasonable timeframe.

6.  **Failure Handling:** The coordinator must be resilient to failures.  Implement a basic logging mechanism to persist transaction state (e.g., transaction ID, participants, votes, and final decision) to a file. Upon restart, the coordinator should attempt to recover any in-flight transactions from the log file. This recovery should involve re-sending prepare/commit/rollback messages as necessary based on the persisted state.

7.  **API:** Define a clear API (using function signatures and data structures) for interacting with the coordinator. This API should include:
    *   `BeginTransaction()`: Initiates a new transaction and returns a transaction ID.
    *   `RegisterParticipant(transaction_id, service_id, rollback_endpoint)`: Registers a service as a participant in a transaction.
    *   `ReportVote(transaction_id, service_id, vote)`:  A participant reports its vote (commit or abort) to the coordinator.

**Constraints:**

*   **Concurrency:** The coordinator must be thread-safe and handle multiple concurrent transactions.
*   **Performance:** The coordinator should be designed to minimize latency and maximize throughput.  Consider the impact of logging on performance.
*   **Scalability:** While a fully scalable solution is not required, think about the design choices that would impact scalability in a real-world distributed system.
*   **Logging:**  Logging must be implemented in a way that avoids data corruption if the process terminates mid-write.
*   **Timeout Handling:** Implement reasonable timeout values for the prepare phase and acknowledgement of commit/rollback messages.  Make these timeout values configurable.
*   **Error Handling:** The coordinator must handle various error conditions gracefully, such as invalid transaction IDs, unregistered participants, and network failures.
*   **Memory Management:**  Pay attention to memory leaks, especially when handling errors and timeouts.

**Input:**

The input will be a series of API calls to the DTC, simulating microservices participating in transactions. The format and specific values of the API calls will be provided during testing.

**Output:**

The output will be the status of the transactions and the actions taken by the DTC (e.g., "Transaction committed", "Transaction rolled back", "Participant timed out", "Retrying commit message", etc.). The output format will be specified during testing. The output is primarily for verification and debugging.

**Evaluation Criteria:**

*   **Correctness:** Does the DTC correctly implement the 2PC protocol and ensure atomicity across all participating services?
*   **Resilience:** Can the DTC recover from failures and continue processing transactions?
*   **Performance:** Is the DTC efficient in terms of latency and throughput?
*   **Code Quality:** Is the code well-structured, readable, and maintainable?
*   **Error Handling:** Does the DTC handle errors gracefully and provide informative error messages?

This problem requires a strong understanding of distributed systems concepts, concurrency, and error handling.  It also tests your ability to design and implement a complex system with multiple interacting components. Good luck!
