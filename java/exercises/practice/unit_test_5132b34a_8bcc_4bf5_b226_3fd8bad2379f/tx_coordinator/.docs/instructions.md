## Problem: Distributed Transaction Coordinator

**Description:**

You are tasked with designing and implementing a simplified distributed transaction coordinator service. This service is responsible for ensuring atomicity and consistency across multiple independent services (participants) when they need to perform a series of operations that should be treated as a single, atomic transaction.

In this simplified model, you will implement a two-phase commit (2PC) protocol to manage transactions across a set of participant services. Your coordinator service will interact with these participants to either commit or rollback changes based on their individual success or failure.

Each participant service exposes two key operations:

*   `prepare(transactionId)`:  The participant attempts to prepare for the transaction. This involves tentatively executing the transaction's operations but without making the changes permanent. It returns `true` if preparation succeeds and `false` otherwise.  The participant must be able to rollback the prepared transaction until a commit or rollback decision is received from the coordinator.
*   `commit(transactionId)`: The participant permanently commits the prepared transaction.
*   `rollback(transactionId)`: The participant rolls back the prepared transaction, discarding any tentative changes.

Your task is to implement the `TransactionCoordinator` class with the following methods:

*   `beginTransaction()`: Starts a new transaction, generating a unique transaction ID. Returns the transaction ID.
*   `enroll(transactionId, participant)`:  Adds a participant (an object implementing the `Participant` interface) to the transaction.
*   `commitTransaction(transactionId)`: Attempts to commit the transaction.  This method performs the 2PC protocol. It first asks all enrolled participants to prepare. If all participants successfully prepare, it then instructs them to commit. If any participant fails to prepare, it instructs all participants to rollback. Returns `true` if the transaction commits successfully, `false` otherwise.
*   `rollbackTransaction(transactionId)`: Rolls back the transaction.  Instructs all enrolled participants to rollback. Returns `true` if the rollback succeeds (all participants successfully rollback), `false` otherwise. In a real system, rollback failures would need to be handled carefully (e.g. retries), but for this problem, return false if any rollback fails.

**Assumptions and Constraints:**

*   The `Participant` interface is pre-defined with `prepare`, `commit`, and `rollback` methods.
*   You can assume that the `transactionId` is a `String`.
*   The `Participant` objects represent external services, and their `prepare`, `commit`, and `rollback` methods may exhibit unpredictable behavior (e.g., throw exceptions, take a long time to respond, return false).
*   The number of participants in a transaction can vary.
*   Each participant should only be enrolled in a single transaction at a time. The coordinator should throw an exception if a participant is enrolled in multiple concurrent transactions.
*   The coordinator should handle concurrent transactions correctly.
*   Implement proper error handling and logging (simulated with print statements is acceptable).
*   The order in which participants are prepared, committed or rolled back does not matter.
*   The coordinator must be thread-safe.

**Optimization Requirements:**

*   The prepare phase should be executed in parallel to minimize the overall transaction time.  Use Java concurrency features (e.g., ExecutorService, Futures) to achieve this.

**Real-World Considerations:**

*   While simplified, this problem reflects core challenges in distributed systems: ensuring data consistency across multiple services.
*   Handling participant failures and timeouts is crucial in real-world scenarios.

**Example `Participant` Interface (for illustration - this will be pre-defined):**

```java
interface Participant {
    boolean prepare(String transactionId);
    void commit(String transactionId);
    void rollback(String transactionId);
}
```

**Expected Code Structure:**

You should provide the implementation of the `TransactionCoordinator` class with the methods described above. You are free to add any helper classes or interfaces as needed.
