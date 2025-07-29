## Problem: Distributed Transaction Coordinator

**Difficulty:** Hard

**Description:**

You are tasked with building a simplified, in-memory distributed transaction coordinator.  This coordinator will manage transactions across multiple independent services (simulated as structs in Go).  The goal is to ensure ACID properties (Atomicity, Consistency, Isolation, Durability) for operations spanning these services.

**Scenario:**

Imagine an e-commerce system with multiple services: `UserService`, `InventoryService`, and `PaymentService`.  A single order might require operations on all three services:

1.  Create a user account (UserService).
2.  Reserve items in the inventory (InventoryService).
3.  Process the payment (PaymentService).

If any of these steps fail, the entire transaction must be rolled back to maintain data consistency.

**Requirements:**

1.  **Transaction Management:** Implement a `Coordinator` struct with methods to begin, commit, and rollback transactions.
2.  **Two-Phase Commit (2PC):** Use the 2PC protocol to ensure atomicity. This involves a "prepare" phase where all participating services are asked if they can commit, and a "commit" phase where the coordinator instructs all services to commit or rollback based on the prepare phase results.
3.  **Concurrency:** The coordinator must handle multiple concurrent transactions safely. Use appropriate synchronization primitives (e.g., mutexes, channels) to prevent race conditions and data corruption.
4.  **Idempotency:**  Services can receive the same "prepare," "commit," or "rollback" command multiple times. Ensure that these operations are idempotent.
5.  **Timeout:** Implement a timeout mechanism. If a service doesn't respond within a specified time during the prepare phase, the coordinator should automatically initiate a rollback.
6.  **Crash Recovery (Simulated):** While a full disk-based recovery isn't required, simulate a coordinator crash.  If the coordinator crashes during the prepare phase, on restart, the services should automatically rollback the prepared transaction. If the crash occurred after all services successfully prepared but before all commits completed, on restart, the services should complete the commit phase.
7.  **Isolation:** Implement a basic form of isolation. During a transaction, the services should prevent other conflicting transactions from modifying the same resources.  A simple locking mechanism (e.g., using mutexes within each service) is sufficient.
8.  **Error Handling:** Robustly handle errors.  Return meaningful errors to the caller when transactions fail. Log errors appropriately.

**Data Structures and Interfaces (Example):**

```go
type TransactionID int

type Service interface {
	Prepare(txID TransactionID) error
	Commit(txID TransactionID) error
	Rollback(txID TransactionID) error
	GetState(txID TransactionID) string // Returns "prepared", "committed", "rolledback", or ""
}

type Coordinator struct {
	// ... your implementation details here ...
}

func NewCoordinator(services []Service, timeout time.Duration) *Coordinator {
	// ... your implementation here ...
}

func (c *Coordinator) BeginTransaction() TransactionID {
	// ... your implementation here ...
}

func (c *Coordinator) CommitTransaction(txID TransactionID) error {
	// ... your implementation here ...
}

func (c *Coordinator) RollbackTransaction(txID TransactionID) error {
	// ... your implementation here ...
}

// (Optional) Simulate Coordinator Restart
func (c *Coordinator) Recover() error {
	// ... your implementation here ...
}
```

**Constraints:**

*   The number of services involved in a transaction can vary.
*   Service implementations can be assumed to be unreliable (may return errors or time out).
*   The timeout duration for service responses should be configurable.
*   The solution should be efficient in terms of resource usage (memory, CPU).  Avoid unnecessary allocations and locking contention.

**Scoring:**

Solutions will be evaluated based on:

1.  **Correctness:** Does the solution correctly implement the 2PC protocol and ensure ACID properties?
2.  **Concurrency:** Does the solution handle concurrent transactions safely and efficiently?
3.  **Error Handling:** Does the solution handle errors gracefully and provide meaningful error messages?
4.  **Performance:** Is the solution efficient in terms of resource usage?
5.  **Code Quality:** Is the code well-structured, readable, and maintainable?

This problem requires a solid understanding of distributed systems concepts, concurrency, and error handling in Go. It challenges the solver to design and implement a robust and efficient transaction coordinator that can handle the complexities of a distributed environment. Good luck!
