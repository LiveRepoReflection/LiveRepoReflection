## Question: Distributed Transaction Manager

### Question Description

You are tasked with designing and implementing a simplified, distributed transaction manager (DTM) for a microservices architecture. This DTM will ensure atomicity and consistency across multiple services during a transaction.

**Scenario:**

Imagine an e-commerce platform where placing an order involves multiple services:

1.  **Inventory Service:** Checks and reserves the required quantity of each item in the order.
2.  **Payment Service:** Charges the customer's credit card.
3.  **Order Service:** Creates the order record in the database.
4.  **Shipping Service:** Schedules the shipment of the order.

All these services must either succeed or fail together to maintain data integrity.

**Requirements:**

1.  **Transaction Coordination:** Implement a central DTM service that orchestrates transactions across these services using the Two-Phase Commit (2PC) protocol. The DTM should act as the coordinator, and the Inventory, Payment, Order, and Shipping services should act as participants.

2.  **2PC Protocol Implementation:** Implement the Prepare (Phase 1) and Commit/Rollback (Phase 2) phases of the 2PC protocol.

    *   **Prepare Phase:** The DTM sends a "prepare" request to all participating services. Each service attempts to perform its local transaction and responds with either a "vote commit" or a "vote abort."
    *   **Commit/Rollback Phase:** If all services vote commit, the DTM sends a "commit" request to all participants. If any service votes abort, the DTM sends a "rollback" request to all participants.

3.  **Idempotency:** Ensure that all operations performed by each service are idempotent. This is crucial to handle potential network failures and retries.  Each service should be able to handle duplicate Prepare, Commit, and Rollback requests without adverse effects.

4.  **Failure Handling:** Implement mechanisms to handle various failure scenarios:

    *   **Service Unavailability:** The DTM should be able to handle situations where one or more services are temporarily unavailable during the transaction.  Consider timeouts and retry mechanisms.
    *   **DTM Failure:** The DTM should be designed to recover from failures.  Upon recovery, it should be able to determine the status of in-flight transactions and complete them accordingly. Persistence of transaction logs is required.
    *   **Network Partitions:**  Consider the impact of network partitions on the 2PC protocol and implement strategies to mitigate potential inconsistencies. (A full-blown Paxos/Raft implementation is not required, but demonstrate awareness of the issue).

5.  **Scalability:** The DTM should be designed to handle a large number of concurrent transactions. Consider using appropriate data structures and concurrency control mechanisms.

6.  **Transaction Logging:** Implement transaction logging to track the progress of each transaction and enable recovery in case of DTM failure.  Logs should include transaction ID, participants involved, and the current state of the transaction.

7.  **Optimistic Concurrency Control:** Assume each service is using optimistic concurrency control.  Services should include a version number or timestamp with their updates.  The DTM should handle conflict resolution if a service's data has changed since the Prepare phase.

**Input:**

Your solution will receive a stream of transaction requests. Each request will contain:

*   A unique transaction ID (TID).
*   A list of services involved in the transaction (e.g., {Inventory, Payment, Order, Shipping}).
*   Data specific to each service required to perform its part of the transaction (e.g., item IDs and quantities for Inventory, credit card details for Payment).

**Output:**

Your solution should output the final status of each transaction (Commit or Rollback) along with any relevant error messages.

**Constraints:**

*   The number of concurrent transactions can be very high (e.g., thousands per second).
*   Network latency between the DTM and the services can be variable.
*   Services can be temporarily unavailable.
*   The DTM should be able to recover from failures quickly.
*   Memory usage should be optimized.

**Judging Criteria:**

*   **Correctness:** Your solution must correctly implement the 2PC protocol and ensure atomicity and consistency.
*   **Robustness:** Your solution must handle various failure scenarios gracefully.
*   **Performance:** Your solution must be able to handle a high transaction load with acceptable latency.
*   **Scalability:** Your solution must be designed to scale horizontally to handle increasing transaction volume.
*   **Code Quality:** Your code should be well-structured, readable, and maintainable.

This problem requires a deep understanding of distributed systems concepts, transaction management, and concurrency control. A well-designed and implemented solution will demonstrate your ability to tackle complex engineering challenges.
