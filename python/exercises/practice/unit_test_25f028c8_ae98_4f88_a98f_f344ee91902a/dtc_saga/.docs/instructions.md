## Problem: Distributed Transaction Orchestration

**Description:**

You are tasked with designing and implementing a distributed transaction orchestration system for a microservices architecture. Imagine a scenario where an e-commerce platform consists of several independent services: `InventoryService`, `PaymentService`, `ShippingService`, and `OrderService`.

When a user places an order, a transaction needs to be initiated across these services to ensure data consistency. The order placement process involves the following steps:

1.  `OrderService` receives an order request.
2.  `OrderService` validates the order and reserves items from `InventoryService`.
3.  `OrderService` triggers a payment request to `PaymentService`.
4.  `OrderService` instructs `ShippingService` to prepare shipment.
5.  `OrderService` confirms the order, finalizing changes in all services.

However, failures can occur at any step in the process. For example:

*   `InventoryService` might not have enough stock.
*   `PaymentService` might decline the payment.
*   `ShippingService` might encounter an issue with the shipping address.

If any of these failures happen, the entire transaction needs to be rolled back to maintain consistency. For instance, if the payment fails, the reserved items in `InventoryService` need to be released, and the order should be cancelled.

**Your task is to implement a distributed transaction coordinator (DTC) that ensures atomicity and consistency across these microservices using the Saga pattern.** The Saga pattern is a sequence of local transactions. Each local transaction updates the database and publishes an event to trigger the next local transaction in the saga. If one of the transactions fails, the saga executes a series of compensating transactions that undo the changes made by the preceding transactions.

**Specific Requirements:**

1.  **Idempotency:** Design your system to handle duplicate events gracefully. Each service should be able to receive the same event multiple times without adverse effects.
2.  **Durability:** The state of the Saga needs to be durable. If the DTC crashes, it should be able to resume the Saga from where it left off. Consider using a database or persistent message queue to store the Saga state.
3.  **Concurrency:** Your system should be able to handle multiple concurrent order placements without data corruption or race conditions.
4.  **Scalability:** While a full-scale distributed system is beyond the scope of a coding challenge, consider the scalability of your design choices.
5.  **Message Broker:** Utilize a message broker to orchestrate the sequence of events between the different services. You can use `RabbitMQ`, `Kafka`, or any other suitable message broker. Assume each service has a dedicated queue to which the DTC publishes events.
6.  **Compensation Transactions:** You must define and implement appropriate compensation transactions for each step in the order placement process.
7.  **Error Handling:** Implement robust error handling and logging to track the progress and status of each Saga instance.
8.  **Optimization:** Minimize the overall execution time of the Saga. Consider strategies like parallelizing certain operations if possible. However, ensure the correctness of the transaction.
9.  **Service Interaction:** Assume each service exposes an API (can be mocked). The DTC interacts with these APIs through asynchronous message passing via the message broker.

**Constraints:**

*   You only need to implement the DTC and mock the `InventoryService`, `PaymentService`, `ShippingService`, and `OrderService`. Focus on the orchestration logic.
*   Assume the message broker is reliable and guarantees at-least-once delivery.
*   Assume the services have sufficient capacity to handle requests.
*   Minimize external dependencies as much as practical.

**Evaluation Criteria:**

*   Correctness of the distributed transaction implementation.
*   Robustness of error handling and compensation logic.
*   Efficiency of the Saga execution.
*   Clarity and maintainability of the code.
*   Adherence to the specified requirements and constraints.
*   Demonstration of idempotency and durability.
