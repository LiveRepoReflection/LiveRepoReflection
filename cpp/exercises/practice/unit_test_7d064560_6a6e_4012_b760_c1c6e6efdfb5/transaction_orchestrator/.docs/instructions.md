## Problem: Distributed Transaction Orchestrator

**Description:**

You are tasked with designing and implementing a simplified distributed transaction orchestrator. This orchestrator is responsible for managing transactions that span multiple independent services.

Imagine a scenario where a user wants to transfer funds from their bank account to another user's account across different banks (microservices). The transaction involves several steps:

1.  Debit the sender's account in Bank A.
2.  Credit the receiver's account in Bank B.
3.  Log the transaction details in an audit service.

Each of these steps is handled by a separate microservice and can fail independently. Your orchestrator must ensure atomicity, consistency, isolation, and durability (ACID) across these services.

**Requirements:**

1.  **Transaction Coordination:** Implement a transaction coordinator that can initiate, monitor, and finalize a distributed transaction.
2.  **Two-Phase Commit (2PC):** Implement a simplified version of the 2PC protocol to ensure atomicity.  The coordinator should send a "prepare" message to all participating services. If all services respond with "commit-ready," the coordinator sends a "commit" message. If any service responds with "abort," or doesn't respond within a specific timeout, the coordinator sends an "abort" message to all services.
3.  **Idempotency:** Design the system such that each operation is idempotent.  Services should be able to handle the same "commit" or "abort" message multiple times without adverse effects (e.g., double debiting). This is crucial for handling network failures and message retries.
4.  **Failure Handling:** Implement robust failure handling. The coordinator should be able to recover from failures (e.g., coordinator crash) and resume unfinished transactions.  Assume you have a persistent log to store transaction states.
5.  **Concurrency:** Design the orchestrator to handle multiple concurrent transactions.
6.  **Service Abstraction:** The orchestrator interacts with services through a well-defined interface.  For the purpose of this exercise, you can simulate service interactions using function calls.  Assume each service can perform "prepare," "commit," and "abort" actions.

**Constraints:**

*   **Limited Resources:** You are working with limited memory and processing power. Optimize for efficiency.
*   **Unreliable Network:** Assume the network is unreliable. Messages can be lost, duplicated, or delayed.
*   **Service Unavailability:** Services can become temporarily unavailable. The orchestrator should handle these situations gracefully.
*   **Timeout:** Implement reasonable timeouts for service responses.
*   **Scalability:** Although this is a simplified implementation, consider the potential for scaling the orchestrator to handle a large number of transactions.

**Input:**

The input consists of a series of transaction requests. Each request specifies the participating services and the actions to be performed on each service (e.g., debit account A, credit account B). Each service action will have its own unique identifier.

**Output:**

The output should indicate whether each transaction was successfully committed or aborted.  The output should also include any error messages or relevant information about the transaction process (e.g., timeout, service unavailable).

**Scoring:**

The solution will be evaluated based on the following criteria:

*   **Correctness:** The solution must correctly implement the 2PC protocol and ensure atomicity across services.
*   **Robustness:** The solution must handle various failure scenarios (coordinator crash, service unavailability, network failures).
*   **Efficiency:** The solution must be efficient in terms of memory usage and processing time.
*   **Concurrency:** The solution must handle multiple concurrent transactions correctly.
*   **Code Quality:** The code must be well-structured, readable, and maintainable.

**Bonus:**

*   Implement a mechanism for detecting and resolving deadlocks.
*   Implement a more sophisticated consensus algorithm (e.g., Raft) for the coordinator to ensure high availability.
*   Provide a basic monitoring system to track the status of transactions.
