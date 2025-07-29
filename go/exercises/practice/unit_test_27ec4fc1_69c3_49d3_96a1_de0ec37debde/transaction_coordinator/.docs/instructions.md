## Problem: Distributed Transaction Coordinator

**Description:**

You are tasked with implementing a simplified, distributed transaction coordinator for a system that manages reservations across multiple independent services. Imagine a scenario where a user books a trip involving flights, hotels, and rental cars. Each of these is managed by a separate service (FlightService, HotelService, CarService). To ensure data consistency, the entire booking process must be treated as a single atomic transaction: either all reservations succeed, or none of them do.

Your task is to implement a `TransactionCoordinator` that orchestrates the two-phase commit (2PC) protocol across these services. Each service exposes a simple interface: `Prepare(transactionID)` to check if it can commit the reservation, and `Commit(transactionID)` or `Rollback(transactionID)` to finalize or cancel the reservation.

**Specifics:**

1.  **Services:** Assume you have access to abstract `Service` interfaces that define the `Prepare`, `Commit`, and `Rollback` methods. Each service has its own independent database and resources. The interface is defined as follows:

    ```go
    type Service interface {
        Prepare(transactionID string) error
        Commit(transactionID string) error
        Rollback(transactionID string) error
    }
    ```

    You do **not** need to implement the services themselves.  You only need to interact with them through this interface. You can mock the `Service` interface for testing.

2.  **Transaction Coordinator:** Implement a `TransactionCoordinator` struct with a `BeginTransaction`, `EndTransaction`, and supporting helper methods. The `TransactionCoordinator` should:

    *   Generate a unique transaction ID for each new transaction.
    *   Implement the 2PC protocol, coordinating with the participating services.
    *   Handle potential failures during the prepare, commit, or rollback phases gracefully.
    *   Ensure that either all services commit or all services rollback.
    *   Be thread-safe.  Multiple transactions might be running concurrently.
    *   Provide configurable timeouts for `Prepare`, `Commit`, and `Rollback` operations.

3.  **2PC Protocol:**

    *   **Prepare Phase:** The coordinator sends a `Prepare` request to all participating services. If all services respond successfully (return `nil` error), the coordinator moves to the commit phase. If any service fails to prepare (returns a non-nil error), the coordinator enters the rollback phase.
    *   **Commit Phase:** If all services prepared successfully, the coordinator sends a `Commit` request to all services.
    *   **Rollback Phase:** If any service failed to prepare, or if a failure occurs during the commit phase, the coordinator sends a `Rollback` request to all services.

4.  **Error Handling:**

    *   Services may return errors during `Prepare`, `Commit`, or `Rollback`.
    *   The coordinator should log these errors (you don't need to implement logging infrastructure, just print to standard output).
    *   If a service fails to `Commit` after successfully preparing, the coordinator should retry the `Commit` operation a configurable number of times with exponential backoff before proceeding to `Rollback`.
    *   If a service fails to `Rollback`, the coordinator should log the error and continue attempting to rollback other services.  After attempting to rollback all services, the coordinator should return an error indicating that the rollback was not fully successful.  This is a "Heuristic Abort" scenario that requires manual intervention in a real system.

5.  **Concurrency:** The coordinator must handle concurrent transactions safely using appropriate synchronization mechanisms (e.g., mutexes, channels).

6.  **Timeouts:** The coordinator must support configurable timeouts for `Prepare`, `Commit`, and `Rollback` operations. If a service does not respond within the timeout, the coordinator should treat it as a failure and proceed accordingly.

7.  **API:** Provide a clear and concise API for beginning and ending transactions:

    ```go
    type TransactionCoordinator struct {
        // ... implementation details ...
    }

    func NewTransactionCoordinator(prepareTimeout time.Duration, commitTimeout time.Duration, rollbackTimeout time.Duration, commitRetries int) *TransactionCoordinator {
        // ...
    }

    func (tc *TransactionCoordinator) BeginTransaction(services []Service) (string, error) {
        // Begins a new transaction, returns transaction ID and error if any.
    }

    func (tc *TransactionCoordinator) EndTransaction(transactionID string) error {
        // Ends the transaction. Commits if all prepared, rolls back otherwise. Returns error if commit/rollback failed.
    }
    ```

**Constraints:**

*   The number of participating services in a transaction can vary.
*   Services may be unreliable and prone to temporary failures.
*   The coordinator should be robust and resilient to failures.
*   Optimize for minimal latency while ensuring data consistency.
*   Assume service's `Prepare`, `Commit`, and `Rollback` are idempotent.

**Judging Criteria:**

*   Correctness: Does the implementation correctly implement the 2PC protocol and ensure atomicity?
*   Error Handling: Does the implementation handle failures gracefully and ensure that the system remains in a consistent state?
*   Concurrency: Is the implementation thread-safe and able to handle concurrent transactions correctly?
*   Performance: Is the implementation efficient and does it minimize latency?
*   Code Quality: Is the code well-structured, readable, and maintainable?
*   Adherence to the API specifications.

This problem requires a solid understanding of distributed systems concepts, concurrency, error handling, and the 2PC protocol.  It's designed to be challenging and to differentiate between good and excellent solutions. Good luck!
