## Question Title: Distributed Transaction Orchestration

### Question Description:

You are tasked with designing and implementing a distributed transaction orchestration system for an e-commerce platform. The platform handles a large number of concurrent requests for placing orders. Each order involves multiple microservices:

1.  **Inventory Service:** Checks if the requested items are in stock and reserves them.
2.  **Payment Service:** Processes the payment for the order.
3.  **Shipping Service:** Schedules the shipment of the order.
4.  **Order Service:** Creates the order record in the central database.

These services communicate via asynchronous messaging (e.g., Kafka, RabbitMQ). Each service has its own database and is responsible for managing its data consistently. Your system must guarantee atomicity across these services to ensure data consistency. This means that either all operations involved in placing an order succeed, or all are rolled back in case of failure.

**Specific Requirements:**

*   **Transaction Coordination:** Implement a central orchestrator (a dedicated microservice) that manages the transaction flow. The orchestrator should initiate transactions, track the progress of each service, and handle compensations (rollbacks) in case of failures.
*   **Compensation Mechanism:** Each service must provide a compensation (rollback) API that the orchestrator can invoke to undo the effects of a successful operation. For example, the Inventory Service's compensation API would release the reserved items back to stock. The Payment Service would initiate a refund.
*   **Idempotency:** Implement each service's operations and compensation APIs to be idempotent. This is crucial to handle message retries and ensure that operations are executed only once, even if the same message is received multiple times.
*   **Concurrency:** The system must handle a large number of concurrent order placement requests efficiently. Consider thread safety and potential race conditions in the orchestrator and the services.
*   **Failure Handling:** The system should be resilient to failures. The orchestrator should be able to recover from crashes and resume ongoing transactions. Services might also experience temporary failures. The system should implement appropriate retry mechanisms and circuit breakers to handle these scenarios.
*   **Optimistic Locking:** Implement optimistic locking on Inventory service to handle concurrency of multiple users trying to purchase the same item.

**Constraints:**

*   **Latency:** Minimize the overall latency of the order placement process.
*   **Scalability:** The system must be horizontally scalable to handle increasing traffic.
*   **Consistency:** Ensure data consistency across all services, even in the presence of failures.
*   **Messaging:** Use asynchronous messaging (Kafka/RabbitMQ) for communication between the orchestrator and the services.

**Bonus Challenges:**

*   Implement a monitoring system to track the status of transactions and identify potential bottlenecks.
*   Implement a distributed lock mechanism to prevent concurrent execution of conflicting operations.
*   Explore alternative transaction management patterns, such as Saga pattern with choreography.
*   Implement a mechanism to detect and resolve deadlocks in the transaction flow.

This problem requires careful consideration of distributed systems concepts, transaction management principles, and concurrency control techniques. Successful solutions will demonstrate a clear understanding of these concepts and a well-designed and implemented system that meets the specified requirements and constraints.
