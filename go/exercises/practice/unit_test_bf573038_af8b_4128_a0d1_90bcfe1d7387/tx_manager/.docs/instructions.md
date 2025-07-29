Okay, here's a challenging Go coding problem designed to be akin to LeetCode's "Hard" difficulty.

## Problem Title: Distributed Transaction Manager

### Question Description

You are tasked with implementing a simplified distributed transaction manager in Go. This system will be responsible for coordinating transactions across multiple independent services.

Imagine a scenario where you have several microservices (databases, payment processors, inventory systems). To ensure data consistency, operations across these services must be atomic; either all operations succeed, or none do.

**Core Requirements:**

1.  **Transaction Coordination:** Implement a `TransactionManager` that can initiate, commit, and rollback transactions involving multiple services.
2.  **Two-Phase Commit (2PC) Protocol:** Use the 2PC protocol to guarantee atomicity.  The `TransactionManager` acts as the coordinator.
3.  **Service Abstraction:** Define an interface `Service` with methods for `Prepare`, `Commit`, and `Rollback`. Each microservice will implement this interface.
4.  **Concurrency:** Design the `TransactionManager` to handle concurrent transactions efficiently.  Avoid race conditions and ensure proper synchronization.
5.  **Timeout Handling:** Implement timeouts for both the `Prepare` and `Commit/Rollback` phases. If a service doesn't respond within a specified timeout, the transaction should be rolled back.
6.  **Idempotency:**  Services must handle `Commit` and `Rollback` requests idempotently. The `TransactionManager` may retry these operations if the initial attempt fails.
7.  **Logging:** Maintain a log of all transactions, including their status (prepared, committed, rolled back), involved services, and timestamps.  This log should be persistent (e.g., written to a file).
8.  **Crash Recovery:**  The `TransactionManager` should be able to recover its state from the log upon restart.  It should determine the outcome of any in-flight transactions at the time of the crash and complete them (commit or rollback).

**Interface Definition:**

```go
type TransactionID string // Unique identifier for a transaction

type Service interface {
	Prepare(txID TransactionID) error // Prepare the service for commit; return nil on success, error on failure
	Commit(txID TransactionID) error  // Commit the transaction; return nil on success, error on failure
	Rollback(txID TransactionID) error // Rollback the transaction; return nil on success, error on failure
}

type TransactionManager interface {
	BeginTransaction() TransactionID        // Starts a new transaction, returns a unique transaction ID.
	EnlistService(txID TransactionID, service Service) error // Adds a service to the transaction.
	CommitTransaction(txID TransactionID) error       // Commits the transaction.
	RollbackTransaction(txID TransactionID) error     // Rolls back the transaction.
	Recover() error // Recover the transaction manager state from persistent log.
}
```

**Constraints:**

*   **Error Handling:** Robust error handling is crucial.  The system should gracefully handle service failures, network issues, and other potential problems.
*   **Scalability:** Consider how your design could be scaled to handle a large number of transactions and services.  While you don't need to implement full-blown distributed consensus, think about potential bottlenecks.
*   **Performance:** Minimize latency and maximize throughput.  Efficient concurrency and data structures are essential.
*   **Durability:** The transaction log must be durable to ensure reliable recovery.

**Input:**

The primary input is the configuration of services to be managed and the requests to begin, commit, and rollback transactions.  The service configuration should be adaptable (e.g., read from a configuration file).

**Output:**

The primary outputs are the success or failure of transaction commits and rollbacks, and the persistent transaction log. The program doesn't need to provide a user interface. Successful/failed transaction status should be logged in a human-readable format.

**Example Scenario:**

1.  The `TransactionManager` starts.
2.  It recovers its state from the log (if any).
3.  A new transaction is started (txID = "TX1").
4.  Service A and Service B are enlisted in transaction "TX1".
5.  `CommitTransaction("TX1")` is called.
6.  The `TransactionManager` sends `Prepare("TX1")` to Service A and Service B.
7.  If both services respond successfully, the `TransactionManager` sends `Commit("TX1")` to both services.
8.  If either service fails during the prepare phase or a timeout occurs, the `TransactionManager` sends `Rollback("TX1")` to all involved services.
9.  All actions are logged to the persistent log.

This problem requires a solid understanding of concurrency, distributed systems principles (especially 2PC), error handling, and persistence. Good luck!
