## Problem: Distributed Transaction Manager

**Description:**

You are tasked with designing and implementing a simplified distributed transaction manager for a microservice architecture. Imagine a scenario where multiple independent services need to perform operations that must be ACID (Atomicity, Consistency, Isolation, Durability) compliant across all involved services.  However, each service has its own independent database and no shared transaction context.

Your transaction manager must orchestrate transactions across these services, ensuring that either all operations succeed (commit) or all operations are rolled back (abort), even in the face of network failures, service crashes, or data inconsistencies.

To simplify the implementation, you will focus on the Two-Phase Commit (2PC) protocol.

**System Requirements:**

1.  **Transaction Initiation:** Clients initiate a distributed transaction by sending a request to the transaction manager, specifying the services involved and the operations they need to perform.

2.  **Prepare Phase:** The transaction manager sends a "prepare" message to all participating services.  Each service attempts to execute its part of the transaction and, if successful, "votes" to commit by responding with a "prepared" message. If a service fails to prepare (e.g., due to data validation errors, resource unavailability), it responds with a "abort" message.

3.  **Commit/Abort Phase:**
    *   If all services respond with "prepared," the transaction manager sends a "commit" message to all services. Each service then permanently applies the changes and acknowledges with a "committed" message.
    *   If any service responds with "abort" or fails to respond within a reasonable timeout, the transaction manager sends an "abort" message to all services. Each service then rolls back any changes made during the prepare phase and acknowledges with an "aborted" message.

4.  **Durability:** The transaction manager must ensure durability. The decision to commit or abort must be persisted to durable storage (e.g., a log file or database) *before* the commit/abort messages are sent to the services. This ensures that the transaction manager can recover its state and complete the transaction even after a crash.

5.  **Idempotency:** Services must be designed to handle duplicate "prepare," "commit," and "abort" messages. This is crucial because network failures can lead to messages being resent.  Each service must implement idempotent logic to ensure that the same operation is not executed multiple times.

6. **Timeout:** Implement a timeout mechanism. If a service does not respond within a specified time, the transaction manager should assume the service has failed and abort the transaction.

**Constraints:**

*   You are not allowed to use existing distributed transaction libraries or frameworks (e.g., JTA/XA). The goal is to implement the core 2PC logic yourself.
*   Assume that the underlying communication between the transaction manager and the services is reliable, ordered, and at-least-once delivery. However, services can still fail or become unreachable.
*   Focus on the core 2PC logic and error handling. You don't need to implement a full-fledged service registry, service discovery, or complex message queuing.
*   Assume that each service has a simple API with `prepare()`, `commit()`, and `rollback()` methods that can be invoked by the transaction manager. These methods may throw exceptions to indicate failures.
* The number of services for each transaction can be different.
* The sequence of the services to prepare, commit or abort does not matter.

**Optimization Requirements:**

*   **Concurrency:**  The transaction manager should be able to handle multiple concurrent transactions efficiently.
*   **Scalability:** The design should consider potential scalability issues, such as the number of services and the number of concurrent transactions. (While you don't need to implement a fully scalable system, your design should acknowledge and address potential bottlenecks).

**Evaluation Criteria:**

*   **Correctness:** The implementation must correctly implement the 2PC protocol and ensure ACID properties.
*   **Robustness:** The implementation must handle failures gracefully (service crashes, network errors, timeouts) and ensure that transactions are either fully committed or fully rolled back.
*   **Efficiency:** The implementation should be reasonably efficient in terms of resource utilization and throughput.
*   **Code Quality:** The code should be well-structured, readable, and maintainable.
*   **Design Justification:** You should be able to explain the design choices made and justify the trade-offs.  Specifically address how your design handles concurrency, durability, idempotency, and scalability.

This problem requires a deep understanding of distributed systems concepts and careful consideration of various failure scenarios. Good luck!
