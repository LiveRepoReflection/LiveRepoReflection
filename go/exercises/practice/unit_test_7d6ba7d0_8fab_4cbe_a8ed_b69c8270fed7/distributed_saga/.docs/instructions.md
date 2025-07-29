## Question: Distributed Transaction Orchestration

### Problem Description

You are tasked with designing a distributed transaction orchestration system for a microservices architecture. Consider a simplified e-commerce platform composed of the following microservices:

*   **Order Service:** Responsible for creating and managing orders.
*   **Payment Service:** Handles payment processing.
*   **Inventory Service:** Manages product inventory.
*   **Notification Service:** Sends out notification to users.

When a customer places an order, a distributed transaction needs to be initiated to ensure data consistency across these services. The transaction should involve the following steps:

1.  **Order Creation:** The Order Service creates a new order in a pending state.
2.  **Payment Authorization:** The Payment Service attempts to authorize the payment.
3.  **Inventory Reservation:** The Inventory Service reserves the required quantity of products.
4.  **Order Confirmation:** The Order Service confirms the order, marking it as "confirmed."
5.  **Send Notification:** Send user notification by Notification Service.

If any of these steps fail, the entire transaction needs to be rolled back to maintain data consistency. The rollback process should involve the following compensation actions:

1.  **Payment Cancellation:** The Payment Service cancels the payment authorization.
2.  **Inventory Release:** The Inventory Service releases the reserved inventory.
3.  **Order Cancellation:** The Order Service cancels the order.

Your goal is to implement a robust and efficient transaction orchestration system using a saga pattern. The system should be able to handle failures gracefully and ensure that either all steps are completed successfully or all steps are rolled back successfully.

You are provided with a message queue (e.g., RabbitMQ, Kafka) for inter-service communication. Each microservice publishes events to the message queue, and the orchestrator subscribes to these events to coordinate the transaction.

**Specific Requirements:**

1.  **Saga Orchestration:** Implement a saga orchestrator that coordinates the distributed transaction. The orchestrator should subscribe to events from the microservices and publish commands to trigger the next step in the transaction or initiate the rollback process.
2.  **Idempotency:** Ensure that each step in the transaction and rollback process is idempotent. This means that if a service receives the same command multiple times, it should only execute the action once.
3.  **Failure Handling:** Implement proper error handling and retry mechanisms to handle transient failures. The system should be able to automatically retry failed steps a certain number of times before initiating the rollback process.
4.  **Concurrency:** Consider the concurrency aspects of the system. Multiple orders can be placed simultaneously, and the orchestrator should be able to handle concurrent transactions without causing data inconsistencies.
5.  **Exactly-Once Semantics:** Ensure that each event is processed exactly once by the orchestrator. This can be achieved using techniques such as message deduplication or transactional outbox pattern.
6.  **Timeouts:** Implement timeouts for each step in the transaction. If a service does not respond within a specified time, the orchestrator should initiate the rollback process.
7.  **Scalability:** The solution should be designed to be scalable to handle a large number of concurrent orders.

**Constraints:**

*   You must use Go for implementing the saga orchestrator and the microservices.
*   You must use a message queue for inter-service communication.
*   The system must be designed to be highly available and fault-tolerant.
*   You should consider the performance implications of your design and strive for optimal efficiency.
*   Assume the message queue can sometimes be unreliable.

**Evaluation Criteria:**

*   Correctness: The system should correctly execute distributed transactions and rollbacks.
*   Robustness: The system should be able to handle failures gracefully and ensure data consistency.
*   Efficiency: The system should be designed for optimal performance and scalability.
*   Code Quality: The code should be well-structured, readable, and maintainable.
*   Design: The system design should be well-thought-out and address the specific requirements and constraints.
*   Documentation: The code should be well-documented, explaining the design choices and implementation details.
