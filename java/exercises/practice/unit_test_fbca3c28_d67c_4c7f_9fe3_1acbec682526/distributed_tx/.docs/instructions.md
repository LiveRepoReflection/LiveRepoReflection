## Question: Distributed Transaction Manager

### Description

You are tasked with designing and implementing a simplified, in-memory distributed transaction manager for a microservice architecture. This system will be responsible for ensuring ACID (Atomicity, Consistency, Isolation, Durability) properties across multiple independent services when a single business operation requires changes to data in several of them.

Assume you have a set of microservices, each managing its own data and accessible via synchronous (HTTP) calls. Your transaction manager must orchestrate a 2-Phase Commit (2PC) protocol to guarantee that either all services commit their changes or all roll back, even in the face of failures.

**Simplified Architecture:**

*   **Transaction Manager (TM):** Your component.  Manages transactions, coordinates services, and maintains transaction logs.
*   **Microservices (MS):** Independent services with their own data stores. They expose endpoints to prepare, commit, and rollback transactions.  Assume these services can execute provided logic, but they don't have built-in transaction coordination.

**Requirements:**

1.  **Transaction Initiation:**
    *   Provide an API to initiate a new distributed transaction with a unique transaction ID (UUID). The client specifies a list of microservices involved in the transaction.

2.  **2-Phase Commit Protocol:**

    *   **Phase 1 (Prepare):**
        *   The TM sends a `prepare` request to each participating microservice.
        *   Each microservice attempts to perform the operation within a local transaction. If successful, it reserves the resources and returns `prepared` (or `OK`). If it fails (e.g., due to data conflict, validation failure), it returns `abort` (or `Error`).
        *   The TM collects the responses from all microservices.

    *   **Phase 2 (Commit/Rollback):**
        *   If all microservices responded with `prepared`, the TM sends a `commit` request to all microservices.
        *   If any microservice responded with `abort`, or if the TM timed out waiting for a response, the TM sends a `rollback` request to all microservices.
        *   Each microservice then commits or rolls back the changes based on the TM's request.

3.  **Concurrency and Isolation:**
    *   Implement basic concurrency control to handle multiple concurrent transactions. Avoid deadlocks.
    *   Assume microservices handle internal isolation. The TM focuses on the global atomicity.

4.  **Failure Handling and Durability:**

    *   **Crash Recovery:** If the TM crashes during the 2PC protocol, it should be able to recover its state from a transaction log and complete the transaction (either commit or rollback). Implement a basic, in-memory transaction log.
    *   **Timeout:** Implement timeouts for communication with microservices. If a microservice does not respond within a reasonable time, treat it as a failure and initiate a rollback.

5.  **API:**
    *   `begin(List<Microservice> services) -> TransactionID` : Starts a transaction, returns the transaction ID.
    *   `commit(TransactionID transactionID) -> boolean` : Commits the transaction. Returns `true` if successful, `false` otherwise.
    *   `rollback(TransactionID transactionID) -> boolean` : Rolls back the transaction. Returns `true` if successful, `false` otherwise.
    *   (Internal) `handlePrepareResponse(TransactionID transactionID, Microservice service, Response response) -> void` :  Called when a microservice responds to the prepare request.
    *   (Internal) `recover() -> void` :  Called on TM startup to recover incomplete transactions from the log.

**Constraints:**

*   **Microservice Interaction:** Assume you have a mock `Microservice` class (provided) that simulates a microservice with `prepare()`, `commit()`, and `rollback()` methods. These methods can randomly succeed or fail to simulate real-world scenarios.  They also have a latency between 0-100ms. You cannot modify the `Microservice` class.
*   **Scalability:**  While a fully scalable TM is beyond the scope, consider the design implications for larger systems (e.g., sharding, distributed logging). Briefly discuss these in comments in your code.
*   **Simplicity:** Focus on correctness and clarity over extreme optimization.

**Assumptions:**

*   The network is unreliable. Messages can be lost or delayed.
*   Microservices are independent and can fail independently.
*   Microservices are idempotent for commit and rollback operations (i.e., they can be called multiple times without adverse effects).
*   No nested transactions.

**Evaluation Criteria:**

*   Correctness: Does the TM guarantee atomicity across microservices?
*   Failure Handling: Does the TM correctly handle microservice failures and TM crashes?
*   Concurrency: Does the TM handle concurrent transactions correctly without deadlocks?
*   Code Quality: Is the code well-structured, readable, and maintainable?
*   Design Considerations: Does the solution demonstrate an understanding of the challenges in building a distributed transaction manager?

This problem requires a solid understanding of distributed systems concepts, concurrency, and failure handling. Good luck!
