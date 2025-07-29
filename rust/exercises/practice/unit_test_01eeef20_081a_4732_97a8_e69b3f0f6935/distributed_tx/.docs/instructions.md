## Problem: Distributed Transaction Coordinator

### Description

You are tasked with building a simplified, yet robust, distributed transaction coordinator (DTC) service. This service is responsible for ensuring the atomicity of operations across multiple independent services (participants). In a distributed system, operations are often performed across multiple services, and it is crucial that these operations either all succeed (commit) or all fail (rollback) together, maintaining data consistency.

Your DTC will manage transactions involving a set of participant services. Each participant can either vote to commit or vote to abort the transaction. The DTC collects these votes and makes a final decision: commit if all participants vote to commit, and abort otherwise.

**System Design Aspects:**

1.  **Participants:** Assume an arbitrary number of participant services. Each participant is identified by a unique string ID. Participants are independent and can fail.
2.  **Two-Phase Commit (2PC):** Implement a simplified version of the 2PC protocol.
    *   **Phase 1 (Voting Phase):** The DTC sends a "prepare" message to all participants. Each participant performs its local operations tentatively and votes either "commit" or "abort".
    *   **Phase 2 (Commit/Rollback Phase):** If all participants vote to commit, the DTC sends a "commit" message to all participants. If any participant votes to abort, the DTC sends a "rollback" message to all participants. Participants then finalize their local operations (commit or rollback) accordingly.
3.  **Fault Tolerance:** The DTC and participants can crash at any point during the transaction. You need to handle these failures gracefully. Specifically, you must ensure that:
    *   If the DTC crashes before sending the final decision (commit or rollback), upon recovery, it should replay its log and resume the transaction from the last known state.
    *   If a participant crashes before voting, it should rollback its tentative operations upon recovery.
    *   If a participant crashes after voting to commit but before receiving the final decision, it should remain in a prepared state upon recovery and wait for the DTC's decision.
    *   If a participant crashes after receiving the final decision (commit or rollback), it should complete the operation on recovery.
4.  **Concurrency:** Multiple transactions can be initiated concurrently. The DTC must handle these transactions in a thread-safe manner.
5.  **Communication:** You don't need to implement the actual network communication. Instead, simulate communication using in-memory channels (e.g., `mpsc` in Rust). Assume that messages can be lost or delayed.
6.  **Logging:** Implement a simple logging mechanism to persist the DTC's state. This log should be used for recovery after a crash.

**Constraints and Requirements:**

*   **Performance:** The DTC should be able to handle a large number of concurrent transactions efficiently.
*   **Scalability:** The design should be scalable to a large number of participants.
*   **Correctness:** The solution must guarantee atomicity, consistency, isolation, and durability (ACID) properties for all transactions.
*   **Error Handling:** The solution must handle various error conditions gracefully, such as network failures, participant failures, and invalid input.
*   **Concurrency Safety:** The DTC must be thread-safe to handle concurrent transactions.
*   **Recovery:** The DTC and participants must be able to recover from crashes and resume transactions from the last known state.
*   **Resource Management:** The DTC should manage its resources efficiently to avoid memory leaks and other resource-related issues.

**Input:**

Your DTC service will receive a stream of transaction requests. Each request will specify a unique transaction ID and a list of participant IDs.

**Output:**

Your DTC service should output the outcome of each transaction (commit or abort) and any error messages.

**Challenge:**

Design and implement a robust and efficient DTC service in Rust that meets the above requirements. Pay close attention to fault tolerance, concurrency, and performance. Consider the trade-offs between different design choices and choose the best approach for this scenario.
