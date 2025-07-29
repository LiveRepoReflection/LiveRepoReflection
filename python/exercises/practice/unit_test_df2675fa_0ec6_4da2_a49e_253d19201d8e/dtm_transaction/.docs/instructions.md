Okay, I'm ready to craft a challenging coding problem. Here's the problem statement:

### Project Name

```
Distributed Transaction Manager
```

### Question Description

You are tasked with designing and implementing a simplified distributed transaction manager (DTM) that guarantees atomicity across multiple independent microservices.  Imagine you are building an e-commerce platform, and a single order creation can involve multiple services: Inventory, Payment, and Order. To ensure data consistency, if any of these services fail, the entire order creation process should be rolled back.

Your DTM will interact with these microservices via HTTP requests (you don't need to implement actual microservices, just simulate their behavior).  Each microservice exposes two endpoints: `prepare` and `commit/rollback`.

*   **Prepare:** The DTM sends a `prepare` request to each service.  The service attempts to tentatively perform its part of the transaction (e.g., reserve inventory, authorize payment).  If successful, it responds with a `200 OK`. If it fails (e.g., insufficient inventory, payment declined), it responds with a `500 Internal Server Error` with a JSON payload containing an error message.

*   **Commit/Rollback:** If all services successfully prepare, the DTM sends a `commit` request to each service.  The service finalizes its part of the transaction.  If *any* service fails to `prepare`, the DTM sends a `rollback` request to all services. The service reverts any changes made during the prepare phase. Services should respond with a `200 OK` on a successful commit/rollback, and a `500 Internal Server Error` if it fails.

**Specific Requirements:**

1.  **Input:** Your DTM will receive a list of microservice URLs and a payload representing the data for the transaction. The data payload will be a JSON object containing the instructions for the inventory service, the payment service, and the order service.
2.  **Transaction Flow:**
    *   The DTM must first send a `prepare` request with the JSON payload to all microservices concurrently.
    *   If all `prepare` requests succeed (return `200 OK`), the DTM must send a `commit` request to all microservices concurrently.
    *   If any `prepare` request fails (returns `500 Internal Server Error`), the DTM must send a `rollback` request to all microservices concurrently.
3.  **Concurrency:**  The `prepare`, `commit`, and `rollback` operations must be performed concurrently to minimize latency. Use asyncio for achieving concurrency.
4.  **Timeout:**  Implement a timeout mechanism. If a microservice does not respond to a `prepare`, `commit`, or `rollback` request within a specified timeout (e.g., 5 seconds), the DTM should consider the operation a failure and proceed with rollback (if in the prepare phase) or log an error (if in the commit phase after a successful prepare).
5.  **Idempotency:**  Ensure that the `commit` and `rollback` operations are idempotent.  If a service receives the same `commit` or `rollback` request multiple times, it should only perform the operation once.  Implement a basic mechanism to track already-processed transaction IDs to ensure idempotency. Assume each request contains a `transaction_id` field.
6. **Error Handling:**  Implement robust error handling.  If a `commit` operation fails *after* all `prepare` operations succeeded, log the error, retry the commit a limited number of times (e.g., 3 retries with exponential backoff), and if it still fails, mark the transaction as "failed" and potentially alert an administrator.

**Constraints:**

*   You can use the `requests` library or `aiohttp` for making HTTP requests.
*   You need to simulate microservice behavior. This simulation can be done by creating mock functions that return specific HTTP responses (200, 500) based on pre-defined conditions or random chance.
*   The number of microservices involved in a transaction can vary.
*   The microservices may reside on different network locations, potentially increasing latency.

**Bonus (Optional):**

*   Implement a retry mechanism for `prepare` operations with exponential backoff.
*   Implement a basic logging system to record the progress and outcomes of transactions.

This problem requires a good understanding of distributed systems concepts, concurrency, error handling, and idempotency. It also tests the ability to write clean, well-structured, and maintainable code. Good luck!
