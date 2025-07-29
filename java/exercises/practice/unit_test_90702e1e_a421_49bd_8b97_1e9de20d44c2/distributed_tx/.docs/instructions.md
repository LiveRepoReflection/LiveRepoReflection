## Question: Distributed Transaction Manager

### Question Description

You are tasked with designing and implementing a simplified distributed transaction manager (DTM) for a microservices architecture. The system needs to ensure atomicity and consistency across multiple services when updating data in a distributed environment.

Imagine a scenario where an e-commerce application processes orders.  Placing an order involves multiple services:

1.  **Order Service:** Creates the order record.
2.  **Inventory Service:** Reserves the items in the order.
3.  **Payment Service:** Processes the payment.
4.  **Shipping Service:** Schedules the shipment.

All these operations must succeed or fail together. If any operation fails (e.g., insufficient inventory, payment failure), the entire transaction should be rolled back to maintain data consistency.

**Requirements:**

*   **Atomicity:** All operations in the transaction either succeed completely, or all are rolled back as if they never happened.
*   **Consistency:** The system must transition from one valid state to another.
*   **Durability:** Once a transaction is committed, the changes are permanent and survive system failures. (Assume a persistent log is available for the DTM.)
*   **Isolation:**  Transactions should be isolated from each other to prevent data corruption due to concurrent transactions. For this simplified version, you don't need to implement full isolation levels, but ensure that concurrent transactions don't interfere with each other in a way that would compromise atomicity.

**The DTM should provide the following functionalities:**

1.  **Transaction Initiation (`begin()`):**  Initiates a new distributed transaction and returns a unique transaction ID (TXID).
2.  **Participant Registration (`enlist(TXID, service, operation, data)`):**  Registers a service as a participant in the transaction.  The `service` is a string identifying the service (e.g., "OrderService"). The `operation` is a string describing the operation to be performed (e.g., "createOrder"). The `data` is a string containing the data required for the operation.
3.  **Transaction Commit (`commit(TXID)`):**  Initiates the commit process for the transaction. The DTM will coordinate the commit across all registered participants.
4.  **Transaction Rollback (`rollback(TXID)`):**  Initiates the rollback process for the transaction. The DTM will coordinate the rollback across all registered participants.
5.  **Idempotency:** Implement idempotency for the commit and rollback operations. If a service receives the same commit or rollback request multiple times for the same transaction, it should only execute the operation once.

**Service Interaction (Simulated):**

You don't need to implement actual network calls to separate services. Instead, you'll simulate service behavior using a provided `ServiceRegistry`. The `ServiceRegistry` will have methods to simulate successful or failed operations for each service.  The DTM will interact with the `ServiceRegistry` to execute the operations and rollbacks.

**Constraints:**

*   The DTM must handle concurrent transactions.
*   The DTM must be resilient to service failures. If a service fails during the commit phase, the DTM should attempt to retry the commit operation (within a reasonable number of retries). If retries fail, the DTM must rollback the entire transaction.
*   The DTM must handle situations where a service is temporarily unavailable.
*   The `ServiceRegistry` is given and cannot be modified. It simulates the underlying services.

**Assumptions:**

*   You are given a `ServiceRegistry` class (code not provided here, but it simulates calling actual services). It has methods like `execute(service, operation, data)` and `compensate(service, operation, data)` that can either succeed or fail (randomly for the purposes of testing).
*   You can use any suitable data structure for storing transaction metadata.
*   Error handling and logging are essential. Provide meaningful error messages.
*   Assume all communication within the DTM is reliable.
*   Assume a simple persistent log is available to record transaction states, like `TransactionLog.log(TXID, message)`. Persistency of this log will be tested.

**Goal:**

Implement the `DistributedTransactionManager` class with the specified functionalities to ensure atomicity and consistency across multiple services in a distributed transaction. Your implementation must be robust, handle concurrency, and be resilient to service failures. Optimize for performance and minimize the impact of failures.

This problem requires a good understanding of distributed systems concepts, concurrency, error handling, and transaction management principles.  A well-structured, testable, and efficient solution is expected.
