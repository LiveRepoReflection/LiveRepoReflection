## Question: Distributed Transaction Manager

### Project Name: `distributed-transaction-manager`

### Question Description:

You are tasked with designing and implementing a simplified, in-memory Distributed Transaction Manager (DTM) for a microservices architecture. The goal is to ensure Atomicity, Consistency, Isolation, and Durability (ACID) properties across multiple services during a transaction.

**Scenario:** Imagine an e-commerce platform where placing an order involves multiple microservices: `InventoryService`, `PaymentService`, and `OrderService`. A successful order placement requires the following steps:

1.  `InventoryService`: Reserve the required quantity of items in the inventory.
2.  `PaymentService`: Process the payment from the customer.
3.  `OrderService`: Create the order record in the order database.

If any of these steps fail, the entire transaction must be rolled back to maintain data consistency.

**Your Task:**

Implement a `DistributedTransactionManager` class with the following functionalities:

1.  **Transaction Definition:** Allow defining a transaction as a sequence of operations (commands) to be executed across different services. Each operation should be represented as a Java `Runnable` that interacts with a specific service.

2.  **Two-Phase Commit (2PC) Protocol:** Implement a 2PC protocol to coordinate the transaction across participating services. This involves:

    *   **Prepare Phase:** The DTM sends a "prepare" request to all participating services, asking them to tentatively execute their assigned operation and indicate whether they can successfully commit. Each service should either respond with a "prepared" (ready to commit) or an "abort" (cannot commit) signal.
    *   **Commit/Rollback Phase:** If all services respond with "prepared," the DTM sends a "commit" request to all services, instructing them to permanently apply the changes. If any service responds with "abort" (or doesn't respond within a reasonable timeout), the DTM sends a "rollback" request to all services, instructing them to undo any tentative changes.

3.  **Transaction Logging:** Implement a simple in-memory transaction log to track the state of each transaction (preparing, committing, rolling back, completed). This log should be used to recover from crashes or failures during the transaction execution.

4.  **Concurrency Control:** Ensure that the DTM can handle concurrent transaction requests without data corruption or race conditions. Use appropriate synchronization mechanisms (e.g., locks, semaphores) to protect shared resources.

5.  **Timeout Handling:** Implement timeout mechanisms for both the prepare and commit/rollback phases. If a service doesn't respond within the specified timeout, the DTM should consider the service as failed and initiate a rollback.

**Constraints:**

*   **No external libraries (other than standard Java libraries) are allowed** for transaction management, concurrency control, or logging.  You can use libraries for utility functions like Collections, Lists, Maps, etc.
*   **Implement an in-memory solution** for simplicity. Don't use any actual database or external services. Simulate service interactions using mock objects or simple data structures.
*   **Focus on the core DTM logic:**  You don't need to implement the actual `InventoryService`, `PaymentService`, or `OrderService`.  Instead, create mock implementations that can simulate successful or failed operations.
*   **Error Handling:** Implement robust error handling to gracefully handle unexpected exceptions, network failures, and service unavailability.
*   **Efficiency:** While correctness is paramount, strive for reasonable efficiency in your implementation.  Consider the performance implications of your design choices, especially with respect to concurrency and locking. Aim for minimal lock contention.

**Bonus Challenges:**

*   **Idempotency:** Design your operations to be idempotent, meaning they can be executed multiple times without changing the result beyond the initial application. This is crucial for handling failures and retries in a distributed environment.
*   **Deadlock Detection/Prevention:** Implement a simple deadlock detection or prevention mechanism to handle potential deadlocks between concurrent transactions.
*   **Optimistic Locking:** Explore using optimistic locking techniques instead of pessimistic locking to improve concurrency.
*   **Implement a simple retry mechanism** for failed operations during the commit phase.
