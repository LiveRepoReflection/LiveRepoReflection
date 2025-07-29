## Question: Distributed Transaction Coordinator

### Description

You are tasked with building a highly reliable and scalable distributed transaction coordinator for a microservices architecture. This coordinator must ensure ACID (Atomicity, Consistency, Isolation, Durability) properties across multiple services when a single business transaction spans them. Due to the nature of the microservices, traditional two-phase commit (2PC) is not feasible due to its blocking nature and potential for deadlock in a complex, rapidly evolving system. Instead, you will implement a Saga pattern with compensations.

**Scenario:**

Imagine an e-commerce platform where placing an order involves several microservices:

*   **Order Service:** Creates a new order record.
*   **Inventory Service:** Reserves the required quantity of items.
*   **Payment Service:** Processes the payment.
*   **Shipping Service:** Schedules the shipment.

A successful order placement requires successful execution of all these steps. If any step fails, the system must roll back any changes made by the previous steps using compensation transactions.

**Requirements:**

1.  **Saga Orchestration:** Implement a central coordinator service that orchestrates the saga. This service receives the initial request (e.g., "Place Order") and manages the execution of the saga steps.  The coordinator is responsible for invoking the microservices in the correct order and handling failures.
2.  **Compensation Transactions:** Each microservice must provide a "compensation" endpoint that reverses the effects of a successful transaction. For example, the Inventory Service's compensation transaction would release the reserved items. The Payment Service might issue a refund.
3.  **Idempotency:** All transactions (both forward and compensation) must be idempotent. This means that if a transaction is executed multiple times with the same input, it should have the same effect as executing it once. This is crucial for handling retries.
4.  **Durability:** The coordinator must persist the state of the saga (e.g., which steps have been completed, which compensations have been executed) to a durable storage (e.g., a database). This ensures that the saga can be resumed even if the coordinator service crashes.
5.  **Concurrency:** Multiple sagas can run concurrently. The coordinator must handle concurrent saga executions correctly and avoid conflicts.
6.  **Error Handling:** Implement robust error handling, including retries with exponential backoff for transient failures and dead-letter queues for persistent failures.  Consider scenarios where a compensation transaction itself fails.
7.  **Scalability:** The coordinator should be designed to handle a high volume of transactions. Consider techniques such as sharding or partitioning the saga state.
8.  **Observability:** Provide metrics and logs to monitor the performance and health of the coordinator, as well as the progress of individual sagas.
9. **Deadline:** Each saga has a maximum time to live(TTL). If a saga is not completed within TTL, it must be cancelled and all compensation transactions must be executed.

**Input:**

The coordinator receives a "Place Order" request containing:

*   `order_id`: A unique identifier for the order.
*   `user_id`: The ID of the user placing the order.
*   `items`: A list of items to be ordered (item ID and quantity).
*   `payment_info`: Payment details.

**Output:**

The coordinator returns:

*   `order_id`: The ID of the order.
*   `status`: "SUCCESS" if the order was placed successfully, "FAILED" otherwise.
*   `error_message`: (Optional) An error message if the order failed.

**Constraints:**

*   Assume the existence of the four microservices (Order, Inventory, Payment, Shipping) with their respective API endpoints for forward and compensation transactions.
*   Network communication between the coordinator and the microservices may be unreliable.
*   The system must be highly available and resilient to failures.
*   Optimize for throughput and minimize latency.
*   Avoid global locks and distributed transactions (e.g., XA).
*   Implement the solution in Rust, leveraging its concurrency features and strong type system.

**Bonus:**

*   Implement a visual dashboard to monitor the progress of sagas and identify potential bottlenecks.
*   Implement a mechanism for handling long-running compensation transactions.

This problem requires a deep understanding of distributed systems concepts, concurrency, and error handling. It also demands a well-thought-out architecture and efficient implementation to meet the performance and reliability requirements. Good luck!
