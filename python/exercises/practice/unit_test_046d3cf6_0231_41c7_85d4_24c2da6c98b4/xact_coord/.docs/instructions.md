## Question: Distributed Transaction Orchestration

### Question Description

You are tasked with designing a distributed transaction orchestration system. Imagine a microservices architecture where multiple services need to participate in a single, atomic transaction. If any service fails to commit its part of the transaction, the entire transaction must be rolled back to maintain data consistency.

Specifically, you need to implement a transaction coordinator that can handle a series of operations across different services. Each service exposes an API endpoint that accepts a transaction ID and a command to either "prepare", "commit", or "rollback".

The system must adhere to the following constraints:

1.  **Atomicity:** All operations within a transaction must either succeed or fail together.
2.  **Consistency:** The system must maintain data consistency across all participating services.
3.  **Isolation:** Concurrent transactions must not interfere with each other.
4.  **Durability:** Once a transaction is committed, the changes must be persistent even in the face of system failures.
5.  **Scalability:** The system should be able to handle a large number of concurrent transactions.
6.  **Idempotency:** Services should be able to handle duplicate "prepare", "commit", or "rollback" requests without causing any unintended side effects. This is essential for handling network issues and ensuring reliable execution.
7.  **Timeout and Retries:** The coordinator must implement appropriate timeout mechanisms and retry strategies to handle temporary service unavailability. If a service fails to respond within a reasonable time, the coordinator should retry the operation a certain number of times before considering the service unavailable.
8.  **Deadlock Detection:** Design the system to prevent deadlocks between transactions. If a deadlock is detected, the system should resolve it by aborting one or more transactions.
9.  **Error Handling:** Robust error handling is crucial. The coordinator must be able to gracefully handle various error scenarios, such as service failures, network errors, and invalid requests.

**Input:**

The input consists of a list of services, each with its URL and the operations it needs to perform within a transaction. Each operation includes a unique transaction ID and a command ("prepare", "commit", or "rollback").

**Output:**

The output should indicate whether the transaction was successfully committed or rolled back. If the transaction fails, provide a detailed error message indicating the reason for the failure. The system should also log all operations performed and their outcomes for auditing and debugging purposes.

**Example:**

Assume three services: `inventory-service`, `payment-service`, and `shipping-service`. A transaction might involve reserving items in the `inventory-service`, processing payment in the `payment-service`, and creating a shipment in the `shipping-service`. If the payment fails, the system must roll back the inventory reservation and cancel the shipment creation.

**Challenge:**

Implement the transaction coordinator in Python, using appropriate data structures and algorithms to ensure the system meets all the specified constraints. Pay close attention to concurrency, error handling, and idempotency. You should also consider the trade-offs between different approaches to deadlock detection and resolution.
