## Question: Distributed Transaction Orchestration

**Problem Description:**

You are tasked with designing and implementing a distributed transaction orchestration system for a microservices architecture. This system needs to ensure data consistency across multiple independent services when a single business transaction spans these services.

Imagine an e-commerce system where placing an order involves several steps:

1.  **Order Service:** Creates a new order record.
2.  **Inventory Service:** Reserves the required quantity of items from the inventory.
3.  **Payment Service:** Processes the payment for the order.
4.  **Shipping Service:** Schedules the shipment of the order.

Each of these services has its own database and operates independently. A successful order requires all these operations to succeed. If any step fails, all previous steps must be rolled back to maintain consistency.

**Requirements:**

*   **Atomicity:** Ensure that either all operations within the transaction succeed, or none of them do.
*   **Consistency:** The transaction must maintain the integrity of the data across all services.
*   **Isolation:** Concurrent transactions should not interfere with each other.
*   **Durability:** Once a transaction is committed, the changes must be permanent, even in the face of system failures.
*   **Idempotency:** Each service operation must be idempotent. Meaning, executing the same operation multiple times has the same effect as executing it once. This is crucial for handling retries in a distributed environment.
*   **Scalability:** The system should be able to handle a large number of concurrent transactions.
*   **Fault Tolerance:** The system should be resilient to service failures and network issues.

**Input:**

You are given a list of services involved in a transaction, along with the operations to be performed on each service (e.g., `[("OrderService", "createOrder", order_details), ("InventoryService", "reserveItems", item_details), ...]`). Assume each service exposes an API endpoint to perform the operation and another endpoint to compensate (rollback) the operation.

**Output:**

Your solution should orchestrate the transaction across the services and return a boolean value indicating whether the transaction was successful (True) or not (False). If the transaction fails, all completed operations must be compensated to revert the system to its initial state.

**Constraints:**

*   **Network Unreliability:** Assume the network between services is unreliable and prone to failures.
*   **Service Unavailability:** Services may become temporarily unavailable.
*   **Concurrency:** Multiple transactions may be initiated concurrently.
*   **Maximum Execution Time:** Each operation and its compensation must complete within a defined timeout (e.g., 10 seconds).  If the timeout expires, the operation should be considered failed.
*   **Limited Retries:** Implement a limited retry mechanism for failed operations and compensations (e.g., maximum 3 retries).
*   **No Global Transaction Manager:** You cannot rely on a global transaction manager (like XA) to coordinate the transactions.  You must implement a custom orchestration mechanism.

**Considerations:**

*   Choose an appropriate distributed transaction pattern (e.g., Saga pattern).
*   Consider using a message queue (e.g., RabbitMQ, Kafka) for asynchronous communication between services. (This is not strictly enforced, but is highly recommended for solving the problem.)
*   Think about how to handle conflicting compensations (e.g., two transactions trying to compensate the same operation).
*   Prioritize correctness and fault tolerance over absolute performance.  The system must reliably maintain data consistency even under adverse conditions.
*   Explain the trade-offs of your chosen approach.

This problem requires a good understanding of distributed systems concepts, concurrency control, and fault tolerance. Good luck!
