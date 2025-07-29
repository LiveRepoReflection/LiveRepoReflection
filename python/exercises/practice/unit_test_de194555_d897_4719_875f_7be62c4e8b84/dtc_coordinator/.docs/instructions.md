## Question Title: Distributed Transaction Coordinator

### Question Description

You are tasked with designing and implementing a simplified, in-memory distributed transaction coordinator (DTC) for a system comprising multiple independent microservices. These microservices need to perform operations that must either all succeed or all fail together, ensuring data consistency across the system.

**Scenario:**

Imagine an e-commerce platform where placing an order involves several microservices: `InventoryService`, `PaymentService`, and `OrderService`. When a user places an order, the following steps must occur atomically:

1.  `InventoryService` must decrement the stock of the ordered items.
2.  `PaymentService` must authorize and capture the payment from the user.
3.  `OrderService` must create a new order record.

If any of these steps fail, all the preceding steps must be rolled back to maintain consistency.

**Your Task:**

Implement a `TransactionCoordinator` class with the following functionalities:

1.  **`begin_transaction()`**: Starts a new transaction and returns a unique transaction ID (TXID).
2.  **`register_participant(txid, participant)`**: Registers a microservice participant with the coordinator for a specific transaction. Each participant is expected to be an object implementing a specific interface (details below).
3.  **`commit_transaction(txid)`**: Attempts to commit the transaction. This involves coordinating with all registered participants to perform their respective commit operations. If all participants successfully commit, the transaction is considered successful.
4.  **`rollback_transaction(txid)`**: Rolls back the transaction if any participant fails to commit or if explicitly requested.
5.  **`get_transaction_status(txid)`**: Returns the status of the transaction (e.g., "PENDING", "COMMITTED", "ABORTED").

**Participant Interface:**

Each microservice participant must implement the following interface:

*   `prepare()`: This method is called by the coordinator to prepare the participant for committing. The participant should perform any necessary checks (e.g., verify sufficient inventory, validate payment details) and return `True` if ready to commit, and `False` otherwise.
*   `commit()`: This method is called when the transaction is being committed. The participant should perform its actual operation (e.g., decrement inventory, capture payment) and return `True` if successful, and `False` otherwise.
*   `rollback()`: This method is called when the transaction is being rolled back. The participant should undo any changes made during the transaction (e.g., restore inventory, void payment). It should return `True` if successful and `False` otherwise.

**Constraints and Requirements:**

*   **Atomicity:** The transaction must be atomic; either all participants commit successfully, or all participants roll back.
*   **Durability:** Although this is an in-memory implementation, consider how durability would be achieved in a real-world system (e.g., logging, persistent storage). Briefly describe your approach in comments within the code.
*   **Concurrency:** The `TransactionCoordinator` must be thread-safe, allowing multiple concurrent transactions to be managed simultaneously.
*   **Idempotency:** The `commit()` and `rollback()` operations should be idempotent, meaning that they can be safely executed multiple times without causing unintended side effects. This is crucial for handling potential network issues and retries.
*   **Error Handling:** The coordinator must handle participant failures gracefully, ensuring that all participants are rolled back if any participant fails.
*   **Optimization:** Minimize the time it takes to complete commit and rollback operations, considering the overhead of coordinating with multiple participants.
*   **Scalability Considerations:** The system will be scaled out to hundreds of microservices. Think about how the design can be made scalable.

**Input/Output:**

*   The input consists of a series of operations (begin, register, commit, rollback, status) with associated data (TXID, participant objects).
*   The output consists of the status of transactions and the return values of participant operations.

**Example:**

```python
coordinator = TransactionCoordinator()
txid = coordinator.begin_transaction()

inventory_service = InventoryService() #Implements the participant interface
payment_service = PaymentService() #Implements the participant interface

coordinator.register_participant(txid, inventory_service)
coordinator.register_participant(txid, payment_service)

if coordinator.commit_transaction(txid):
    print("Transaction committed successfully.")
else:
    print("Transaction failed and rolled back.")
```

**Judging Criteria:**

*   Correctness: The implementation must correctly implement the distributed transaction protocol and ensure atomicity.
*   Concurrency: The coordinator must be thread-safe.
*   Efficiency: The implementation should be optimized for performance.
*   Error Handling: The implementation must handle participant failures gracefully.
*   Code Quality: The code must be well-structured, readable, and maintainable.
*   Scalability Discussion: The code must include comments briefly discussing scalability considerations and potential approaches for handling a large number of microservices.

This problem requires a solid understanding of distributed systems concepts, concurrency, and object-oriented design. Good luck!
