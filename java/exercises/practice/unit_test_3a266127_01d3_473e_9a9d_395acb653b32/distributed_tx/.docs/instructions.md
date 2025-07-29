## Problem: Distributed Transaction Manager

**Description:**

You are tasked with designing and implementing a simplified, in-memory distributed transaction manager for a system composed of multiple independent services. Each service manages its own local data and exposes an API to perform operations. To maintain data consistency across services, transactions need to span multiple services.

Your transaction manager should provide ACID (Atomicity, Consistency, Isolation, Durability) properties, focusing on atomicity and isolation. Since we are focusing on a simplified, in-memory system, durability can be achieved through regular snapshots (not part of this coding problem).

**System Architecture:**

Imagine a system consisting of `n` services, each identified by a unique ID (an integer between 0 and n-1). Each service has a limited set of operations it can perform, represented by simple data manipulation.

**The Challenge:**

Implement a `TransactionManager` class in Java that can orchestrate distributed transactions across these services. The `TransactionManager` should provide the following functionalities:

1.  **Begin Transaction:** Start a new transaction. The transaction manager assigns a unique transaction ID (TID) to the transaction.

2.  **Register Operation:** Register an operation on a specific service within the current transaction. The operation is represented by a `Callable<Boolean>` that executes the desired action on the service.  The `Boolean` return type indicates whether the operation was successful.

3.  **Commit Transaction:** Attempt to commit the current transaction. The transaction manager should execute all registered operations. If all operations succeed (return `true`), the transaction is committed, and the changes are considered permanent. If any operation fails (returns `false`) or throws an exception, the transaction is rolled back.

4.  **Rollback Transaction:** Rollback the current transaction. The transaction manager should undo all operations that were executed as part of the transaction. Each service must provide a rollback `Callable<Boolean>` for each operation registered in the transaction.

**Constraints and Requirements:**

*   **Atomicity:** All operations within a transaction must either succeed or fail as a single unit. If any operation fails, all operations must be rolled back.
*   **Isolation:**  While a transaction is in progress, other transactions should not see the partial changes made by the current transaction.  This can be achieved using in-memory copies of the data within each service.  Specifically, each service should maintain a 'staging area' for changes made within a transaction. Only on successful commit are these staged changes merged into the service's main data.
*   **Concurrency:** The `TransactionManager` must be thread-safe. Multiple transactions can be initiated and executed concurrently.
*   **Idempotency:** Rollback operations must be idempotent.  They should be able to be executed multiple times without causing unintended side effects.
*   **Optimization:** The transaction manager should be designed to minimize the time required to commit or rollback transactions, particularly when dealing with a large number of services and operations. Consider potential parallel execution where appropriate.
*   **Error Handling:** The transaction manager must handle exceptions gracefully. Exceptions thrown by service operations during commit or rollback should be caught and logged, and should not prevent the transaction manager from completing the commit or rollback process.
*   **Service API:** You can assume each service exposes two methods: `execute(Callable<Boolean> operation)` and `rollback(Callable<Boolean> rollbackOperation)`.

**Input/Output:**

The `TransactionManager` does not have specific input files. Instead, it receives operations to register and executes them based on the commit/rollback calls. The `Callable<Boolean>` operations represent the data manipulations performed on each service. The output is the success/failure of the transaction commit. The transaction manager itself should not print anything.

**Example Scenario:**

Imagine two services:

*   **Service 0:** Manages user accounts.  Operations include creating a user, deleting a user, transferring funds.
*   **Service 1:** Manages order processing. Operations include creating an order, updating order status, canceling an order.

A transaction might involve creating a user account in Service 0 *and* creating an initial order for that user in Service 1.  If either operation fails, the entire transaction should be rolled back (user account deleted from Service 0, order creation reverted in Service 1).

**Your Task:**

Implement the `TransactionManager` class and demonstrate how it can be used to manage distributed transactions across a set of services. You do not need to implement the actual services (Service 0, Service 1 above). You can simulate them using simple data structures and operations. The focus is on the `TransactionManager`'s logic.

**Bonus Points:**

*   Implement a deadlock detection mechanism to prevent transactions from getting stuck in a deadlock situation.
*   Implement a two-phase commit protocol for enhanced reliability.
