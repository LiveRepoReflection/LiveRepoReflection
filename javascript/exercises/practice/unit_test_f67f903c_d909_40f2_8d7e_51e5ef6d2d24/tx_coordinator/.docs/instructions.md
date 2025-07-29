## Problem: Distributed Transaction Coordinator

### Question Description

You are tasked with implementing a simplified, in-memory distributed transaction coordinator. This coordinator is responsible for ensuring atomicity and consistency across multiple independent service calls. In a real-world scenario, these services might be databases, message queues, or other distributed systems. For simplicity, we will simulate these services with JavaScript functions.

Your coordinator must support the following functionalities:

1.  **Register Transaction:**  The coordinator must be able to register a new transaction, assigning it a unique transaction ID (UUID).

2.  **Add Participants:**  For each transaction, participants need to be registered. A participant is defined by two functions: a `commit` function and a `rollback` function.
    *   The `commit` function represents the action to be performed if the transaction succeeds.
    *   The `rollback` function represents the compensating action to undo the changes made by the `commit` function if the transaction fails.
    *   Each function must return a `Promise` that resolves when complete or rejects with an error.
    *   The commit and rollback function are only allowed to throw synchronously if they violate preconditions, such as the provided arguments being in the wrong format, they should never throw asynchronously.

3.  **Commit Transaction:**  When a transaction is ready to be committed, the coordinator must execute all registered `commit` functions in an **asynchronous, non-blocking** manner. The coordinator must wait for all `commit` functions to complete successfully or reject. If all `commit` functions succeed, the transaction is considered committed.

4.  **Rollback Transaction:**  If any `commit` function fails (rejects), the coordinator must execute all registered `rollback` functions in an **asynchronous, non-blocking** manner.  The `rollback` functions should be executed **regardless** of whether other `rollback` functions succeed or fail. The coordinator must wait for all `rollback` functions to complete (either resolve or reject).  The coordinator will then throw an error.

5.  **Idempotency:**  The `commit` and `rollback` methods should only execute once.

6. **Asynchronous execution**:
    * The execution of the commit and rollback functions must be asynchronous.
    * If there are multiple commit or rollback functions, the execution of these functions must be non-blocking with respect to each other.

### Constraints and Requirements:

*   **Error Handling:**  Your coordinator must handle errors gracefully. If any `commit` function fails, the coordinator must trigger the rollback mechanism. If any `rollback` function fails, the coordinator must log the error but continue to execute other `rollback` functions. The coordinator should throw an aggregate error containing all commit and/or rollback errors.
*   **Concurrency:**  The coordinator should handle concurrent transaction requests efficiently.  You can assume a multi-threaded environment.
*   **Atomicity:**  The entire transaction must either succeed completely (all `commit` functions succeed) or fail completely (all committed changes are rolled back).
*   **Durability:** While this is an in-memory coordinator, ensure that once a transaction is committed (all `commit` functions succeed), that information is persisted in memory and a subsequent system failure will not cause the transaction to be re-attempted.  Similarly, once a transaction has started rollback, that information should be persisted.
*   **Isolation:**  Concurrent transactions should not interfere with each other.
*   **Optimization:**  The coordinator should be designed for performance.  Consider the impact of data structures and algorithms on the overall performance.
*   **Scalability:**  Consider how the coordinator could be scaled to handle a large number of concurrent transactions and participants. (While a full implementation of scalability is not required, your design should consider the implications.)
*   **Memory Management:**  Avoid memory leaks and ensure efficient memory usage, especially with a large number of transactions.
*   **UUID Generation:** Use a proper UUID library for generating unique transaction IDs.
*   **Input Validation**: Every function needs to validate the input and throw a relevant error if the input is wrong.

### Input:

*   `commit` and `rollback` functions are provided as arguments to the `addParticipant` method. These functions can be asynchronous (return Promises).
*   Transaction data is in-memory.

### Output:

*   The `commitTransaction` function should resolve (return a Promise that resolves) if the transaction is committed successfully.
*   The `commitTransaction` function should reject (return a Promise that rejects) with an appropriate error if the transaction fails to commit, even after rolling back. The error must contain information about each commit and rollback failure.

### Example Scenario:

Imagine you are building an e-commerce platform. A transaction might involve:

1.  Reserving inventory in the inventory service.
2.  Charging the customer's credit card in the payment service.
3.  Creating an order in the order service.

If any of these steps fail, you need to rollback the changes made by the previous steps to maintain consistency.

### Bonus Challenges:

*   Implement a timeout mechanism for `commit` and `rollback` functions. If a function takes too long to execute, consider it a failure.
*   Implement a retry mechanism for failed `commit` and `rollback` functions.
*   Add support for distributed tracing to track transactions across multiple services.

This problem requires a deep understanding of asynchronous programming, error handling, and distributed systems concepts. Good luck!
