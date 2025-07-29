Okay, here's a challenging Go coding problem description designed to be at a LeetCode Hard level.

**Problem Title: Distributed Transaction Manager**

**Problem Description:**

You are tasked with building a simplified, in-memory distributed transaction manager. This system manages transactions across multiple independent service nodes (represented as integers). Each service node can perform operations that need to be ACID (Atomicity, Consistency, Isolation, Durability) compliant.  Since we focus on the algorithm challenge, we omit the durability requirement and persist data in memory.

Your transaction manager should support the following operations:

1.  **Begin(transactionID int):** Starts a new transaction with the given unique transaction ID.

2.  **Participate(transactionID int, serviceNode int):**  Registers a service node as a participant in the specified transaction. A service node can only participate in one transaction at a time.

3.  **Prepare(transactionID int):**  Initiates the prepare phase of the 2-Phase Commit (2PC) protocol for the specified transaction.  Each participating service node must 'vote' to either commit or abort. The service nodes vote 'commit' if they are ready to commit their local changes, otherwise they vote 'abort'. Assume each service node has a local function `PrepareVote(transactionID int) bool` that returns `true` if the service node votes to commit and `false` otherwise.  The transaction manager simulates calling this function on each participating service node.

4.  **Commit(transactionID int):**  Initiates the commit phase of the 2PC protocol. This can only be called if all participating service nodes voted to commit in the Prepare phase.  If any service node voted to abort, calling this method should return an error.

5.  **Abort(transactionID int):**  Initiates the abort phase of the 2PC protocol. This forces all participating service nodes to rollback any local changes.

6.  **GetTransactionState(transactionID int) string:** Returns the current state of the transaction. Possible states are: "ACTIVE", "PREPARED", "COMMITTED", "ABORTED".

**Constraints and Requirements:**

*   **Atomicity:**  A transaction must either be fully committed across all participating service nodes, or fully aborted.
*   **Isolation:** Transactions must not interfere with each other.  A service node can only participate in one transaction at a time.
*   **Concurrency:**  The transaction manager must be thread-safe. Multiple Begin, Participate, Prepare, Commit, and Abort calls can happen concurrently from different goroutines.
*   **Error Handling:**  Appropriate errors should be returned for invalid operations, such as attempting to commit a transaction that hasn't been prepared, or attempting to participate a service node in multiple transactions concurrently.
*   **Performance:**  The transaction manager should be designed to handle a large number of concurrent transactions and service nodes efficiently.  Consider potential bottlenecks and optimize for minimal contention. The number of service nodes can be on the order of 1000s.
*   **Service Node Failure:** If a service node fails (e.g., always returns false from `PrepareVote`) the system must correctly abort.
*   **Idempotency:** The `Commit` and `Abort` operations should be idempotent if possible. Meaning calling `Commit` multiple times in `COMMITTED` state should not throw an error. Likewise, `Abort` can be called multiple times in `ABORTED` state.

**Input/Output:**

The operations are methods on a `TransactionManager` struct. You need to design the struct and implement the methods. The methods should return appropriate error values when operations fail. For `GetTransactionState`, return a string representing the state.

**Example Usage:**

```go
tm := NewTransactionManager()

err := tm.Begin(123)
if err != nil {
  // Handle error
}

err = tm.Participate(123, 1)
if err != nil {
  // Handle error
}

err = tm.Participate(123, 2)
if err != nil {
  // Handle error
}

// Simulate the PrepareVote function for service nodes 1 and 2 (example)
// Assume serviceNodeVotes is a map[int]bool
serviceNodeVotes := map[int]bool{
	1: true,
	2: true,
}
tm.PrepareVoteFunc = func(transactionID, serviceNode int) bool {
  return serviceNodeVotes[serviceNode]
}

err = tm.Prepare(123)
if err != nil {
  // Handle error
}

err = tm.Commit(123)
if err != nil {
  // Handle error
}

state := tm.GetTransactionState(123)
// state should be "COMMITTED"

```

**Note:**

*   You'll need to design your own data structures to track transactions, participating service nodes, and transaction states.
*   Focus on correctness, concurrency safety, and performance.
*   Consider edge cases and potential race conditions.
*   Implement the 2PC protocol correctly, handling both commit and abort scenarios.
*   This problem tests your understanding of distributed systems concepts, concurrency, and error handling in Go.
