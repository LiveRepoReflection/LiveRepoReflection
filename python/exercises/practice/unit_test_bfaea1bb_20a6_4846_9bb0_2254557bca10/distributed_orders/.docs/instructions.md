## Question: Distributed Transaction Orchestration

**Problem Description:**

You are tasked with designing and implementing a distributed transaction orchestration system for a simplified e-commerce platform. The platform consists of three microservices: `OrderService`, `InventoryService`, and `PaymentService`.

*   `OrderService`: Responsible for creating and managing customer orders.
*   `InventoryService`: Manages the inventory of products.
*   `PaymentService`: Processes customer payments.

When a customer places an order, the following steps must occur atomically across these services:

1.  `OrderService` creates a pending order.
2.  `InventoryService` reserves the requested quantity of products from the inventory.
3.  `PaymentService` attempts to authorize the payment.
4.  If all steps succeed, `OrderService` confirms the order, `InventoryService` commits the inventory reservation, and `PaymentService` captures the payment.
5.  If any step fails, all preceding steps must be rolled back. `OrderService` cancels the pending order, `InventoryService` releases the reserved inventory, and `PaymentService` voids the authorization.

**Input:**

A dictionary containing the following keys:

*   `user_id`: An integer representing the user placing the order.
*   `order_id`: A unique string identifying the order.
*   `items`: A list of dictionaries, where each dictionary represents an item in the order and contains:
    *   `product_id`: An integer representing the product ID.
    *   `quantity`: An integer representing the quantity ordered.
*   `payment_info`: A dictionary containing payment details (e.g., credit card number, expiry date, amount).

**Output:**

A boolean value: `True` if the order was successfully processed (committed), `False` if the order failed (rolled back).

**Constraints and Requirements:**

*   **Atomicity:** The entire order processing must be atomic. Either all steps succeed, or all steps are rolled back.
*   **Isolation:** Concurrent order processing should not interfere with each other.  Implement appropriate concurrency control.
*   **Durability:** Once an order is committed, it should survive system failures.
*   **Idempotency:** The system should be able to handle duplicate order requests gracefully. If the same order is received multiple times, it should only be processed once (or rolled back if it previously failed).
*   **Service Failures:**  Simulate potential service failures (e.g., `InventoryService` or `PaymentService` being temporarily unavailable or rejecting the request). Your solution must handle these failures gracefully and attempt retries (with exponential backoff) before ultimately rolling back the transaction. You need to implement a retry mechanism to handle transient failures.
*   **Compensation:** Implement compensation logic (rollback procedures) for each service.
*   **Optimization:** Minimize the overall latency of the order processing.
*   **No External Libraries:** You are restricted to Python's built-in libraries only. No external packages (like `celery`, `dask`, or transaction managers) are allowed. This forces you to implement the transaction orchestration logic from scratch.

**Simulated Services:**

You are provided with simplified, unreliable simulated versions of the `InventoryService` and `PaymentService` that can randomly fail or introduce delays. These services will be mocked with predefined functions that you can call. Assume the `OrderService` is reliable and implemented within your solution. You do NOT need to implement the real services, but rather use simulated services to test your transaction orchestration logic.

**Error Handling:**

Your solution must handle all possible errors gracefully, including invalid input data, service failures, and concurrency conflicts.  Provide informative error messages or logging.

**Concurrency:**

The system must support concurrent order processing. Use appropriate threading or asynchronous programming techniques to achieve concurrency.

**Evaluation Criteria:**

*   **Correctness:** Your solution must correctly process orders and maintain data consistency across the services.
*   **Robustness:** Your solution must handle service failures and other errors gracefully.
*   **Performance:** Your solution should minimize the overall latency of order processing.
*   **Code Quality:** Your code should be well-structured, readable, and maintainable.
*   **Concurrency Handling:** Your solution should handle concurrent requests safely and efficiently.
