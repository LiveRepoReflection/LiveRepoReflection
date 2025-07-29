## Problem: Distributed Transaction Manager

### Question Description

You are tasked with designing and implementing a simplified distributed transaction manager (DTM) for a microservices architecture. The goal is to ensure atomicity across multiple services when a single business operation requires modifications in each service. In the context of this problem, we'll focus on a scenario involving an e-commerce platform with two services: an Inventory Service and an Order Service.

A customer places an order. This action necessitates:

1.  Decrementing the stock count of the ordered item in the Inventory Service.
2.  Creating a new order record in the Order Service.

Both actions must succeed or fail together to maintain data consistency. If the inventory update succeeds but the order creation fails, or vice versa, the system should roll back the successful operation.

**Specific Requirements:**

1.  **Transaction Coordination:** Implement a DTM that coordinates transactions across the Inventory Service and the Order Service.
2.  **Two-Phase Commit (2PC) Protocol:** The DTM should employ the 2PC protocol to ensure atomicity.
3.  **Concurrency Handling:** The DTM must handle concurrent transactions and prevent data corruption. Assume both services use optimistic locking, and the DTM must handle service-level transaction retries.
4.  **Failure Handling:** The DTM must be resilient to failures. Implement appropriate retry mechanisms and timeout strategies to handle transient errors. If failures persist beyond a threshold, the DTM should initiate a rollback.
5.  **Idempotency:**  The services are NOT guaranteed to be idempotent. Design the DTM to handle potential non-idempotency issues, especially during the commit/rollback phases.
6.  **Scalability:**  While focusing on the core functionality, consider the scalability implications of your design.  How would your design adapt if you needed to support a significantly larger number of services involved in a transaction?
7. **Performance:** While correctness is paramount, strive for a design that minimizes latency and resource consumption. Consider the overhead introduced by the 2PC protocol and explore potential optimizations within its constraints.

**Constraints:**

*   You are provided with simplified interfaces for the Inventory Service and the Order Service (see below). You cannot modify these interfaces.
*   Assume reliable message delivery between the DTM and the services (e.g., using a message queue).
*   Focus on the core logic of the DTM and the 2PC protocol. You don't need to implement the actual network communication or message queue infrastructure.
*   The number of services participating in a transaction is known upfront by the DTM.
*   Assume only one DTM instance exists in the system.

**Inventory Service Interface (Provided):**

```java
interface InventoryService {
    /**
     * Attempts to decrement the stock of the item by the specified quantity.
     * @param itemId The ID of the item.
     * @param quantity The quantity to decrement.
     * @param transactionId The unique ID of the transaction.
     * @return true if the decrement was successful, false otherwise (e.g., due to insufficient stock or optimistic lock failure).
     * @throws ServiceUnavailableException if the service is temporarily unavailable.
     */
    boolean decrementStock(String itemId, int quantity, String transactionId) throws ServiceUnavailableException;

    /**
     * Attempts to compensate for a previous decrementStock operation.
     * @param itemId The ID of the item.
     * @param quantity The quantity to increment back.
     * @param transactionId The unique ID of the transaction.
     * @throws ServiceUnavailableException if the service is temporarily unavailable.
     */
    void compensateDecrementStock(String itemId, int quantity, String transactionId) throws ServiceUnavailableException;
}
```

**Order Service Interface (Provided):**

```java
interface OrderService {
    /**
     * Attempts to create a new order record.
     * @param orderDetails The details of the order.
     * @param transactionId The unique ID of the transaction.
     * @return true if the order creation was successful, false otherwise (e.g., due to optimistic lock failure or data validation failure).
     * @throws ServiceUnavailableException if the service is temporarily unavailable.
     */
    boolean createOrder(OrderDetails orderDetails, String transactionId) throws ServiceUnavailableException;

    /**
     * Attempts to compensate for a previous createOrder operation by deleting the order record.
     * @param orderId The ID of the order to delete.
     * @param transactionId The unique ID of the transaction.
     * @throws ServiceUnavailableException if the service is temporarily unavailable.
     */
    void compensateCreateOrder(String orderId, String transactionId) throws ServiceUnavailableException;
}

record OrderDetails(String itemId, int quantity, String customerId) {}

class ServiceUnavailableException extends Exception {}
```

**Deliverables:**

1.  Implement the `DistributedTransactionManager` class.
2.  Explain your design choices and the rationale behind them, especially regarding concurrency handling, failure handling, idempotency, and scalability.
3.  Analyze the performance implications of your design and suggest potential optimizations.

This problem requires a strong understanding of distributed systems concepts, transaction management, and concurrency control. A well-designed solution should be robust, scalable, and performant. Good luck!
