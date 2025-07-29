## Question: Distributed Transaction Orchestration

**Problem Description:**

You are building a distributed e-commerce platform that handles a high volume of transactions. A core component of this platform is the order processing system, which involves multiple microservices: `InventoryService`, `PaymentService`, and `ShippingService`.  Each service has its own database and is responsible for a specific part of the order fulfillment process.

When a user places an order, the following steps must occur atomically:

1.  **Inventory Check & Reservation:** `InventoryService` verifies that enough items are in stock and reserves them for the order.
2.  **Payment Authorization:** `PaymentService` authorizes the payment for the order amount.
3.  **Shipping Preparation:** `ShippingService` prepares the shipment based on the order details and calculates the shipping cost.
4.  **Order Confirmation:** If all steps succeed, each service persists its changes and the order is confirmed. If any step fails, all previous steps must be rolled back to maintain data consistency.

Your task is to implement a robust transaction orchestration mechanism using a Saga pattern to ensure atomicity across these microservices.  You are provided with simplified, unreliable versions of each service's API. You must implement a central orchestrator that manages the distributed transaction, handles failures gracefully, and ensures eventual consistency.

**Constraints:**

*   **Idempotency:**  Each service operation (reservation, payment authorization, shipping preparation, and their respective compensations/rollbacks) must be idempotent. The orchestrator might retry operations multiple times due to network issues or service failures.
*   **Concurrency:** Multiple orders can be placed concurrently. Your solution must handle concurrent transactions without data corruption. You may assume that each order has a unique order ID.
*   **Network Unreliability:** Communication between the orchestrator and the microservices is unreliable.  You should implement appropriate retry mechanisms with exponential backoff.
*   **Partial Failures:**  A service might fail during any operation (e.g., payment authorization succeeds, but inventory reservation fails).  Your orchestrator must detect these failures and initiate the appropriate compensation transactions.
*   **Eventual Consistency:** While strong consistency is desirable, it's not always achievable in a distributed system.  Your solution should aim for eventual consistency, meaning that after a series of operations (including compensations), the system should eventually reach a consistent state.
*   **Optimistic Locking**: Assume each database table has a version column, and implement optimistic locking for concurrent updates.

**Input:**

Your solution will receive a stream of order requests, each containing:

*   `order_id`: A unique identifier for the order (string).
*   `user_id`: The ID of the user placing the order (integer).
*   `items`: A list of items in the order, each with `item_id` (string) and `quantity` (integer).
*   `payment_info`: Payment details (e.g., credit card number, expiry date).
*   `shipping_address`: Shipping address details.

**Output:**

For each order request, your solution should output one of the following:

*   `"Order <order_id> confirmed"` if the order is successfully processed.
*   `"Order <order_id> failed"` if the order processing fails after multiple retries and compensations.

**Example:**

```
Input:
Order 123, User 456, Items: [{A, 2}, {B, 1}], Payment: CreditCard, Address: ...
Order 456, User 789, Items: [{C, 1}], Payment: PayPal, Address: ...

Output:
Order 123 confirmed
Order 456 failed
```

**Grading Criteria:**

*   **Correctness (70%):**  The solution must correctly process orders, ensuring atomicity and data consistency across microservices.
*   **Fault Tolerance (20%):** The solution must handle service failures, network issues, and concurrency gracefully.
*   **Efficiency (10%):** The solution should minimize the number of retries and compensations required to process an order.

This problem requires careful consideration of distributed systems principles, data consistency, and fault tolerance. Good luck!
