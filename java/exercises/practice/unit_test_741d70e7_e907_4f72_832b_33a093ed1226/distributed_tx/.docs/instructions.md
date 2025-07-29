## Project Name

`DistributedTransactionManager`

## Question Description

Design and implement a simplified, in-memory distributed transaction manager (DTM) for managing transactions across multiple services. This DTM guarantees ACID (Atomicity, Consistency, Isolation, Durability) properties in a distributed environment.

**Scenario:**

Imagine a microservices architecture where updates to a single business entity require modifications across multiple services (e.g., updating a user profile may involve updating the user service, profile service, and notification service). To ensure data consistency, these updates must occur within a single, atomic transaction.

**Your Task:**

You are to implement a simplified DTM that coordinates transactions across multiple participating services. Each service exposes an interface to perform operations and to participate in the distributed transaction.

**Components:**

1.  **TransactionManager:**
    *   Responsible for coordinating the distributed transaction.
    *   Provides methods to begin, commit, and rollback transactions.
    *   Maintains the state of each transaction (e.g., active, prepared, committed, rolled back).
    *   Uses a two-phase commit (2PC) protocol to ensure atomicity.

2.  **Participant Service Interface:**
    *   Defines methods that each participating service must implement.
    *   `prepare(transactionId)`: Each service attempts to perform its part of the transaction. If successful, it locks the necessary resources and returns 'PREPARED'. If it fails, it returns 'ABORT'.
    *   `commit(transactionId)`: If all services prepared successfully, each service commits its changes.
    *   `rollback(transactionId)`: If any service failed to prepare, each service rolls back its changes and releases any locks.

3.  **Simulated Services:**
    *   You don't need to implement actual network calls. Instead, simulate the behavior of different services using in-memory data structures.
    *   Each service should have a simulated database (e.g., a `HashMap`) to store data.
    *   Simulate potential service failures and network issues (e.g., by randomly returning "ABORT" during the prepare phase).
    *   Implement at least two or three simulated services.

**Requirements:**

*   **Atomicity:** All participating services must either commit or rollback the transaction as a single unit of work.
*   **Consistency:** The DTM must maintain data consistency across all services.
*   **Isolation:** Transactions must be isolated from each other. You only need to consider a single concurrent transaction at a time.
*   **Durability:** Once a transaction is committed, the changes must be durable (in this simplified version, durability can be simulated with in-memory persistence).
*   **Two-Phase Commit (2PC):** The DTM must implement the 2PC protocol.
*   **Concurrency:** Handle a single concurrent transaction gracefully. No need to implement full-fledged concurrency control mechanisms.
*   **Error Handling:** Implement robust error handling to deal with service failures, network issues, and other potential problems.
*   **Optimization:** Minimize resource locking duration during the prepare phase.
*   **Logging:** Implement basic logging to trace the execution of transactions and debug potential issues.

**Constraints:**

*   Use only standard Java libraries (no external dependencies).
*   Focus on correctness, clarity, and efficiency.
*   Provide clear and concise code.
*   Assume that network delays are negligible for this exercise.

**Bonus Points:**

*   Implement a timeout mechanism to handle services that fail to respond during the prepare or commit phase.
*   Implement a basic recovery mechanism to handle DTM failures (e.g., recovering transaction states from a log file).
*   Develop a unit test suite to verify the correctness of your DTM.

This question focuses on applying knowledge of distributed systems principles, concurrency, and error handling in a practical scenario. The challenge lies in correctly implementing the 2PC protocol, handling potential failures, and ensuring data consistency across multiple simulated services. The optimization requirement and the bonus points add further layers of complexity.
