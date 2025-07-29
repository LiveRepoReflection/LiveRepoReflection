## Problem: Distributed Transaction Manager

**Problem Description:**

You are tasked with designing and implementing a simplified distributed transaction manager (DTM) for a microservices architecture.  Imagine a system where multiple independent services (databases, message queues, etc.) need to participate in a single, atomic transaction.  Your DTM should ensure ACID properties (Atomicity, Consistency, Isolation, Durability) even if some services fail during the transaction.

The system operates with the following assumptions:

*   **Two-Phase Commit (2PC):**  Implement a simplified 2PC protocol.
*   **Coordinator and Participants:** One service acts as the coordinator, initiating and managing the transaction. Other services are participants, providing resources and performing actions within the transaction.
*   **Communication:** Services communicate using a reliable message queue (you don't need to implement the message queue itself; assume you have a function `sendMessage(destinationService, message)` and `receiveMessage()` that work reliably).
*   **Transaction IDs:** Each transaction is assigned a unique transaction ID (UUID).
*   **Logging:** Each service maintains a local transaction log to record transaction states and actions.  This log is persistent across restarts.
*   **Timeout:**  Introduce timeouts for each phase to handle unresponsive services.

**Your Task:**

Implement the core logic for both the coordinator and participant services within the DTM.

**Coordinator Responsibilities:**

1.  **Initiate Transaction:**  Assign a unique transaction ID and send a "PREPARE" message to all participants involved in the transaction. The PREPARE message includes the transaction ID.
2.  **Collect Votes:**  Wait for responses (votes) from all participants. Participants can vote "COMMIT" or "ABORT."
3.  **Global Decision:**
    *   If *all* participants vote "COMMIT", send a "GLOBAL_COMMIT" message to all participants.
    *   If *any* participant votes "ABORT" or if a participant times out before responding, send a "GLOBAL_ABORT" message to all participants.
4.  **Completion:**  After sending the global decision, wait for acknowledgments from all participants indicating that they have committed or aborted the transaction.
5.  **Timeout Handling:** If the coordinator does not receive a vote or acknowledgement within a specified timeout, treat the participant as having voted to abort.

**Participant Responsibilities:**

1.  **Receive PREPARE:** Upon receiving a "PREPARE" message, perform the necessary actions to prepare for the transaction (e.g., acquire locks, write data to a temporary location, etc.). Log this "prepared" state to the local transaction log with the transaction ID.
2.  **Vote:**  If preparation is successful, vote "COMMIT" to the coordinator. Otherwise, vote "ABORT."
3.  **Receive Global Decision:**
    *   If "GLOBAL_COMMIT" is received, permanently commit the changes and send an acknowledgment to the coordinator. Log the "committed" state.
    *   If "GLOBAL_ABORT" is received, roll back any changes made during preparation and send an acknowledgment to the coordinator. Log the "aborted" state.
4.  **Recovery:** If the service crashes and restarts, upon restart, check the local transaction log. If there is an unfinished transaction (prepared but not committed/aborted), contact the coordinator (or a designated recovery service – you can assume it exists) to determine the global decision and proceed accordingly.
5.  **Timeout Handling:** If the participant does not receive a global decision within a specified timeout after voting, contact the coordinator (or the recovery service) to determine the global decision.

**Constraints and Requirements:**

*   **Error Handling:** Implement proper error handling for network failures, service crashes, and invalid messages.
*   **Concurrency:** The DTM should be able to handle multiple concurrent transactions.
*   **Durability:**  Transaction logs must be durable (written to disk) to survive service restarts.
*   **Efficiency:** Minimize the number of messages exchanged between services.  Consider the performance implications of your data structures and algorithms.  The system needs to handle a high volume of transactions with low latency.
*   **Scalability:** The design should be scalable to a large number of participants. Consider strategies for handling a growing number of services and transactions. (While you don't need to implement scaling features, your design should be conducive to scaling.)
*   **Deadlock Prevention:** Address the potential for deadlocks among participants.

**Input/Output:**

Since this is a system design-oriented problem, there is no specific input/output format. Your solution will primarily involve implementing the logic for the coordinator and participant services. You need to define the data structures for transaction logs, messages, and participant states.

**Evaluation Criteria:**

Your solution will be evaluated based on the following criteria:

*   **Correctness:**  Does the DTM correctly implement the 2PC protocol and ensure ACID properties?
*   **Completeness:** Does the solution address all the requirements outlined in the problem description?
*   **Robustness:**  Does the DTM handle errors and failures gracefully?
*   **Efficiency:**  Is the implementation efficient in terms of message exchange and resource utilization?
*   **Scalability:** Is the design scalable to a large number of participants and transactions?
*   **Code Quality:**  Is the code well-structured, readable, and maintainable?
*   **Deadlock Handling:** Does the solution address the potential for deadlocks?

This problem requires a strong understanding of distributed systems concepts, concurrency, and data structures. Good luck!
