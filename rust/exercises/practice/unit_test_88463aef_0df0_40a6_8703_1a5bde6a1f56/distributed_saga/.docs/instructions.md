## Problem Title: Distributed Transaction Orchestration

### Problem Description

You are building a distributed e-commerce platform. A single order might involve multiple microservices: `InventoryService`, `PaymentService`, `ShippingService`, and `NotificationService`. To ensure data consistency and reliability, you need to implement a distributed transaction orchestration mechanism using the Saga pattern.

Specifically, you need to implement a transaction orchestrator that handles the following steps for a new order:

1.  **Reserve Inventory:** Call the `InventoryService` to reserve the required quantity of each item in the order.
2.  **Process Payment:** Call the `PaymentService` to process the payment for the order.
3.  **Schedule Shipping:** Call the `ShippingService` to schedule the shipment of the order.
4.  **Send Notification:** Call the `NotificationService` to send a confirmation email to the customer.

Each service call can potentially fail. If any step fails, the orchestrator needs to execute compensating transactions (rollbacks) in reverse order to undo the changes made by the previous successful steps. For example, if the `ShippingService` fails, the orchestrator needs to:

1.  Cancel the shipment by calling `ShippingService`.
2.  Refund the payment by calling `PaymentService`.
3.  Release the reserved inventory by calling `InventoryService`.

**Your task is to implement a robust and efficient distributed transaction orchestrator that can handle transaction failures and ensure data consistency across all involved microservices.**

**Constraints and Requirements:**

*   **Concurrency:** The orchestrator must be able to handle multiple concurrent orders efficiently.
*   **Idempotency:** The service calls should be designed to be idempotent, meaning that calling the same operation multiple times has the same effect as calling it once. This is crucial to handle potential network issues and retry scenarios.
*   **Durability:** The state of the transaction (e.g., which steps have been completed, which compensations need to be executed) must be durable and recoverable in case of orchestrator failures. Consider using a persistent storage mechanism.
*   **Fault Tolerance:** The orchestrator should be resilient to failures in individual microservices. It should implement appropriate retry mechanisms with exponential backoff.
*   **Ordering:** Compensating transactions must be executed in the reverse order of the original transactions.
*   **Asynchronous Communication:** The orchestrator and microservices should communicate asynchronously (e.g., using message queues like RabbitMQ or Kafka) to decouple the components and improve scalability.
*   **Error Handling:** Handle different types of errors gracefully, including service unavailability, invalid input data, and business logic violations.
*   **Logging:** Implement detailed logging to track the progress of each transaction and diagnose potential issues.
*   **Performance:** Optimize the orchestrator for minimal latency and high throughput.

**Input:**

*   An `Order` struct containing details such as customer ID, order ID, item list (with item ID and quantity), and payment information.

**Output:**

*   A result indicating whether the order was successfully processed or if a rollback occurred.
*   Detailed logs indicating the progress of the transaction and any errors encountered.

**Considerations:**

*   You can simulate the microservices using mock implementations that introduce artificial delays and potential failures.
*   Consider using appropriate data structures to manage the state of the transaction and the list of compensating transactions.
*   Think about how to handle partial failures, where some compensating transactions might fail.
*   Explore different strategies for handling concurrent access to shared resources (e.g., inventory).
*   Choose appropriate error codes and messages to provide meaningful feedback to the caller.
*   Consider the trade-offs between different consistency levels (e.g., eventual consistency vs. strong consistency).

This problem requires a deep understanding of distributed systems concepts, transaction management, and concurrency control. It also requires strong Rust programming skills, including the ability to work with asynchronous programming, data structures, and error handling. Solving this problem effectively requires careful design, implementation, and testing to ensure correctness, robustness, and performance.
