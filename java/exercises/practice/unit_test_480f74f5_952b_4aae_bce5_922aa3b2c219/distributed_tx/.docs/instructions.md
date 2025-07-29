## Problem: Distributed Transaction Manager

**Description:**

You are tasked with designing and implementing a simplified distributed transaction manager for a microservices architecture. Imagine a scenario where multiple independent services need to perform operations that must either all succeed or all fail together. This is a classic distributed transaction problem.

**System Architecture:**

*   You have `N` microservices (numbered 1 to N). Each microservice manages its own local data store (e.g., a database).
*   The Transaction Manager (TM) is responsible for coordinating transactions across these microservices.
*   The TM communicates with each microservice using a simplified RPC mechanism (assume a `Microservice` interface with `prepare`, `commit`, and `rollback` methods, described below).

**Transaction Protocol:**

Implement a two-phase commit (2PC) protocol. The TM acts as the coordinator, and the microservices are the participants.

1.  **Prepare Phase:**
    *   The TM sends a `prepare(transactionId, operations)` message to all involved microservices. The `operations` represent the actions that the microservice needs to perform as part of the transaction.
    *   Each microservice attempts to execute the `operations` tentatively. If it succeeds, it logs its intention to either commit or rollback (this log needs to be durable, although you can simulate durability in memory for simplicity). It then responds with a "prepared" message to the TM. If it fails (e.g., due to data validation errors, resource constraints), it responds with a "abort" message.
2.  **Commit/Rollback Phase:**
    *   If the TM receives "prepared" messages from *all* involved microservices, it sends a `commit(transactionId)` message to all of them.
    *   If the TM receives at least one "abort" message, or if it doesn't receive a response from a microservice within a timeout period, it sends a `rollback(transactionId)` message to all involved microservices.
    *   Upon receiving a `commit` message, a microservice permanently applies the changes it tentatively executed in the prepare phase.
    *   Upon receiving a `rollback` message, a microservice undoes any changes it tentatively executed in the prepare phase.
    *   Each microservice must acknowledge the `commit` or `rollback` message.

**Interface Definition:**

Define a `Microservice` interface with the following methods:

*   `String prepare(int transactionId, List<Operation> operations)`:  Takes a transaction ID and a list of operations to perform. Returns "prepared" if successful, "abort" if not.  Simulate durable logging within this method.
*   `String commit(int transactionId)`: Takes a transaction ID. Returns "ack" if successful.
*   `String rollback(int transactionId)`: Takes a transaction ID. Returns "ack" if successful.

Define a `TransactionManager` class with a method:

*   `boolean executeTransaction(List<Integer> involvedMicroservices, List<List<Operation>> operationsPerService)`: Takes a list of involved microservice IDs and a list of lists of operations.  The outer list corresponds to the microservices listed in `involvedMicroservices`, and the inner lists contain the operations for each microservice. Returns `true` if the transaction commits successfully, `false` if it aborts.

**Constraints and Requirements:**

*   **Concurrency:** Multiple transactions can be executed concurrently. Ensure thread safety in your implementation.  The transaction manager should handle concurrent `executeTransaction` calls correctly.
*   **Timeouts:** Implement a timeout mechanism. If a microservice doesn't respond to a `prepare` message within a specified timeout (e.g., 5 seconds), the TM should abort the transaction.
*   **Idempotency:**  The `commit` and `rollback` operations should be idempotent.  A microservice might receive the same `commit` or `rollback` message multiple times due to network issues.  It should only execute the operation once.
*   **Durability (Simulated):** The decision to commit or rollback in the `prepare` phase must be durable.  You can simulate this by storing the decision in an in-memory data structure that is properly synchronized.  Consider what happens if the TM crashes after sending the prepare and before sending the commit/rollback. How would you handle recovery? (This doesn't need to be fully implemented, but the code should show considerations for it)
*   **Scalability Considerations:** While you don't need to implement actual network communication, consider how your design would scale to a large number of microservices and concurrent transactions.  Discuss potential bottlenecks and optimizations in comments in your code.
*   **Operations:** Define a simple `Operation` class representing a single operation to be performed on a microservice (e.g., `UpdateAccountBalanceOperation(accountId, amount)`).  The `Operation` class should have a method to "execute" it.

**Example:**

Assume you have three microservices (1, 2, 3).  You want to execute a transaction involving microservices 1 and 2:

*   Microservice 1 needs to transfer \$100 from account A to account B.
*   Microservice 2 needs to update a user profile.

You would call `executeTransaction` with the following arguments:

*   `involvedMicroservices = [1, 2]`
*   `operationsPerService = [[new UpdateAccountBalanceOperation("A", -100), new UpdateAccountBalanceOperation("B", 100)], [new UpdateUserProfileOperation("user123", "new_address")]]`

**Judging Criteria:**

*   **Correctness:**  The implementation correctly implements the 2PC protocol and ensures atomicity (all or nothing).
*   **Concurrency:** The implementation is thread-safe and handles concurrent transactions correctly.
*   **Timeout Handling:** The timeout mechanism works as expected.
*   **Idempotency:** The `commit` and `rollback` operations are idempotent.
*   **Scalability Considerations:** The design takes into account scalability concerns.
*   **Code Quality:** The code is well-structured, readable, and maintainable.
*   **Error Handling:** The code handles potential errors gracefully.

This problem requires a strong understanding of distributed systems concepts, concurrency, and error handling. Good luck!
