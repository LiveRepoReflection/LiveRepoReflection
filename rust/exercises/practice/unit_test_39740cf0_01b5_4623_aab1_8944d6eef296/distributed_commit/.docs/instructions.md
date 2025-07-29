Okay, here's a challenging Rust programming competition problem designed to test a competitor's knowledge of advanced data structures, algorithms, and optimization.

## Problem: Distributed Transaction Commit Protocol

**Description:**

You are designing a distributed database system.  A critical component is the transaction commit protocol, ensuring atomicity across multiple nodes. Your task is to implement a simplified version of the Two-Phase Commit (2PC) protocol coordinator in Rust.

**Scenario:**

You have a cluster of `N` nodes (represented by unique integer IDs from 1 to `N`).  A transaction involves updating data on a subset of these nodes. The coordinator is responsible for orchestrating the commit or abort of a transaction across all participating nodes.

**Data Structures:**

*   `NodeId`: A `usize` representing the unique ID of a node (from 1 to `N`).
*   `TransactionId`: A `usize` representing the unique ID of a transaction.
*   `Vote`: An enum with two possible values: `Commit` and `Abort`.
*   `TransactionState`: An enum representing the current state of a transaction: `Pending`, `Prepared`, `Committed`, `Aborted`.
*   `Coordinator`: Your struct that manages the transaction commit process.

**Requirements:**

1.  **Initialization:** The `Coordinator` should be initialized with the total number of nodes `N`.

2.  **Transaction Initiation:**  Implement a function `start_transaction(transaction_id: TransactionId, participating_nodes: Vec<NodeId>) -> Result<(), String>`. This function should:

    *   Record the participating nodes for the given `transaction_id`.
    *   Ensure that a transaction with the same `transaction_id` does not already exist.
    *   Return `Ok(())` if the transaction is successfully started, or `Err("Reason")` with a descriptive error message if not.

3.  **Vote Collection:** Implement a function `receive_vote(transaction_id: TransactionId, node_id: NodeId, vote: Vote) -> Result<(), String>`. This function should:

    *   Record the vote from the given `node_id` for the specified `transaction_id`.
    *   Ensure that the `node_id` is a participating node for the transaction.
    *   Ensure that the `transaction_id` exists and is in the `Pending` state.
    *   Return `Ok(())` if the vote is successfully recorded, or `Err("Reason")` with a descriptive error message if not.

4.  **Global Decision:** Implement a function `make_decision(transaction_id: TransactionId) -> Result<TransactionState, String>`. This function should:

    *   Determine the global decision (Commit or Abort) based on the votes received.
    *   If *all* participating nodes voted `Commit`, the global decision is `Commit`.
    *   If *any* participating node voted `Abort`, the global decision is `Abort`.
    *   If not all votes have been received, the function should return `Err("Not all votes received")`.
    *   Update the `TransactionState` of the transaction to either `Committed` or `Aborted` based on the decision.
    *   Ensure that the `transaction_id` exists and is in the `Pending` state.
    *   Return the final `TransactionState` or `Err("Reason")` with a descriptive error message if not.

5.  **Transaction Completion/Cleanup:** Implement a function `get_transaction_state(transaction_id: TransactionId) -> Result<TransactionState, String>`. This function should:
    * Return the current state of the transaction. If the transaction does not exist return `Err("Transaction not found")`.

6.  **Concurrency:** The `Coordinator` must be thread-safe. Multiple threads might concurrently call `start_transaction`, `receive_vote`, `make_decision`, and `get_transaction_state`. Use appropriate synchronization primitives (e.g., `Mutex`, `RwLock`) to prevent race conditions.

7.  **Optimization:**
    *   The `receive_vote` function should have minimal lock contention.
    *   The `make_decision` function should efficiently determine the global decision without iterating through all votes multiple times.

**Constraints:**

*   `1 <= N <= 1000` (Number of nodes)
*   `1 <= number of transactions <= 1000`
*   The number of participating nodes in a transaction can vary.
*   The program must be robust and handle edge cases gracefully.
*   Ensure no deadlocks occur.
*   Optimize for read-heavy workload (frequent calls to `get_transaction_state`).

**Error Handling:**

All functions must return a `Result<(), String>` or `Result<TransactionState, String>` and provide informative error messages.

**Evaluation:**

The solution will be evaluated based on:

*   **Correctness:** Does the implementation correctly implement the 2PC protocol?
*   **Concurrency Safety:** Does the implementation prevent race conditions?
*   **Performance:** Is the implementation efficient in terms of lock contention and algorithm complexity?
*   **Code Quality:** Is the code well-structured, readable, and maintainable?
*   **Error Handling:** Does the implementation handle errors gracefully?

This problem requires a solid understanding of concurrency, data structures, and algorithms, making it a challenging and sophisticated programming task. Good luck!
