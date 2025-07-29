## Question: Distributed Transaction Orchestration

### Problem Description

You are tasked with designing and implementing a distributed transaction orchestration system for an e-commerce platform. This system needs to manage transactions across multiple microservices: `OrderService`, `PaymentService`, `InventoryService`, and `NotificationService`.

When a customer places an order, the following steps must occur atomically:

1.  `OrderService`: Create a new order record.
2.  `PaymentService`: Process the payment for the order.
3.  `InventoryService`: Reserve (or deduct, depending on the inventory model chosen) the ordered items from the inventory.
4.  `NotificationService`: Send a confirmation email to the customer.

If any of these steps fail, the entire transaction must be rolled back, ensuring data consistency across all services.

**Specific Requirements:**

*   **Atomicity:** The entire order placement process must be atomic; either all steps succeed, or none do.
*   **Durability:** Once the transaction is committed, the changes must be durable and not lost, even in the event of system failures.
*   **Isolation:** Concurrent order placements should not interfere with each other, maintaining data integrity.
*   **Scalability:** The system should be able to handle a high volume of concurrent order requests.
*   **Fault Tolerance:** The system should gracefully handle failures in individual services (e.g., network issues, service crashes) and recover from them.
*   **Observability:**  Provide mechanisms for monitoring the state of transactions, identifying potential bottlenecks, and diagnosing failures.

**Constraints:**

*   You can assume that each microservice has its own independent database.  Direct database access across services is prohibited. Communication between services should occur via asynchronous messaging (e.g., using a message queue like RabbitMQ or Kafka).
*   You are free to choose the transaction orchestration pattern (e.g., Saga pattern with choreography or orchestration, Two-Phase Commit (2PC), etc.). However, you must justify your choice based on the problem requirements and constraints.  Consider the trade-offs in terms of complexity, performance, and consistency.
*   Assume that network latency between services can be variable and unpredictable.
*   You must implement a mechanism to handle idempotent operations within each service to avoid issues related to duplicate messages or retries.
*   The maximum time allowed for the entire transaction to complete is 5 seconds.  Transactions exceeding this limit should be considered failed and rolled back.

**Input:**

A dictionary containing order details, including customer ID, item IDs, quantities, and payment information. Example:

```python
order_data = {
    "customer_id": "user123",
    "items": [{"item_id": "productA", "quantity": 2}, {"item_id": "productB", "quantity": 1}],
    "payment_info": {"card_number": "XXXX-XXXX-XXXX-1234", "expiry_date": "12/24", "cvv": "123"},
}
```

**Output:**

A dictionary indicating the success or failure of the transaction. If successful, the dictionary should include the order ID. If failed, it should include an error message and the reason for the failure.  Example (success):

```python
{"status": "success", "order_id": "order456"}
```

Example (failure):

```python
{"status": "failure", "error": "Payment failed", "reason": "Insufficient funds"}
```

**Bonus Challenges:**

*   Implement a deadlock detection mechanism to prevent deadlocks during resource reservation in the `InventoryService`.
*   Implement a compensation mechanism to handle partial failures during rollback. For example, if the `InventoryService` fails to restock items during rollback, you need a mechanism to retry or escalate the issue.
*   Design a mechanism for handling long-running transactions that might exceed the 5-second timeout limit.  Consider splitting the transaction into smaller, independent steps.
