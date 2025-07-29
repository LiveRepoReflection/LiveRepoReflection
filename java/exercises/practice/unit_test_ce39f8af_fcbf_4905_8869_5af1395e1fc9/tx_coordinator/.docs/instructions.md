## Problem: Distributed Transaction Coordinator

**Description:**

You are tasked with designing and implementing a simplified distributed transaction coordinator for a microservice architecture.  Imagine a scenario where multiple microservices (databases, message queues, external APIs, etc.) need to participate in a single, atomic transaction.  Your coordinator will orchestrate these services to either commit or rollback the entire transaction as a unit.

**Simplified Context:**

*   **Participants:** Represented by unique String identifiers. These are the individual services involved in the transaction.
*   **Transaction ID:** Each transaction is assigned a unique String identifier.
*   **Two-Phase Commit (2PC) Protocol:** Your coordinator will implement a simplified version of the 2PC protocol.

**Workflow:**

1.  **Initiation:** A client requests a new transaction with a set of participating services (Participants).
2.  **Prepare Phase:** The coordinator sends a "prepare" message to each participant.  Each participant must respond with either "vote_commit" or "vote_rollback".  The prepare phase has a *strict timeout*. If a participant doesn't respond within the timeout, it's considered a "vote_rollback".  The coordinator should handle potential network failures or unresponsive services gracefully.
3.  **Commit/Rollback Phase:**
    *   If *all* participants vote to commit, the coordinator sends a "commit" message to all participants.
    *   If *any* participant votes to rollback (or times out), the coordinator sends a "rollback" message to all participants.
4.  **Completion:** After sending the commit/rollback message, the coordinator considers the transaction complete. Participants are expected to eventually execute the commit/rollback decision.

**Your Task:**

Implement the `TransactionCoordinator` class with the following methods:

*   `String beginTransaction(Set<String> participants)`:  Starts a new transaction, assigning a unique ID and registering the participants.  Returns the transaction ID.
*   `TransactionResult executeTransaction(String transactionId, Map<String, Function<String, String>> participantActions)`: Executes the transaction using the 2PC protocol. This function simulates the interaction with the participants. The `participantActions` map contains functions that represent each participant's behavior when receiving "prepare", "commit", or "rollback" messages. These functions take the message string as input and return a string representing the participant's response (e.g., "vote_commit", "vote_rollback"). Participants *might* throw exceptions, which should be treated as "vote_rollback".  The function should return a `TransactionResult` enum indicating the overall transaction outcome (COMMIT or ROLLBACK).
*   `enum TransactionResult { COMMIT, ROLLBACK }`

**Constraints & Requirements:**

*   **Concurrency:** The `TransactionCoordinator` must be thread-safe. Multiple transactions may be initiated and executed concurrently.
*   **Timeout:** Implement a timeout mechanism for the prepare phase.  A reasonable timeout value (e.g., 5 seconds) should be used.
*   **Logging:** Include basic logging to track the transaction progress (e.g., transaction start, votes, decision).
*   **Idempotency (Optional but highly recommended):**  Consider how you would make the commit/rollback operations idempotent in a real-world scenario (i.e., handling duplicate commit/rollback messages).  You don't need to *implement* idempotency, but describe in comments how you would approach it.
*   **Scalability (Design Consideration):** Although you don't need to implement distributed coordination in this exercise, consider how your design could be scaled to handle a large number of transactions and participants. Think about the bottlenecks and how to address them (e.g., sharding, distributed consensus).

**Participant Simulation (Important):**

The `participantActions` map simulates the behavior of the real microservices.  Each key in the map is a participant ID, and the corresponding value is a `Function<String, String>` that represents how that participant will respond to a given message ("prepare", "commit", "rollback"). You will *not* be making real network calls.  This allows you to test different scenarios, including:

*   All participants vote to commit.
*   One or more participants vote to rollback.
*   A participant throws an exception during the prepare phase (simulating an error).
*   A participant doesn't respond within the timeout.

**Success Criteria:**

Your solution will be judged based on:

*   Correctness:  Accurate implementation of the 2PC protocol.
*   Thread Safety:  Handling concurrent transactions without data corruption.
*   Timeout Handling:  Properly handling timeouts in the prepare phase.
*   Error Handling:  Gracefully handling exceptions and network failures (simulated by exceptions in `participantActions`).
*   Code Clarity:  Well-structured and readable code.
*   Design Considerations:  Thoughtful consideration of idempotency and scalability.

This problem requires a good understanding of concurrent programming, distributed systems concepts, and error handling. Good luck!
