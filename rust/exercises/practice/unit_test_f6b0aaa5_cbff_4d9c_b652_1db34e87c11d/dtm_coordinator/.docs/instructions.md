## Project Name

**Distributed Transaction Manager**

## Question Description

You are tasked with designing and implementing a simplified distributed transaction manager (DTM) in Rust. This DTM will be responsible for coordinating transactions across multiple independent services.

Imagine a system composed of various microservices, each managing its own database. A single logical transaction might require modifications across several of these services. The DTM ensures that either all services commit their changes, or all services roll back, maintaining data consistency.

**Requirements:**

1.  **Transaction Coordination:** Implement the Two-Phase Commit (2PC) protocol. The DTM acts as the coordinator, and the microservices act as participants.

2.  **Service Interaction:** Design a simple interface for microservices to interact with the DTM (e.g., using HTTP or gRPC; the choice impacts complexity). Services should be able to register with the DTM, prepare for a transaction, commit, and rollback.

3.  **Durability:** The DTM must be durable. Transaction logs should be persisted to disk to recover from crashes.  You need to consider what information needs to be persisted and how it should be structured.

4.  **Concurrency:** The DTM must handle concurrent transactions efficiently. Use appropriate locking mechanisms (consider potential deadlocks) and data structures to ensure thread safety and performance.

5.  **Error Handling:** Implement robust error handling, including timeouts, network failures, and participant failures.  The DTM should be able to detect and handle these failures gracefully.

6.  **Transaction States:** Maintain and manage transaction states (e.g., PREPARING, PREPARED, COMMITTED, ABORTED).

7.  **Optimization:** Design the DTM to minimize the number of network calls required to complete a transaction. Consider batching operations or using asynchronous communication.

**Constraints:**

*   **Number of Participants:** Support up to 100 participating services per transaction.
*   **Transaction Timeout:** Transactions should automatically roll back if they take longer than 60 seconds.
*   **Crash Recovery:**  The DTM should be able to recover to the correct state after a crash, based on its transaction logs.  Assume a single DTM instance; HA is out of scope.
*   **Scalability:** While not the primary focus, consider how your design could be scaled to handle a larger number of concurrent transactions.

**Edge Cases:**

*   A participant fails to respond to the PREPARE request.
*   A participant responds with an error during the PREPARE phase.
*   The DTM crashes after sending the PREPARE requests but before receiving all responses.
*   The DTM crashes after receiving all PREPARE responses but before sending the COMMIT/ROLLBACK requests.
*   A participant fails to respond to the COMMIT/ROLLBACK request.

**Evaluation Criteria:**

*   **Correctness:** Does the DTM correctly implement the 2PC protocol and ensure atomicity?
*   **Durability:** Can the DTM recover from crashes without losing transaction data?
*   **Concurrency:** Does the DTM handle concurrent transactions efficiently and without deadlocks?
*   **Performance:** Does the DTM minimize network latency and resource usage?
*   **Code Quality:** Is the code well-structured, readable, and maintainable?
*   **Error Handling:** Does the DTM handle various error scenarios gracefully?
*   **Completeness:** Does the implementation address all the requirements and constraints?

This problem requires a strong understanding of distributed systems concepts, concurrency, and Rust's error handling and memory management features.  You will need to make design choices that balance consistency, performance, and fault tolerance.  Good luck!
