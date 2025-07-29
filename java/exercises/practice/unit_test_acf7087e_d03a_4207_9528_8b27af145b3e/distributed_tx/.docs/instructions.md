## Question: Distributed Transaction Manager

**Problem Description:**

You are tasked with designing and implementing a simplified, distributed transaction manager (DTM) for a microservices architecture.  Imagine a system where multiple independent services (databases, message queues, etc.) need to participate in a single atomic transaction.  Your DTM will coordinate the transaction across these services, ensuring either all services commit their changes, or all rollback, even in the face of failures.

**System Design and Constraints:**

1.  **Two-Phase Commit (2PC):** Implement the 2PC protocol as the core mechanism for coordinating distributed transactions.  The DTM acts as the coordinator, and the microservices are the participants.

2.  **Participants (Microservices):**  Assume the participants have a well-defined API for transaction management:
    *   `prepare(transactionId)`:  The participant attempts to prepare for the commit.  It performs necessary checks (e.g., resource availability, data validation) and reserves resources.  Returns `true` if prepared successfully, `false` otherwise.
    *   `commit(transactionId)`:  The participant commits the transaction.  This operation is guaranteed to succeed if `prepare()` returned `true`.
    *   `rollback(transactionId)`: The participant rolls back the transaction, releasing any reserved resources. This operation is guaranteed to succeed.

3.  **DTM Coordinator:** The DTM will have the following functionalities:
    *   `begin()`: Starts a new transaction and returns a unique transaction ID.
    *   `enlist(transactionId, participant)`:  Adds a participant (microservice) to the transaction.
    *   `commit(transactionId)`: Initiates the 2PC protocol.  First, sends a `prepare()` request to all participants. If all participants successfully prepare, the DTM sends a `commit()` request to all participants. Otherwise, the DTM sends a `rollback()` request to all participants.
    *   `rollback(transactionId)`: Rolls back the transaction by sending a `rollback()` request to all enlisted participants. This is typically called when something goes wrong before the `commit` phase.

4.  **Concurrency:**  The DTM must handle concurrent transaction requests.

5.  **Failure Handling:**
    *   **Participant Failure:** If a participant fails to respond to a `prepare()` request within a reasonable timeout, the DTM must assume the participant has failed to prepare and initiate a rollback of the entire transaction.
    *   **DTM Failure (Simplified):**  For simplicity, you don't need to handle the DTM crashing mid-transaction. Assume the DTM is highly available.

6.  **Optimization:**
    *   **Parallelism:** Implement the `prepare()`, `commit()`, and `rollback()` phases using concurrent goroutines to improve performance.

7.  **Data Structures:** Choose appropriate data structures for managing transaction states, participant lists, and concurrency control.

8.  **Scalability:** While a full-blown distributed system is beyond the scope, consider how your design would scale to handle a large number of concurrent transactions and participants.

**Requirements:**

*   Implement the `DTM` class with the methods described above.
*   Your code should be well-structured, readable, and maintainable.
*   Consider the trade-offs between different design choices and document your reasoning.
*   Your solution should be efficient and scalable.

**Bonus (for extra difficulty):**

*   **Idempotency:**  Make the `commit()` and `rollback()` operations idempotent.  This is important because network issues might cause the DTM to send the same request multiple times.  Participants should be able to handle duplicate requests without adverse effects.
*   **Recovery Log (Conceptual):** Describe how you would implement a recovery log to handle DTM failures. What information would you need to log, and how would you use it to recover the state of ongoing transactions after a crash?  (No need to implement the logging mechanism itself.)

This problem requires a solid understanding of distributed systems concepts, concurrency, and data structures.  It also challenges you to think about failure handling and optimization in a real-world scenario. Good luck!
