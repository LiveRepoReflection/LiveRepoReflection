## The Distributed Transaction Coordinator

### Question Description

You are tasked with designing and implementing a simplified, yet robust, Distributed Transaction Coordinator (DTC) for a microservices architecture. This DTC will ensure atomicity across multiple independent services during complex operations.

**Scenario:**

Imagine an e-commerce platform where placing an order involves multiple services:

*   **Order Service:** Creates the order record.
*   **Inventory Service:** Decreases the stock of the ordered items.
*   **Payment Service:** Processes the payment.
*   **Notification Service:** Sends email/SMS for the order confirmation.

All these actions must happen atomically. If any service fails, the entire transaction must be rolled back to maintain data consistency.

**Requirements:**

1.  **Transaction Initiation:** A client initiates a distributed transaction by contacting the DTC. The DTC generates a unique transaction ID (UUID).
2.  **Two-Phase Commit (2PC) Protocol:** Implement the 2PC protocol to coordinate the transaction across services.
    *   **Phase 1 (Prepare):** The DTC sends a "prepare" message to all participating services (Order, Inventory, Payment, Notification). Each service attempts to perform its part of the transaction and responds with either "prepared" (if successful and the change is tentatively committed) or "abort" (if it fails).
    *   **Phase 2 (Commit/Rollback):**
        *   If all services respond with "prepared," the DTC sends a "commit" message to all services. Each service then permanently commits its changes.
        *   If any service responds with "abort," or if the DTC doesn't receive a response from a service within a specified timeout, the DTC sends a "rollback" message to all services. Each service then rolls back any tentative changes.
3.  **Idempotency:** Services must handle prepare, commit, and rollback messages idempotently. This means that if a service receives the same message multiple times, it only executes the operation once.
4.  **Crash Recovery:** The DTC needs to be resilient to crashes. Upon restart, it should be able to recover the state of ongoing transactions and complete them (either commit or rollback). For simplicity, you can simulate crash recovery by storing transaction states in memory. A more robust implementation would involve persistent storage (e.g., a database).
5.  **Timeout Handling:** Implement a timeout mechanism for the prepare phase. If a service does not respond within a reasonable time (e.g., 5 seconds), the DTC should assume it has failed and initiate a rollback.
6.  **Concurrency:** The DTC must be able to handle multiple concurrent transactions.
7.  **Scalability & Performance:** The system needs to be efficient. Avoid unnecessary blocking operations and aim for minimal latency.
8.  **Logging:** Implement proper logging to track transaction progress and any errors encountered.

**Constraints:**

*   **Simulate Services:** You don't need to implement actual Order, Inventory, Payment, and Notification services. Instead, simulate their behavior using simple Java classes with methods that can either succeed or fail (randomly or based on predefined conditions).
*   **Communication:** Simulate inter-service communication using in-memory method calls or simple messaging (e.g., using a concurrent queue). Avoid external dependencies like REST APIs or message brokers for simplicity.
*   **Error Handling:** Implement robust error handling to gracefully handle failures, timeouts, and other exceptions.

**Evaluation Criteria:**

*   Correctness: Does the DTC correctly implement the 2PC protocol and ensure atomicity?
*   Resilience: Can the DTC recover from crashes and handle timeouts gracefully?
*   Idempotency: Do the services handle duplicate messages correctly?
*   Concurrency: Can the DTC handle multiple concurrent transactions without issues?
*   Performance: Is the DTC efficient and does it minimize latency?
*   Code Quality: Is the code well-structured, readable, and maintainable?
*   Logging: Is the logging informative and helpful for debugging?

This problem requires a good understanding of distributed systems concepts, concurrency, and error handling. Efficient design and coding are crucial to meet the performance requirements. You will need to carefully consider the trade-offs between simplicity and robustness when making design decisions.
