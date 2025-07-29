Okay, here's a challenging C++ problem designed to test a wide range of skills.

## Problem: Distributed Transaction Coordinator

**Problem Description:**

You are tasked with implementing a simplified distributed transaction coordinator.  Imagine a system where multiple independent services (nodes) need to participate in a single, atomic transaction.  To ensure data consistency across these services, a two-phase commit (2PC) protocol is used, coordinated by your transaction coordinator.

Your coordinator will manage multiple transactions concurrently.  Each transaction involves a set of participant nodes.  The coordinator must orchestrate the 2PC protocol to either commit or rollback the changes made by all participants in a transaction.

**Input:**

The coordinator receives a stream of messages through a `message_queue` (you can assume a thread-safe queue is provided, along with message type definitions).  These messages can be of the following types:

1.  **`BeginTransaction(transaction_id, set<node_id>)`**: Starts a new transaction with the given `transaction_id` and a set of `node_id`s representing the participants.  `transaction_id` and `node_id` are unique integer identifiers.
2.  **`VoteRequest(transaction_id, node_id)`**:  Simulates a participant node sending a vote (either `COMMIT` or `ABORT`) to the coordinator for the given transaction.
3.  **`CoordinatorTimeout(transaction_id)`**: Simulates a timeout event occurring at the coordinator for the given transaction.

**Output:**

Your coordinator should produce the following output (printed to `std::cout`) in response to the messages:

1.  **`"Transaction <transaction_id> prepared to commit (all nodes voted COMMIT)."`**: Printed when all participant nodes in a transaction have voted `COMMIT`.
2.  **`"Transaction <transaction_id> committed."`**:  Printed when the coordinator has successfully committed the transaction (after receiving all COMMIT votes).
3.  **`"Transaction <transaction_id> aborted."`**: Printed when the coordinator has decided to abort the transaction (either due to an ABORT vote from a participant, or a timeout).
4.  **`"Transaction <transaction_id> rolled back."`**:  Printed when the coordinator has successfully rolled back the transaction at all participants.
5.  **`"Node <node_id> COMMIT vote received for transaction <transaction_id>."`**: Printed when a COMMIT vote is received from a node.
6.  **`"Node <node_id> ABORT vote received for transaction <transaction_id>."`**: Printed when an ABORT vote is received from a node.
7.  **`"Coordinator timed out waiting for votes for transaction <transaction_id>."`**: Printed when the CoordinatorTimeout message is received.
8.  **`"Node <node_id> instructed to COMMIT for transaction <transaction_id>."`**: Printed when a node is instructed to commit.
9.  **`"Node <node_id> instructed to ROLLBACK for transaction <transaction_id>."`**: Printed when a node is instructed to rollback.
10. **`"Invalid transaction ID <transaction_id>"`**: Printed if `VoteRequest` or `CoordinatorTimeout` messages are received before a `BeginTransaction` message with the given `transaction_id`.

**Constraints and Requirements:**

*   **Concurrency:** The coordinator must handle multiple transactions concurrently.  Use appropriate synchronization mechanisms (e.g., mutexes, locks) to ensure thread safety.
*   **Atomicity:**  The coordinator must ensure that all participants either commit or rollback a transaction.
*   **Durability (Implied):** While you don't need to implement actual disk persistence, the coordinator's state must be consistent even in the face of simulated crashes (e.g., if the program is terminated abruptly).  This means proper handling of in-memory data structures is crucial.
*   **Message Handling:** The coordinator must process messages from the `message_queue` in a timely manner.  Consider using a separate thread to handle message processing.
*   **Timeout Handling:** If the coordinator doesn't receive votes from all participants within a timeout period (simulated by the `CoordinatorTimeout` message), it must abort the transaction.
*   **Error Handling:** The coordinator must handle invalid transaction IDs gracefully.
*   **Optimization:** Aim for efficient memory usage and minimal lock contention.  Consider using lock-free data structures or other optimization techniques if appropriate.
*   **Scalability:** While not strictly required for this problem, think about how your design could scale to handle a large number of concurrent transactions and participants.
*   **Node Simulation:** You do **not** need to actually implement the participant nodes themselves. The `VoteRequest` message simulates their behavior. Similarly, there is no need to implement communication between the Coordinator and the nodes.

**Example Message Sequence (Illustrative):**

1.  `BeginTransaction(1, {101, 102})`
2.  `VoteRequest(1, 101) // Node 101 votes COMMIT`
3.  `VoteRequest(1, 102) // Node 102 votes COMMIT`

**Expected Output:**

```
Node 101 COMMIT vote received for transaction 1.
Node 102 COMMIT vote received for transaction 1.
Transaction 1 prepared to commit (all nodes voted COMMIT).
Transaction 1 committed.
Node 101 instructed to COMMIT for transaction 1.
Node 102 instructed to COMMIT for transaction 1.
```

**Another Example Message Sequence (Illustrative):**

1. `BeginTransaction(2, {201, 202})`
2. `VoteRequest(2, 201) // Node 201 votes COMMIT`
3. `VoteRequest(2, 202) // Node 202 votes ABORT`

**Expected Output:**

```
Node 201 COMMIT vote received for transaction 2.
Node 202 ABORT vote received for transaction 2.
Transaction 2 aborted.
Node 201 instructed to ROLLBACK for transaction 2.
Node 202 instructed to ROLLBACK for transaction 2.
Transaction 2 rolled back.
```

**Another Example Message Sequence (Illustrative):**

1. `BeginTransaction(3, {301, 302})`
2. `VoteRequest(3, 301) // Node 301 votes COMMIT`
3. `CoordinatorTimeout(3)`

**Expected Output:**

```
Node 301 COMMIT vote received for transaction 3.
Coordinator timed out waiting for votes for transaction 3.
Transaction 3 aborted.
Node 301 instructed to ROLLBACK for transaction 3.
Node 302 instructed to ROLLBACK for transaction 3.
Transaction 3 rolled back.
```

**Yet Another Example Message Sequence (Illustrative):**

1. `VoteRequest(4, 401) // Node 401 votes COMMIT`
2. `BeginTransaction(4, {401, 402})`

**Expected Output:**

```
Invalid transaction ID 4
Node 401 COMMIT vote received for transaction 4.
```

**Tips for Solving:**

*   **Design Data Structures Carefully:** Choose appropriate data structures to store transaction information, participant votes, and transaction status.  Consider using `std::map`, `std::unordered_map`, `std::set`, or custom structures.
*   **Use a State Machine:**  Model the transaction lifecycle as a state machine (e.g., `INIT`, `VOTING`, `PREPARED`, `COMMITTED`, `ABORTED`, `ROLLING_BACK`).
*   **Implement Logging (Optional, but Recommended):**  A simple logging mechanism can help with debugging and understanding the coordinator's behavior.

This problem requires a solid understanding of concurrency, distributed systems concepts, and C++ programming. Good luck!
