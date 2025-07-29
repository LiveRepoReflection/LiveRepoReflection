## Question: Distributed Transaction Orchestration with Limited Resources

### Question Description

You are tasked with designing a distributed transaction orchestration system for a microservices architecture. Several independent services (Service A, Service B, Service C, etc.) need to participate in atomic transactions. Traditional two-phase commit (2PC) protocols are deemed too heavyweight and introduce unacceptable latency. You need to implement a Saga pattern-based transaction coordinator, but with significant resource constraints.

**Scenario:**

Imagine an e-commerce platform where placing an order involves multiple services:

*   **Order Service (A):** Creates the order record.
*   **Payment Service (B):** Processes the payment.
*   **Inventory Service (C):** Reserves the stock.
*   **Shipping Service (D):** Schedules the shipment.

A successful order placement requires all these services to complete their respective operations. If any service fails, the entire transaction must be rolled back.

**Constraints and Requirements:**

1.  **Limited Memory:** The transaction coordinator has extremely limited memory (e.g., only enough to hold information about a small number of concurrent transactions). Persisting transaction state to disk is too slow. Therefore, you must devise a strategy to maintain transaction context with minimal memory footprint. The number of concurrent transactions may be very high.
2.  **Eventual Consistency:** Strong ACID guarantees are not required. Eventual consistency is acceptable, but the system must converge to a consistent state eventually. You want to minimize the time to achieve consistency.
3.  **Idempotency:** Each service must be idempotent. Applying the same operation multiple times should have the same effect as applying it once.
4.  **Message Broker:** Services communicate asynchronously through a reliable message broker (e.g., RabbitMQ, Kafka).
5.  **Compensating Transactions:** Each service must provide a compensating transaction (undo operation) to reverse its effects in case of a failure. These compensating transactions also need to be idempotent.
6.  **Concurrency:** The system must handle concurrent transactions efficiently.
7.  **Failure Handling:** The system must be resilient to service failures and message broker outages. Messages should eventually be delivered/processed even if there are temporary outages.
8.  **Optimization:** Minimize the number of messages exchanged for each transaction to reduce network overhead.
9.  **Scalability:** Your design should be scalable to handle a large number of services and transactions.

**Task:**

Implement a transaction coordinator that orchestrates the distributed transaction using the Saga pattern, adhering to the constraints outlined above.

Specifically, you need to design and implement the following:

*   **Transaction Coordinator Logic:** The core logic for initiating, tracking, and compensating transactions.
*   **Message Format:** The structure of the messages exchanged between the coordinator and the services.
*   **State Management:** A memory-efficient strategy for maintaining transaction context. Consider how to reconstruct transaction state when a coordinator instance restarts.
*   **Compensation Mechanism:** The mechanism for triggering and executing compensating transactions.
*   **Recovery Mechanism**: The mechanism for recovering from coordinator crashes, message broker failures or service failures.

**Bonus Challenges:**

*   **Deadlock Detection and Resolution:** Implement a mechanism to detect and resolve potential deadlocks that might occur due to resource contention across services.
*   **Optimization of Compensation Flow:** Optimize the compensation flow to minimize the time required to roll back a failed transaction. Can you execute compensations in parallel where possible, while respecting dependencies?
*   **Implement a basic simulation of all services A, B, C and D and the message broker to test your transaction coordinator.**
