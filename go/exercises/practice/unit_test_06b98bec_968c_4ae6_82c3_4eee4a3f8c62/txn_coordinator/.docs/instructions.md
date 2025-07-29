## Question: Distributed Transaction Coordinator

### Question Description

You are tasked with building a simplified distributed transaction coordinator. This coordinator is responsible for ensuring atomicity and consistency across multiple independent services involved in a single logical transaction.

**System Overview:**

Imagine you have a system with multiple microservices. A single user action might require modifications to data across several of these services. To ensure data integrity, these modifications must be treated as a single, atomic transaction: either all changes succeed, or none do.

**Your Task:**

Implement a transaction coordinator that manages the two-phase commit (2PC) protocol for a set of participating services.

**Participants (Services):**

Each service can participate in a transaction by implementing a simple interface:

```go
type Participant interface {
	Prepare(transactionID string, data map[string]interface{}) error // Asks the participant if it's ready to commit the transaction.
	Commit(transactionID string) error   // Instructs the participant to commit the transaction.
	Rollback(transactionID string) error // Instructs the participant to rollback the transaction.
}
```

**Transaction Coordinator:**

Your coordinator must provide the following functionality:

1.  **`BeginTransaction() string`**: Starts a new transaction and returns a unique transaction ID.
2.  **`EnlistParticipant(transactionID string, participant Participant)`**: Adds a service (Participant) to an existing transaction.
3.  **`CommitTransaction(transactionID string, data map[string]interface{}) error`**: Attempts to commit the transaction. This involves:
    *   Sending a `Prepare` message to all enlisted participants with `transactionID` and `data`.
    *   If *all* participants successfully prepare, send a `Commit` message to all participants.
    *   If *any* participant fails to prepare, send a `Rollback` message to all participants.
4.  **`RollbackTransaction(transactionID string) error`**: Rolls back the transaction. This involves sending a `Rollback` message to all enlisted participants.

**Constraints and Requirements:**

*   **Concurrency:** The coordinator must be able to handle multiple concurrent transactions.
*   **Error Handling:**  The coordinator must gracefully handle errors from participants (e.g., network failures, participant crashes).  Implement appropriate retry mechanisms with exponential backoff for failed `Prepare`, `Commit`, and `Rollback` calls. Limit retries to a configurable maximum (e.g., 3 retries).  After all retries are exhausted, log the error and continue with the rest of the participants.
*   **Idempotency:**  The `Commit` and `Rollback` operations on participants must be idempotent. This means that if a participant receives the same `Commit` or `Rollback` message multiple times, it should only execute the action once. Your coordinator should be designed to handle potential message duplication.
*   **Timeout:** Implement a timeout mechanism for `Prepare` calls. If a participant doesn't respond within a configurable timeout (e.g., 5 seconds), consider the `Prepare` call failed and initiate a rollback.
*   **Logging:** Implement basic logging to record transaction events (start, enlist, prepare, commit, rollback, errors).
*   **Deadlock Prevention:** Participants should be prepared to handle concurrent transactions and avoid deadlocks. While you don't need to implement explicit deadlock detection within the coordinator, consider how your design might influence the likelihood of deadlocks at the participant level.
*   **Optimistic Concurrency Control:** Assume participants implement optimistic concurrency control (e.g., using version numbers or timestamps) to prevent data corruption. The coordinator doesn't need to manage concurrency control directly, but the `data` parameter passed to the `Prepare` call may contain version information that participants use for concurrency checks.
*   **Data Consistency:** Guarantee that if the `CommitTransaction` function returns without an error, all enlisted participants have successfully committed the transaction.  If the function returns an error, all enlisted participants have been rolled back (or the coordinator has made a best-effort attempt to roll back).

**Optimizations to Consider (Not Required for Base Solution, but Highly Encouraged):**

*   **Asynchronous Operations:**  Offload `Commit` and `Rollback` operations to background goroutines to improve the responsiveness of the `CommitTransaction` and `RollbackTransaction` functions. However, the `CommitTransaction` function *must* still guarantee that all operations either succeed or are attempted to be rolled back.
*   **Batching:**  If possible, batch `Commit` and `Rollback` operations to reduce the number of network calls to participants.  This might involve grouping multiple participants into a single request. (Requires modifications to the `Participant` interface)
*   **Parallel Prepare Phase:** Initiate `Prepare` calls to all participants in parallel to reduce the overall transaction commit time.

This problem tests your understanding of distributed systems concepts, concurrency, error handling, and optimization techniques in Go. Good luck!
