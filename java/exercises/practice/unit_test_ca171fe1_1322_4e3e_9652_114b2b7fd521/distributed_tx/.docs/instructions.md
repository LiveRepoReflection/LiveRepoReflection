## Problem Title: Distributed Transaction Manager

### Question Description

You are tasked with designing and implementing a simplified Distributed Transaction Manager (DTM) for a microservices architecture. This DTM will handle transactions spanning multiple services, ensuring atomicity, consistency, isolation, and durability (ACID) properties.

**Scenario:**

Imagine an e-commerce system consisting of the following microservices:

*   **Order Service:** Creates and manages orders.
*   **Payment Service:** Processes payments.
*   **Inventory Service:** Manages product inventory.

A typical transaction involves creating an order, processing the payment, and reserving inventory. If any of these steps fail, the entire transaction should be rolled back to maintain data consistency.

**Your Task:**

Implement a DTM that coordinates transactions across these three services. The DTM should:

1.  **Start a Transaction:** Provide an API to initiate a distributed transaction. The DTM should generate a unique transaction ID (TXID).

2.  **Two-Phase Commit (2PC):** Implement the 2PC protocol to coordinate the transaction.

    *   **Prepare Phase:** The DTM should send a "prepare" message to each participating service (Order, Payment, Inventory) with the TXID and details about the operation they need to perform. Each service should attempt to perform the operation and respond with either "prepared" (if successful) or "abort" (if it fails). The services must ensure that they can rollback the operation until commit or abort message is received.
    *   **Commit/Abort Phase:** If all services respond with "prepared", the DTM sends a "commit" message to all services. If any service responds with "abort", or if a timeout occurs during the prepare phase, the DTM sends an "abort" message to all services. The services need to commit or rollback the operation respectively.

3.  **Transaction Log:** The DTM should maintain a transaction log to track the state of each transaction and ensure durability in case of failures.

4.  **Idempotency:** The DTM and the participating services must be designed to handle duplicate "prepare," "commit," or "abort" messages gracefully.

5.  **Concurrency:** The DTM should support concurrent transactions.

**Constraints and Considerations:**

*   **Simplified Service Interactions:** You do not need to implement the actual Order, Payment, and Inventory services. Instead, you can simulate their behavior using simple methods that return "prepared" or "abort" based on pre-defined success/failure scenarios.
*   **Communication:** You can use in-memory data structures or simple messaging (e.g., queues) for communication between the DTM and the services.  You do NOT need to implement network communication.
*   **Error Handling:** Implement robust error handling, including timeouts, retries (with limited attempts), and deadlock detection.
*   **Performance:** Optimize the DTM for performance. Consider the impact of concurrency and transaction log size.
*   **Scalability:** While a fully scalable solution is not required, consider how the DTM could be scaled in a real-world environment.

**Specific Requirements:**

*   Implement the DTM in Java.
*   Provide classes for:
    *   `TransactionManager`: The main class responsible for managing transactions.
    *   `Transaction`: Represents a distributed transaction with its TXID, state, and participating services.
    *   `TransactionLog`: Manages the transaction log.
    *   `ServiceProxy`: A proxy class to simulate communication with the Order, Payment, and Inventory services. This will contain the logic to either prepare/commit/abort the transaction in memory.
*   Provide methods for:
    *   `begin()`: Starts a new transaction and returns the TXID.
    *   `prepare(TXID, service, operationDetails)`: Sends a prepare message to a service.
    *   `commit(TXID)`: Commits a transaction.
    *   `abort(TXID)`: Aborts a transaction.
    *   `getTransactionStatus(TXID)`: Returns the status of a transaction (e.g., "preparing", "committed", "aborted").

**Example Scenario:**

1.  A client calls `transactionManager.begin()` and receives TXID "123".
2.  The client uses TXID "123" to call `transactionManager.prepare("123", orderService, orderDetails)`, `transactionManager.prepare("123", paymentService, paymentDetails)`, and `transactionManager.prepare("123", inventoryService, inventoryDetails)`.
3.  If all services respond with "prepared", the client calls `transactionManager.commit("123")`.
4.  The DTM sends "commit" messages to all services.
5.  If any service responds with "abort" in step 2, the client calls `transactionManager.abort("123")`.
6.  The DTM sends "abort" messages to all services.

This problem requires a deep understanding of distributed systems concepts, transaction management, and concurrency. It challenges you to design and implement a complex system with multiple interacting components, while considering various failure scenarios and performance optimizations. Good luck!
