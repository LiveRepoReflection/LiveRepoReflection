Okay, I'm ready. Here's a challenging Go coding problem:

### Project Name

`DistributedTransactionCoordinator`

### Question Description

You are tasked with building a distributed transaction coordinator (DTC) for a simplified banking system. This system involves multiple independent bank services (simulated as Go functions), each managing a subset of customer accounts. A transaction involves transferring funds between accounts potentially residing on *different* bank services.

The system has the following constraints:

1.  **Atomicity:** A transaction must either complete fully (all transfers succeed) or have no effect (all transfers are rolled back). Partial transactions are not allowed.
2.  **Consistency:** The banking system must remain in a consistent state. Transfers must maintain the total balance of all accounts within each service and across the entire system.
3.  **Isolation:** Concurrent transactions must not interfere with each other. The result of concurrent transactions should be the same as if they were executed serially.
4.  **Durability:** Once a transaction is committed, the changes must be permanent, even in the event of service failures (simulated by panics).

**Implement a DTC that can reliably execute distributed transactions involving these bank services.**

**Specifically, you need to implement the following:**

*   A `Transaction` struct that encapsulates the operations (fund transfers) to be performed. Each operation specifies the source account, the destination account, and the amount to transfer, as well as the bank service identifier.
*   A `Coordinator` struct that manages the transaction lifecycle: preparation, commit, and rollback.
*   A `Prepare` phase: The coordinator must first ensure that *all* participating bank services are willing to perform their part of the transaction. This involves sending a "prepare" request to each service and receiving an acknowledgment. The preparation phase must handle the case where an individual bank service can not perform the transaction (e.g., insufficient funds in the source account) and must return to initial state in this scenario.
*   A `Commit` phase: If all services successfully prepare, the coordinator instructs them to commit their changes.
*   A `Rollback` phase: If any service fails to prepare, or if the commit phase fails, the coordinator must instruct all services to roll back their changes to ensure atomicity.
*   Error Handling: The DTC must handle various error conditions gracefully, including network failures (simulated by timeouts), service unavailability (simulated by panics), and data validation errors (e.g., negative transfer amounts).
*   Concurrency: Your DTC must handle concurrent transactions correctly, ensuring isolation and preventing race conditions. Assume bank services do *not* handle any concurrency safety and rely on DTC to maintain the order.
*   Idempotency: The Prepare, Commit and Rollback operations on each bank service must be idempotent. I.e. repeating the request must have the same effect as performing it once. This is required as the DTC may retry operations after a network failure or service panic. You can assume that operations are uniquely identifiable.
*   Logging: Log all important events such as prepare, commit, rollback, service failures and retries. The logging must happen to the standard output.

**Constraints and Edge Cases:**

*   The number of bank services and the number of operations within a transaction can vary.
*   Bank services can fail (panic) at any point during the transaction lifecycle. Your DTC must be resilient to these failures.
*   Network communication between the DTC and bank services can be unreliable (simulated by timeouts).
*   The total number of accounts managed by the entire system can be very large.
*   The transfer amount is an integer value.
*   Account IDs are strings.
*   Bank service identifiers are strings.
*   The bank services are simulated using Go functions, so you'll need to manage concurrency using channels and goroutines.
*   Assume the bank services expose following interface:
    *   `Prepare(transactionID string, operations []Operation) error`
    *   `Commit(transactionID string) error`
    *   `Rollback(transactionID string) error`

**Optimization Requirements:**

*   The DTC should minimize the overall transaction latency. Consider using techniques like parallel execution where applicable, and minimizing the number of network round trips.

This problem requires a solid understanding of distributed systems concepts, concurrency in Go, error handling, and fault tolerance. Good luck!
