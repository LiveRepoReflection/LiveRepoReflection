## Project Name

```
distributed-transaction-manager
```

## Question Description

You are tasked with designing and implementing a simplified Distributed Transaction Manager (DTM) in C++. This DTM will coordinate transactions across multiple independent services (simulated by simple data stores in memory).  The goal is to ensure atomicity and consistency across these services, even in the face of potential service failures.

**Scenario:**

Imagine an e-commerce platform where ordering a product involves:

1.  Reserving the item in the Inventory Service.
2.  Creating an order record in the Order Service.
3.  Processing the payment in the Payment Service.

All three operations must succeed for the order to be considered complete. If any one fails, all changes must be rolled back.

**Requirements:**

1.  **Core Functionality:** Implement the `DistributedTransactionManager` class with the following methods:
    *   `begin_transaction()`: Starts a new transaction and returns a unique transaction ID (TID).
    *   `enlist_resource(tid, resource_id, prepare_function, commit_function, rollback_function)`:  Registers a resource (service) with the DTM for a specific transaction.  It takes the transaction ID (`tid`), a unique resource ID (`resource_id`), and three function pointers: `prepare_function`, `commit_function`, and `rollback_function`.  These functions encapsulate the service-specific logic for preparing, committing, and rolling back changes.  These functions take no arguments and return a boolean value indicating success (true) or failure (false).
    *   `commit_transaction(tid)`:  Initiates the commit process for the transaction with the given ID.  It should execute the `prepare_function` for each enlisted resource first. If all `prepare_function` calls succeed, it then executes the `commit_function` for each resource. If any `prepare_function` fails, it must execute the `rollback_function` for all resources, including those whose prepare calls succeeded. The `commit_transaction` function returns true if the overall transaction commits successfully, and false otherwise.
    *   `rollback_transaction(tid)`:  Initiates the rollback process for the transaction with the given ID. It should execute the `rollback_function` for all enlisted resources. The `rollback_transaction` function always returns true (even if individual rollback functions fail).

2.  **Resource Registration:**  The DTM must be able to handle multiple resources (services) participating in the same transaction.  Each resource is identified by a unique `resource_id`.

3.  **Two-Phase Commit (2PC) Protocol:** The DTM must implement a simplified version of the 2PC protocol. This means:
    *   **Prepare Phase:**  Before committing, the DTM must ask each resource to "prepare" for the commit.  This involves executing the `prepare_function`. The resource should perform any necessary checks (e.g., sufficient inventory, valid payment details) to ensure it can commit the transaction.  The `prepare_function` should return `true` if the resource is ready to commit, and `false` otherwise.
    *   **Commit Phase:** If all resources successfully prepare, the DTM tells each resource to "commit" by executing the `commit_function`.
    *   **Rollback Phase:** If any resource fails to prepare, or if there's a general error during the commit phase, the DTM tells each resource to "rollback" by executing the `rollback_function`.

4.  **Transaction Isolation:**  For simplicity, you do *not* need to implement full isolation levels. Assume that resource conflicts are rare and that the functions provided to the DTM are designed to handle basic concurrency issues (e.g., using mutexes internally).

5.  **Failure Handling:** The DTM must gracefully handle failures. Specifically:
    *   If a `prepare_function` returns `false`, the DTM must rollback the entire transaction.
    *   If a `commit_function` or `rollback_function` throws an exception, the DTM should log an error (to `std::cerr`) *and continue attempting to commit/rollback other resources*. The overall `commit_transaction` function should still return `false` if any exception was thrown during the commit phase.  The `rollback_transaction` function will always return `true` regardless of exceptions thrown during the rollback phase.
    * The functions `prepare_function`, `commit_function`, and `rollback_function` should be exception-safe. They should not leak resources or leave the system in an inconsistent state if they throw an exception.

6.  **Concurrency (Optional, but highly recommended for increased difficulty):**  Make the `commit_transaction` and `rollback_transaction` methods thread-safe, allowing multiple transactions to be committed or rolled back concurrently.  This will require careful use of mutexes to protect the internal state of the DTM.

**Constraints:**

*   The `prepare_function`, `commit_function`, and `rollback_function` *must* be implemented using function pointers, not lambdas or `std::function`. This is to simulate interacting with external services that might only provide C-style APIs.
*   The implementation must be efficient. Avoid unnecessary copying of data.
*   The code must be well-structured and easy to understand.
*   The solution must be exception-safe.
*   The maximum number of resources enlisted in a single transaction will not exceed 100.
*   The number of concurrent transactions will not exceed 10.

**Testing:**

You will need to provide a comprehensive set of unit tests to demonstrate the correctness and robustness of your DTM implementation.  Your tests should cover:

*   Successful commits.
*   Rollbacks due to prepare failures.
*   Rollbacks due to exceptions thrown during commit or rollback.
*   Concurrent commits and rollbacks (if you implement concurrency).
*   Edge cases, such as empty transactions (no resources enlisted).

This problem requires a deep understanding of C++, including function pointers, exception handling, thread safety, and data structure design. Good luck!
