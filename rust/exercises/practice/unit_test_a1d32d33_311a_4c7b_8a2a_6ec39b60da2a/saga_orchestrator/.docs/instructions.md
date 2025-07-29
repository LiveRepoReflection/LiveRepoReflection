## Question: Distributed Transaction Orchestration

### Description:

You are tasked with designing and implementing a distributed transaction orchestration system for a microservices architecture. This system must ensure atomicity, consistency, isolation, and durability (ACID) across multiple services when performing complex operations.

Imagine a scenario where a customer places an order. This involves several microservices:

*   **Order Service:** Creates and manages the order.
*   **Payment Service:** Processes the payment.
*   **Inventory Service:** Reserves and deducts stock.
*   **Shipping Service:** Schedules the shipment.

A single order placement operation *must* either complete successfully across all services or be rolled back entirely if any service fails. This requires a robust transaction orchestration mechanism.

Your system should function as a central coordinator, guiding each service to perform its part of the transaction and handling potential failures gracefully. The system must support the Saga pattern, specifically the *choreography-based saga* to simplify inter-service communication. Each service will listen to events and react accordingly.

**Specific Requirements:**

1.  **Event-Driven Architecture:** Services communicate via asynchronous events. Assume a reliable message broker (e.g., Kafka, RabbitMQ) is available. Messages are guaranteed to be delivered at least once.
2.  **Choreography-Based Saga:**  The orchestrator is implicit.  Each service listens for relevant events and emits events to trigger the next step or to initiate compensation (rollback) in other services.
3.  **Idempotency:**  Services must be idempotent. They should be able to safely handle the same event multiple times without adverse effects. This is crucial due to the "at least once" delivery guarantee of the message broker.
4.  **Fault Tolerance:**  The system must be resilient to service failures.  If a service fails during the transaction, the saga should trigger compensation actions in all previously involved services to revert their changes.
5.  **Concurrency:**  The system must handle concurrent order placements efficiently without causing data inconsistencies (e.g., over-selling inventory). Consider strategies to mitigate race conditions.
6.  **Deadlock Prevention:** Design the system to prevent deadlocks or livelocks during compensation actions.
7.  **Observability:** Design the system to provide insight into the progress and status of ongoing sagas for monitoring and debugging purposes. This involves tracing events across services.
8.  **Optimistic Concurrency Control:** For Inventory Service, implement optimistic concurrency control using a version number to avoid race condition.

**Constraints:**

*   You cannot use two-phase commit (2PC) or distributed transactions (XA). The microservices architecture prohibits direct transactional coordination.
*   Services can fail at any point during the transaction.
*   Network communication between services can be unreliable.
*   The system should be designed for high throughput and low latency.

**Evaluation Criteria:**

*   **Correctness:** Does the system correctly ensure atomicity and consistency across services?
*   **Resilience:** How well does the system handle service failures and network issues?
*   **Performance:** Does the system achieve reasonable throughput and latency under load?
*   **Scalability:** Is the system designed to scale horizontally to handle increased demand?
*   **Code Quality:** Is the code well-structured, readable, and maintainable?
*   **Error Handling:** Is error handling robust and informative?
*   **Concurrency Handling:** Is concurrency correctly handled to avoid race conditions?

This problem requires careful consideration of distributed systems principles, concurrency control, and fault tolerance techniques. It demands a robust and well-designed solution to ensure data integrity and system reliability in a complex microservices environment.
