## Problem Title: Distributed Transaction Coordinator

### Question Description

You are tasked with designing and implementing a simplified distributed transaction coordinator (DTC) for a microservice architecture. The system consists of multiple independent services that need to perform atomic operations spanning across their individual databases.

The goal is to ensure that either all operations within a transaction succeed (commit), or all operations are rolled back in case of a failure, maintaining data consistency across the system.

Here's a simplified overview of how the DTC should work:

1.  **Transaction Initiation:** A client initiates a distributed transaction by contacting the DTC. The DTC assigns a unique transaction ID (TXID) to this transaction.

2.  **Participant Registration:** As the client invokes operations on various microservices, each microservice that participates in the transaction registers itself with the DTC, providing the TXID. Along with the registration, it provides two functions (or endpoints): a `prepare` function and a `commit/rollback` function.

3.  **Prepare Phase:** When the client requests the DTC to commit the transaction, the DTC initiates the prepare phase. It sends a `prepare` request to each registered participant. Each participant then attempts to perform its operation (e.g., update its database) and responds to the DTC with either a "prepared" (success) or "abort" (failure) status.

4.  **Commit or Rollback Phase:**
    *   If all participants respond with "prepared," the DTC initiates the commit phase by sending a `commit` request to each participant.
    *   If any participant responds with "abort," or if the DTC times out waiting for a response from any participant, the DTC initiates the rollback phase by sending a `rollback` request to each participant.

5.  **Completion:** Each participant executes the `commit` or `rollback` operation and acknowledges the completion to the DTC. The DTC then informs the client about the final outcome of the transaction (committed or rolled back).

**Your Task:**

Implement the core logic of the Distributed Transaction Coordinator (DTC) service in Python. The DTC should be able to:

*   Assign unique transaction IDs.
*   Register participants (microservices) for a given transaction.
*   Orchestrate the prepare phase, collecting responses from participants.
*   Orchestrate the commit or rollback phase based on the outcome of the prepare phase.
*   Handle timeouts during the prepare phase (if a participant doesn't respond within a reasonable time).
*   Ensure idempotency: participants should be able to handle multiple prepare/commit/rollback requests for the same TXID.

**Constraints & Considerations:**

*   **Concurrency:** The DTC must handle multiple concurrent transactions.
*   **Error Handling:** Implement robust error handling, including dealing with unresponsive participants and unexpected exceptions.
*   **Idempotency:**  Ensure commit and rollback operations are idempotent. Services might receive multiple commit or rollback requests.
*   **Timeouts:** Implement timeouts for the prepare phase. If a participant doesn't respond within a specified time, the transaction should be rolled back.
*   **Logging:** Implement basic logging to track the progress of transactions and any errors encountered.
*   **Scalability:** While you don't need to implement full horizontal scaling, design your solution with scalability in mind.  Consider how you might distribute the load in a real-world scenario.
*   **Communication:**  Assume a reliable message queue or RPC mechanism (e.g., gRPC, RabbitMQ, etc.) exists for communication between the DTC and the participants. You don't need to implement the actual communication layer, but your DTC should be designed to interact with it. You can simulate this communication with function calls or mock objects for testing.
*   **Durability:**  Assume the underlying message queue or RPC mechanism provides at-least-once delivery guarantees, so messages will eventually be delivered even if services crash.

**Input/Output:**

The specific input/output format is up to you, but your DTC should expose the following functionalities:

*   `begin_transaction()`: Returns a unique TXID.
*   `register_participant(txid, prepare_func, commit_rollback_func)`: Registers a participant with its prepare and commit/rollback functions (or endpoints).
*   `commit_transaction(txid)`: Initiates the commit process for a given transaction.

**Example Usage (Conceptual):**

```python
dtc = DistributedTransactionCoordinator()

txid = dtc.begin_transaction()

# Microservice A registers
dtc.register_participant(txid, microservice_a_prepare, microservice_a_commit_rollback)

# Microservice B registers
dtc.register_participant(txid, microservice_b_prepare, microservice_b_commit_rollback)

# Client requests commit
result = dtc.commit_transaction(txid) # result will be "committed" or "rolled_back"
```

**Bonus Challenges:**

*   Implement a recovery mechanism to handle DTC crashes. Upon restart, the DTC should be able to recover the state of in-flight transactions and continue the commit/rollback process.
*   Implement deadlock detection.  If two or more transactions are waiting for each other, detect the deadlock and automatically roll back one of the transactions.
*   Support nested transactions.

This problem requires a good understanding of distributed systems principles, concurrency, and error handling. The difficulty lies in the complexity of coordinating operations across multiple services while ensuring atomicity and handling potential failures. Good luck!
