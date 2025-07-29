## Project Name

```
distributed-transaction-manager
```

## Question Description

You are tasked with implementing a simplified, in-memory distributed transaction manager. This system should coordinate atomic transactions across multiple independent services. Due to the limitations of the environment, you'll need to provide a solution that emphasizes reliability, concurrency and performance under heavy workloads.

**Scenario:**

Imagine a microservices architecture where multiple services (e.g., `UserService`, `ProductService`, `OrderService`) need to participate in a single transaction. For example, creating a new user might involve updating the `UserService` database, the `ProductService` inventory (if the user receives a free product), and the `OrderService` to create a welcome order. All these operations need to happen atomically: either all succeed, or none at all.

**Requirements:**

1.  **Transaction Coordinator:** Implement a `TransactionCoordinator` struct that manages the lifecycle of distributed transactions. It should provide methods for:
    *   `begin_transaction()`: Initiates a new transaction and returns a unique transaction ID.
    *   `register_participant(transaction_id, participant)`: Registers a `Participant` with the coordinator for a given transaction. A `Participant` represents a service involved in the transaction.
    *   `prepare_transaction(transaction_id)`: Signals all registered participants to prepare for the transaction commit. Participants should perform necessary checks (e.g., data validation, resource availability) and return a `PreparedResult`.
    *   `commit_transaction(transaction_id)`: If all participants have successfully prepared, signals them to commit the transaction.
    *   `rollback_transaction(transaction_id)`: If any participant fails to prepare, or if the coordinator decides to abort the transaction, signals all participants to rollback.
    *   `get_transaction_state(transaction_id)`: Returns the current state of the transaction (e.g., Active, Prepared, Committed, Aborted).

2.  **Participant Trait:** Define a `Participant` trait with the following methods:
    *   `prepare(transaction_id)`: Called by the coordinator to ask the participant to prepare for the commit. Returns a `PreparedResult`.
    *   `commit(transaction_id)`: Called by the coordinator to signal the participant to commit the transaction.
    *   `rollback(transaction_id)`: Called by the coordinator to signal the participant to rollback the transaction.

3.  **PreparedResult Enum:** Define a `PreparedResult` enum with the following variants:
    *   `Ready`: The participant is ready to commit.
    *   `ReadOnly`: The participant did not make any changes and does not need to commit or rollback.
    *   `Aborted(String)`: The participant cannot commit and the transaction must be rolled back. The `String` contains a reason for the abort.

4.  **Concurrency:** The `TransactionCoordinator` must support concurrent transactions. Ensure that multiple transactions can be active, prepared, committed, or rolled back simultaneously without data races or deadlocks. Use appropriate synchronization primitives (e.g., `Mutex`, `RwLock`, `Arc`) to protect shared state.

5.  **Reliability:** The system should handle participant failures gracefully. If a participant crashes during the prepare, commit, or rollback phase, the coordinator should be able to recover and ensure the transaction eventually reaches a consistent state. (For simplicity, assume that participant failures are permanent and that the coordinator must proceed without them.  Do not implement persistent storage).

6.  **Optimization:** Design your solution with performance in mind. Minimize lock contention, avoid unnecessary copying of data, and use efficient data structures. Pay attention to algorithmic complexity.

**Constraints:**

*   All data must be stored in memory. No external databases or persistent storage are allowed.
*   The number of participants in a transaction is limited to 100.
*   The maximum number of concurrent transactions is limited to 1000.
*   The system must be implemented in Rust, leveraging its ownership and concurrency features.
*   Focus on correctness, concurrency, and performance. Code readability and maintainability are also important.
*   Assume that network communication between the coordinator and participants is reliable (no message loss or corruption).
*   Participants are independent and may have different latencies for prepare, commit, and rollback operations.

**Edge Cases and Considerations:**

*   **Duplicate Registrations:** Handle the case where the same participant is registered multiple times for the same transaction.
*   **Non-Existent Transactions:** Handle attempts to prepare, commit, or rollback transactions that do not exist.
*   **Idempotency:**  While the participants themselves are assumed to be reliable regarding idempotency, consider how your design could facilitate idempotent operations at the coordinator level.
*   **Timeouts:** Consider a scenario where a participant is slow to respond to a prepare request. How could you incorporate timeouts without unduly complicating the core logic? (A basic timeout mechanism is sufficient, no need for advanced strategies).

This problem requires a solid understanding of Rust's concurrency features, advanced data structures, and distributed systems concepts. The solution should be well-structured, efficient, and robust. Good luck!
