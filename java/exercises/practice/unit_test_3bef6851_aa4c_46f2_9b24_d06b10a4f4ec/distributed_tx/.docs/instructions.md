## Problem: Distributed Transaction Manager

**Description:**

You are tasked with designing and implementing a simplified, in-memory distributed transaction manager (DTM).  Imagine a system where multiple independent services (represented as nodes in a network) need to perform operations that must either all succeed or all fail – an "all or nothing" scenario governed by the ACID properties.

Your DTM must coordinate transactions across these services using a two-phase commit (2PC) protocol. Each service holds a local resource (represented by a simple integer value) and can perform increment and decrement operations on it. The DTM is responsible for ensuring atomicity, consistency, isolation, and durability (in memory, for this problem) across all participating services during a transaction.

**Specific Requirements:**

1.  **Services (Nodes):** Represented by a unique ID (integer). Each service maintains a local state (an integer representing a resource value). You need to simulate at least 5 services. The initial value of each service can be randomly generated.

2.  **Transaction Manager (DTM):** A central component responsible for coordinating transactions.

3.  **Transaction Operations:**
    *   `increment(serviceId, amount)`: Increments the resource value of the specified service by `amount`.
    *   `decrement(serviceId, amount)`: Decrements the resource value of the specified service by `amount`.

4.  **Two-Phase Commit (2PC) Protocol:**
    *   **Phase 1 (Prepare):**
        *   The DTM receives a transaction request (a list of operations: increment/decrement on various services).
        *   The DTM sends a "prepare" message to all participating services, asking them to tentatively execute the operations and log their intentions (in memory only).
        *   Each service responds with either "vote_commit" (if it can successfully perform the operations) or "vote_abort" (if it cannot).  A service might vote to abort due to insufficient resources (e.g., trying to decrement below zero), or internal errors (simulated by a random chance of failure, like a 10% chance).
    *   **Phase 2 (Commit/Rollback):**
        *   If the DTM receives "vote_commit" from all participating services, it sends a "commit" message to all services. Each service then permanently applies the changes.
        *   If the DTM receives "vote_abort" from any service, it sends a "rollback" message to all services. Each service then reverts any tentative changes.

5.  **Concurrency:**  The DTM must be able to handle multiple concurrent transaction requests. Implement appropriate locking mechanisms to prevent race conditions and ensure data consistency.  The DTM must prevent deadlocks from occurring.

6.  **Fault Tolerance (Simplified):**  Simulate a service failure by randomly making a service unavailable during the prepare phase (e.g., 5% chance). If a service fails during the prepare phase, the DTM should treat it as a "vote_abort" and rollback the entire transaction. Do *not* implement recovery mechanisms; simply abort the transaction and log the failure.

7.  **Optimization:** Implement a deadlock detection mechanism. If a deadlock is detected, abort one of the transactions involved in the deadlock to resolve it. Prioritize aborting transactions that have the fewest number of participating services.

8.  **Logging:** Implement basic logging to record transaction attempts, prepare votes, commit/rollback decisions, and any failures (service unavailability, deadlocks).

**Constraints:**

*   All operations are performed in-memory.
*   You are not allowed to use external transaction management libraries or databases. You must implement the 2PC protocol and concurrency control yourself.
*   The number of services is fixed at the start and does not change during the execution.
*   The `amount` in increment/decrement operations is a positive integer.
*   The system should be designed to handle a reasonably high volume of concurrent transaction requests (e.g., at least 10 concurrent requests).
*   The correctness of the final resource values across all services must be verifiable.

**Evaluation Criteria:**

*   Correctness of the 2PC implementation (atomicity, consistency, isolation).
*   Concurrency handling and deadlock prevention.
*   Fault tolerance (handling service unavailability).
*   Efficiency and scalability (ability to handle concurrent requests).
*   Code quality, readability, and maintainability.
*   Completeness of logging.

This problem requires a strong understanding of distributed systems concepts, concurrency control, and the 2PC protocol. Good luck!
