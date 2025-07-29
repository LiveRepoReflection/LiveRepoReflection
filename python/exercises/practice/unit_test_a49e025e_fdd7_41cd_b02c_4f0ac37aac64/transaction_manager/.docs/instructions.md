## Problem: Distributed Transaction Manager

### Question Description

You are tasked with building a simplified, in-memory distributed transaction manager for a microservice architecture. Imagine a system where multiple services need to participate in a single, atomic transaction.  If all services successfully complete their part of the transaction, the changes are committed. If any service fails, all changes are rolled back.

This problem focuses on implementing the core transaction coordination logic, not the actual database interactions or network communication.

**Scenario:**

You have a set of independent services (represented by unique integer IDs) that need to perform operations as part of a single transaction. Each service can either successfully complete its operation (represented by a "commit" request) or fail (represented by a "rollback" request). The transaction manager must ensure that either all services commit, or all services rollback.

**Requirements:**

Implement a `TransactionManager` class with the following methods:

1.  `begin_transaction(transaction_id: int) -> bool`:
    *   Starts a new transaction with the given `transaction_id`.
    *   Returns `True` if the transaction was successfully started, `False` if a transaction with the same `transaction_id` already exists.
    *   The transaction manager should keep track of participating services for each transaction.

2.  `service_commit(transaction_id: int, service_id: int) -> bool`:
    *   Registers a "commit" request from the service with the given `service_id` for the transaction with `transaction_id`.
    *   Returns `True` if the commit was successfully registered, `False` if the transaction doesn't exist or the service has already committed/rolled back.
    *   If all participating services have committed, the transaction manager should automatically commit the entire transaction (internally).

3.  `service_rollback(transaction_id: int, service_id: int) -> bool`:
    *   Registers a "rollback" request from the service with the given `service_id` for the transaction with `transaction_id`.
    *   Returns `True` if the rollback was successfully registered, `False` if the transaction doesn't exist or the service has already committed/rolled back.
    *   If any service rolls back, the transaction manager should automatically rollback the entire transaction (internally).

4.  `get_transaction_status(transaction_id: int) -> str`:
    *   Returns the current status of the transaction with `transaction_id`.
    *   Possible return values:
        *   `"PENDING"`: The transaction is still in progress (not all services have committed or rolled back).
        *   `"COMMITTED"`: The transaction has been successfully committed.
        *   `"ROLLED_BACK"`: The transaction has been rolled back.
        *   `"NON_EXISTENT"`: The transaction does not exist.

5. `register_participant(transaction_id: int, service_id: int) -> bool`:
    * Registers a service with the `service_id` to the transaction with `transaction_id`.
    * Returns `True` if the registration was successful, `False` if the transaction doesn't exist, or the service is already registered.

**Constraints:**

*   Transaction IDs and Service IDs are integers.
*   The transaction manager should be thread-safe. Multiple services can call the methods concurrently.
*   The number of services participating in a transaction is not known beforehand and can vary.
*   Once a transaction is committed or rolled back, no further operations (commit, rollback, or register participant) are allowed for that transaction.
*   The transaction manager should handle a large number of concurrent transactions efficiently.
*   The system should be designed to minimize contention and locking overhead.
*   Assume that you cannot directly communicate between services to orchestrate the transaction. All coordination happens through the transaction manager.

**Optimization Requirements:**

*   Optimize for read operations (`get_transaction_status`).  These operations should be as fast as possible.
*   Minimize the time it takes to commit a transaction once all participating services have committed.

**Edge Cases to Consider:**

*   Duplicate commit/rollback requests from the same service.
*   Commit/rollback requests before a service has registered as a participant.
*   Registering a participant after the transaction has already started.
*   Concurrent calls to `begin_transaction` with the same transaction ID.

This problem challenges your ability to design and implement a concurrent, efficient, and robust distributed transaction manager, considering various edge cases and optimization requirements. Good luck!
