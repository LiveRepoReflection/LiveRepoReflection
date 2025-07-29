## Question: Distributed Transaction Manager

### Description

You are tasked with designing and implementing a simplified, distributed transaction manager for a system that manages reservations across multiple independent services. Think of it as booking resources like flights, hotels, and rental cars across different providers.

Each service exposes an API to reserve (tentatively book), confirm (make the reservation permanent), and cancel resources. A single transaction might involve reserving resources from several of these services.

Your transaction manager must ensure atomicity – either all reservations in a transaction are confirmed, or all are cancelled (rolled back). Consistency and Isolation are assumed to be handled by each individual service (database). The focus here is on implementing the **Durability** and **Atomicity** parts of the ACID properties in a distributed setting.

**Specifically:**

1.  **Participants:** Each service involved in a transaction is considered a participant. Each participant can either vote to commit or abort the transaction.

2.  **Coordinator:** Your transaction manager acts as the coordinator. It initiates and manages the transaction lifecycle.

3.  **Two-Phase Commit (2PC):** Implement the 2PC protocol to manage the distributed transaction. This involves:

    *   **Phase 1 (Prepare Phase):** The coordinator asks all participants to prepare to commit. Each participant tries to tentatively perform its part of the transaction and then votes to commit (Yes) or abort (No). The vote is sent back to the coordinator. Importantly, the participant must persist its tentative changes and vote to durable storage *before* replying to the coordinator. This ensures that even if the participant crashes before Phase 2, it can recover and still act according to its vote.
    *   **Phase 2 (Commit/Rollback Phase):**
        *   If *all* participants voted to commit, the coordinator sends a commit message to all participants. Each participant then permanently commits its changes.
        *   If *any* participant voted to abort, or if the coordinator doesn't receive a response from a participant within a timeout, the coordinator sends a rollback message to all participants. Each participant then rolls back its changes.

4.  **Fault Tolerance:** The coordinator must be able to handle participant failures *during* the transaction process. This includes:

    *   **Timeouts:** If a participant doesn't respond to a prepare request or a commit/rollback request within a reasonable time, the coordinator should consider it a failure and abort the transaction.
    *   **Recovery:** Consider the scenario where the coordinator crashes during the transaction (e.g., after sending prepare requests but before receiving all votes). How would you ensure that the transaction eventually completes consistently after the coordinator recovers? (Hint: persistent logging). For simplicity, assume a single coordinator instance; HA and failover are out of scope.

5.  **Logging:** Implement persistent logging for the coordinator to track the state of the transaction. This log should include:

    *   Transaction ID
    *   Participants involved
    *   Votes received from participants
    *   The final decision (Commit or Abort)

    This log is crucial for recovery in case of coordinator failure. Think about what information is essential to log at each stage of the 2PC protocol.

**Constraints and Requirements:**

*   **Concurrency:** The transaction manager should be thread-safe and handle concurrent transactions correctly.
*   **Optimization:** Minimize the number of messages exchanged between the coordinator and participants.
*   **Scalability:** While the solution does not need to handle a massive number of participants, design it with potential scalability in mind. Consider how your design would be affected by a larger number of participants.
*   **Durability:** Ensure that all critical states and decisions are persisted to disk to survive crashes. Use a simple file-based logging mechanism for this problem.
*   **Edge Cases:** Carefully consider various failure scenarios and edge cases, such as network partitions, participant crashes before voting, coordinator crashes at different phases of the 2PC, and message loss.

**Challenge:**

The major difficulty lies in correctly implementing the 2PC protocol with proper logging and recovery mechanisms. Ensuring that the system remains consistent even under various failure scenarios is a substantial challenge. The persistent logging and recovery logic requires careful consideration of what data to log and when, to allow the transaction manager to resume correctly from any point of failure. You will also need to design an efficient and thread-safe mechanism to manage concurrent transactions.
