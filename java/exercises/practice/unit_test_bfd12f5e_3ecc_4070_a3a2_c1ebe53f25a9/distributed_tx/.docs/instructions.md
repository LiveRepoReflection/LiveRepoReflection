## Problem: Distributed Transaction Manager

**Description:**

You are tasked with designing and implementing a simplified, in-memory Distributed Transaction Manager (DTM) for a microservices architecture.  This DTM will coordinate transactions across multiple participating services (resource managers, RMs). The goal is to ensure atomicity: either all operations across all RMs succeed, or all operations are rolled back, even in the face of failures.

**Scenario:**

Imagine an e-commerce system where placing an order involves multiple services:

1.  **Inventory Service (RM1):**  Reserves items from the inventory.
2.  **Payment Service (RM2):**  Authorizes payment.
3.  **Shipping Service (RM3):**  Creates a shipping order.

A transaction to place an order needs to atomically perform operations in all three services. If any of these operations fail (e.g., insufficient inventory, payment declined), the entire transaction must be rolled back to maintain data consistency.

**Requirements:**

1.  **Transaction Coordination:** Implement a `TransactionManager` class that manages the transaction lifecycle.  It should support the following operations:
    *   `begin()`: Starts a new distributed transaction and returns a unique transaction ID (UUID).
    *   `enlist(transactionId, resourceManager)`:  Registers a resource manager with the transaction. A resource manager must implement a `prepare()`, `commit()` and `rollback()` method. The resource manager object is passed as an interface.
    *   `prepare(transactionId)`:  Instructs all enlisted RMs to prepare for the commit.  Each RM performs necessary checks (e.g., validating sufficient inventory) and returns a boolean indicating success or failure.  This phase must be idempotent.
    *   `commit(transactionId)`:  If all RMs successfully prepared, instruct them to commit their changes.  This phase must also be idempotent.
    *   `rollback(transactionId)`:  If any RM failed to prepare, or if the commit fails, instruct all enlisted RMs to rollback their changes. This phase must be idempotent.

2.  **Resource Manager Interface:** Define a `ResourceManager` interface with `prepare()`, `commit()`, and `rollback()` methods. These methods should simulate performing operations on the underlying resources (e.g., updating a database).  They should also simulate potential failures (e.g., throwing exceptions, returning false).

3.  **Idempotency:** Ensure that `prepare()`, `commit()`, and `rollback()` methods of the `ResourceManager` interface are idempotent.  Meaning, calling them multiple times with the same transaction ID should have the same effect as calling them once.

4.  **Concurrency:** The `TransactionManager` should handle concurrent transactions correctly. Multiple threads might be attempting to begin, prepare, commit, or rollback transactions simultaneously.

5.  **Fault Tolerance (Simulated):** Implement mechanisms to simulate failures during the prepare and commit phases. Resource managers should have a configurable probability of failure (e.g., 20% chance of failing during prepare).

6. **Logging**: Implement a simple logging mechanism. Each transaction's progress (begin, prepare, commit, rollback, failures) should be logged to a file or the console.

**Constraints:**

*   Implement the solution in Java.
*   Use appropriate data structures and algorithms to optimize performance.  Consider the trade-offs between memory usage and execution time.
*   The solution should be thread-safe.
*   Simulate resource manager operations (no actual database interactions required).
*   The solution must handle a large number of concurrent transactions.
*   Minimize dependencies. Using external libraries should be justified.

**Evaluation Criteria:**

*   Correctness:  Does the solution correctly implement the DTM logic and ensure atomicity?
*   Concurrency:  Does the solution handle concurrent transactions safely and efficiently?
*   Fault Tolerance:  Does the solution gracefully handle simulated failures?
*   Idempotency: Are the resource manager operations idempotent?
*   Performance:  Is the solution performant and scalable?
*   Code Quality:  Is the code well-structured, readable, and maintainable?

This problem requires a good understanding of distributed systems concepts, concurrency, and exception handling.  It also requires careful design and implementation to achieve the desired correctness, performance, and fault tolerance characteristics. Good luck!
