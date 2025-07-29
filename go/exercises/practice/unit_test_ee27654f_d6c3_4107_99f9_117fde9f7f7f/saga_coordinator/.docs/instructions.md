## Problem: Distributed Transaction Coordinator

**Description:**

You are tasked with designing a distributed transaction coordinator in a microservices architecture. Multiple services need to participate in transactions that must adhere to the ACID properties (Atomicity, Consistency, Isolation, Durability). However, direct two-phase commit (2PC) is not feasible due to the diverse technologies and independent deployment cycles of the services. You need to implement a Saga pattern with compensation transactions to achieve eventual consistency.

**Details:**

Imagine an e-commerce system with the following services: `OrderService`, `PaymentService`, `InventoryService`, and `NotificationService`. A typical order placement scenario involves these steps:

1.  `OrderService` creates a new order record (pending state).
2.  `PaymentService` reserves funds from the customer's account.
3.  `InventoryService` reserves the required items from the inventory.
4.  `NotificationService` sends an order confirmation email to the customer.
5.  `OrderService` updates the order record to a confirmed state.

If any of these steps fail, the previous steps need to be compensated to maintain data consistency. For instance, if the `InventoryService` fails to reserve items due to insufficient stock, the `PaymentService` needs to release the reserved funds, and the `OrderService` should cancel the order.

**Your task is to implement a transaction coordinator that manages these distributed transactions using the Saga pattern.**

**Specific Requirements:**

1.  **Saga Definition:** You need to define a configuration format (e.g., JSON or YAML) for describing the saga. This configuration should specify the steps involved in the transaction, the participating services, the forward transaction for each step, and the corresponding compensation transaction.
    *   For example:

    ```json
    {
      "sagaName": "OrderPlacementSaga",
      "steps": [
        {
          "service": "OrderService",
          "transaction": "createOrder",
          "compensation": "cancelOrder"
        },
        {
          "service": "PaymentService",
          "transaction": "reserveFunds",
          "compensation": "releaseFunds"
        },
        {
          "service": "InventoryService",
          "transaction": "reserveInventory",
          "compensation": "releaseInventory"
        },
        {
          "service": "NotificationService",
          "transaction": "sendConfirmationEmail",
          "compensation": "sendCancellationEmail"
        },
        {
          "service": "OrderService",
          "transaction": "confirmOrder",
          "compensation": null
        }
      ]
    }
    ```

2.  **Transaction Coordinator Engine:** Implement a core component that reads the saga definition and executes the transactions. This engine should handle:
    *   Invoking forward transactions in the defined order.
    *   Handling transaction failures and invoking compensation transactions in reverse order.
    *   Maintaining the saga state (e.g., in progress, completed, failed).
    *   Implement a retry mechanism for failed transactions and compensation transactions.

3.  **Idempotency:** Ensure that both forward and compensation transactions are idempotent. This means that if a transaction is executed multiple times, the result should be the same as if it were executed only once.  Consider how to handle scenarios where a transaction might have partially executed before a failure.

4.  **Concurrency:** Design the coordinator to handle multiple concurrent saga executions. Consider potential race conditions and implement appropriate locking or concurrency control mechanisms.

5.  **Error Handling:** Implement robust error handling.  The coordinator should be able to gracefully handle service unavailability, network errors, and unexpected exceptions during transaction execution or compensation.

6.  **Logging and Monitoring:** Implement comprehensive logging to track the progress and status of each saga execution. Consider metrics for monitoring the overall health and performance of the transaction coordinator.

**Constraints:**

*   **External Services:** You do *not* need to implement the actual `OrderService`, `PaymentService`, `InventoryService`, and `NotificationService`. You can simulate their behavior with mock functions that return success or failure randomly (or based on predefined conditions). The coordinator should interact with these services via HTTP or gRPC (choose one, and clearly specify).
*   **Persistence:** The saga state should be persisted to a durable storage (e.g., in-memory, file system, or database). The choice affects performance and complexity.
*   **Timeout:**  Implement timeouts for each transaction step. If a service does not respond within a specified timeout, the coordinator should consider the transaction failed and initiate compensation.
*   **Optimization:** The coordinator should be designed to minimize the impact on the performance of the participating services.  Consider strategies for asynchronous communication and batching of operations.

**Bonus Challenges:**

*   Implement a visual dashboard to monitor the status of running sagas.
*   Allow manual intervention to resolve failed sagas (e.g., manually retry a transaction or skip a compensation).
*   Implement dead-letter queue for failed compensations.

This problem requires a good understanding of distributed systems concepts, concurrency, error handling, and system design. The multiple constraints and the need for optimization make it a challenging task suitable for experienced Go developers. Good luck!
