## Project Name

`DistributedTransactionManager`

## Question Description

You are tasked with designing and implementing a simplified, in-memory, distributed transaction manager (DTM). This DTM will coordinate transactions across multiple independent service instances (simulated in-memory). The goal is to ensure atomicity: either all participating service instances commit their changes, or all rollback.

**Scenario:**

Imagine a system where transferring funds between bank accounts requires updating balances in multiple independent account services. Each service instance manages a subset of accounts. A single transaction might involve multiple service instances.

**Requirements:**

1.  **Transaction ID Generation:** Implement a mechanism to generate unique transaction IDs (UUIDs are acceptable).
2.  **Transaction Start/Commit/Rollback:** Implement methods for starting a transaction, committing a transaction, and rolling back a transaction.
3.  **Service Instance Registration:** Implement a way for service instances to register themselves with the DTM. A service instance provides a unique ID (String) and a callback function (`Callable<Boolean> commit` and `Callable<Boolean> rollback`) to the DTM.
4.  **Transaction Participation:** Allow transactions to "enlist" service instances. When a transaction enlists a service instance, the DTM records that the service instance is participating in the transaction.
5.  **Two-Phase Commit (2PC) Protocol:** Implement a simplified 2PC protocol.
    *   **Phase 1 (Prepare):** When a transaction is committed, the DTM iterates through all enlisted service instances and invokes their `commit` callback.  If *any* callback returns `false` or throws an exception, the entire transaction must be rolled back.
    *   **Phase 2 (Commit or Rollback):**
        *   **Commit:** If all `commit` callbacks in Phase 1 return `true` successfully, the DTM considers the transaction committed.  While there's no explicit "commit" phase in this simplified model (the `commit` callbacks *are* the commit), the DTM must record the transaction's final status as committed.
        *   **Rollback:** If any `commit` callback in Phase 1 returns `false` or throws an exception, the DTM iterates through all enlisted service instances (including those that succeeded in Phase 1) and invokes their `rollback` callback. The DTM must record the transaction's final status as rolled back.
6.  **Concurrency:** The DTM must be thread-safe, allowing multiple concurrent transactions.  Use appropriate synchronization mechanisms.
7.  **Idempotency (Important):** The `commit` and `rollback` callbacks provided by service instances must be idempotent.  This means that if a callback is called multiple times for the same transaction, the result should be the same as if it were called only once. This is crucial because network issues or DTM failures might lead to retries. This requirement is very important.
8.  **Timeout:** Implement a timeout mechanism for the prepare phase. If a service instance does not respond within a specified timeout period (e.g., 5 seconds), the transaction should be rolled back.
9.  **Transaction Status:** Provide methods to check the status of a transaction (e.g., `ACTIVE`, `COMMITTED`, `ROLLED_BACK`).
10. **Error Handling:** Handle potential exceptions during `commit` and `rollback` gracefully. Log errors and ensure that rollback attempts are made even if some service instances fail during rollback.

**Constraints:**

*   You are responsible for providing all necessary data structures and synchronization mechanisms.
*   Assume the service instances are reliable within themselves (i.e., they won't crash mid-transaction). The focus is on coordinating the transaction across instances.
*   Simulate the service instances in-memory; you don't need to interact with external databases or systems.
*   Optimize for speed and low latency, given the in-memory nature of the simulation.  Avoid unnecessary locking or blocking.
*   The number of service instances participating in a transaction can be very large. Optimize for this scenario.
*   The DTM must be robust. It should handle edge cases such as service instance failures, timeouts, and concurrent transactions correctly.

**Evaluation Criteria:**

*   Correctness: The DTM must correctly implement the 2PC protocol and ensure atomicity.
*   Concurrency: The DTM must be thread-safe and handle concurrent transactions efficiently.
*   Performance: The DTM should be optimized for low latency and high throughput.
*   Robustness: The DTM should handle errors and edge cases gracefully.
*   Code Quality: The code should be well-structured, readable, and maintainable.
*   Idempotency: The `commit` and `rollback` callbacks MUST be called in idempotent ways.

This problem requires careful design and implementation of data structures, synchronization, and error handling to create a robust and efficient distributed transaction manager. The focus is on ensuring atomicity in a concurrent and potentially failure-prone environment.
