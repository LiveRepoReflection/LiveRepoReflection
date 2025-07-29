## Problem: Distributed Transaction Manager

**Description:**

You are tasked with designing and implementing a simplified, in-memory Distributed Transaction Manager (DTM). This DTM will coordinate transactions across multiple independent services.  Each service exposes an interface to perform local operations, and these local operations must be executed atomically across all participating services.

**Core Concepts:**

*   **Transaction:** A sequence of operations that must be treated as a single, indivisible unit of work. Either all operations succeed, or none succeed.
*   **Distributed Transaction:** A transaction that involves operations on multiple, independent services.
*   **Two-Phase Commit (2PC):** A protocol used to ensure atomicity in distributed transactions. It involves two phases:
    *   **Prepare Phase:** The DTM asks each participating service to prepare to commit the transaction. Each service performs necessary checks (e.g., resource availability, data validation) and responds with either a "prepare success" or "prepare failure".
    *   **Commit Phase:** If all services prepared successfully, the DTM instructs all services to commit the transaction. If any service failed to prepare, the DTM instructs all services to rollback.
*   **Rollback:** If a transaction fails, all participating services must undo any changes they made as part of the transaction, ensuring data consistency.

**Services:**

Assume you have a collection of `Service` objects. Each `Service` provides the following interface:

```java
interface Service {
    String getName();
    boolean prepare(TransactionContext transactionContext, String operation);
    boolean commit(TransactionContext transactionContext, String operation);
    boolean rollback(TransactionContext transactionContext, String operation);
}
```

Where:

*   `getName()`: Returns the unique name of the service.
*   `prepare(TransactionContext transactionContext, String operation)`:  Called by the DTM during the prepare phase. The service should validate the `operation` and return `true` if it can commit, `false` otherwise.
*   `commit(TransactionContext transactionContext, String operation)`:  Called by the DTM during the commit phase. The service should execute the `operation` and return `true` if successful.
*   `rollback(TransactionContext transactionContext, String operation)`: Called by the DTM during the rollback phase. The service should undo any changes made by the `operation` and return `true` if successful.
*   `TransactionContext`: A simple class to hold transaction-specific information (e.g., transaction ID).

**Your Task:**

Implement a `DistributedTransactionManager` class with the following public methods:

```java
class DistributedTransactionManager {
    DistributedTransactionManager(List<Service> services);
    boolean executeTransaction(List<Operation> operations); //Operations that need to be performed atomically across all services.
}

class Operation {
    String serviceName;
    String operationDetails;
    //Constructor and getters
}
```

Where:

*   `DistributedTransactionManager(List<Service> services)`: Constructor that takes a list of participating services.
*   `executeTransaction(List<Operation> operations)`: Executes a distributed transaction across the specified services. It should follow the 2PC protocol. The method should return `true` if the entire transaction was successfully committed, and `false` otherwise.

**Constraints and Edge Cases:**

1.  **Concurrency:** Your DTM should be thread-safe.  Multiple transactions might be executed concurrently.  Use appropriate synchronization mechanisms to prevent race conditions and ensure data consistency.
2.  **Timeouts:**  Implement timeouts for the prepare and commit/rollback phases. If a service does not respond within a specified timeout, the DTM should consider the operation failed. Assume the service is unavailable.
3.  **Idempotency:** The commit and rollback operations on the services might be called multiple times. Ensure that your implementation handles this gracefully (i.e., committing or rolling back multiple times has the same effect as committing or rolling back once).
4.  **Logging:** Implement basic logging to track the progress of transactions and any errors that occur.
5.  **Service Failure:**  Simulate service failures. If a service fails during the commit or rollback phase, the DTM should retry the operation a limited number of times.  If the operation still fails, log the error and continue.
6.  **Deadlock:** Consider the potential for deadlock if multiple transactions are trying to access the same resources on different services. While a full deadlock detection/resolution is beyond the scope, try to minimize the chances of deadlock.
7.  **Resource Management:**  Avoid resource leaks (e.g., threads, connections).  Clean up resources properly after a transaction completes, regardless of success or failure.
8.  **Scalability:**  While this is an in-memory implementation, consider the scalability implications of your design.  How would your design need to change to handle a large number of services and concurrent transactions?

**Optimization Requirements:**

*   **Performance:** Minimize the latency of transactions.  Optimize the communication between the DTM and the services.
*   **Resource Utilization:** Minimize the CPU and memory usage of the DTM.

**Grading Criteria:**

*   Correctness: The DTM must correctly implement the 2PC protocol and ensure atomicity.
*   Robustness: The DTM must handle concurrency, timeouts, service failures, and idempotency.
*   Performance: The DTM must execute transactions efficiently.
*   Code Quality: The code must be well-structured, well-documented, and easy to understand.

This problem requires a deep understanding of distributed systems concepts, concurrency, and error handling. It challenges you to design and implement a robust and efficient DTM that can handle a variety of real-world scenarios. Good luck!
