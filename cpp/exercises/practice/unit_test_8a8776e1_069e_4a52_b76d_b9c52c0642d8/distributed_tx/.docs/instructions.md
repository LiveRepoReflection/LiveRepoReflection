## Problem: Distributed Transaction Coordinator

**Description:**

You are tasked with designing and implementing a simplified distributed transaction coordinator for a system involving multiple microservices. Imagine a scenario where a user action requires updates across several independent services (e.g., updating user profile, modifying inventory, and logging the activity). To maintain data consistency, these updates must happen atomically – either all succeed, or all fail.

Each microservice exposes an API with two key endpoints:

1.  `Prepare(transaction_id)`: This endpoint simulates the service attempting to perform its part of the transaction. It checks for resource availability, performs necessary validation, and reserves any resources needed. If successful, it returns `true`; otherwise, it returns `false` (or throws an exception indicating failure).  Crucially, after a successful `Prepare`, the service *must* be able to either `Commit` or `Rollback` the transaction, even if it crashes and restarts.  This implies the service must persist the "prepared" state.

2.  `Commit(transaction_id)`:  This endpoint commits the changes associated with the given `transaction_id`. It finalizes the operation and releases any reserved resources.

3.  `Rollback(transaction_id)`: This endpoint undoes any changes made during the `Prepare` phase associated with the given `transaction_id`. It releases any reserved resources and returns the service to its original state before the transaction.

Your goal is to implement a central transaction coordinator that orchestrates these distributed transactions.

**Input:**

*   A list of microservice endpoints (URLs or addresses).
*   A user action that triggers a distributed transaction.

**Output:**

*   A success/failure indication of the overall transaction.
*   Log messages indicating the steps taken by the coordinator.

**Requirements:**

1.  **Atomicity:** The system must guarantee atomicity. All participating services must either commit their changes or rollback to their original state.
2.  **Durability:** Once the coordinator decides to commit or rollback, the outcome must be durable, even if the coordinator crashes.  Consider what data the coordinator itself needs to persist and how it persists it.
3.  **Concurrency:** The coordinator must be able to handle multiple concurrent transactions.
4.  **Fault Tolerance:** The coordinator should be resilient to service failures. If a service fails during the `Prepare` phase, the coordinator should rollback all other services. If a service fails during the `Commit` or `Rollback` phase, the coordinator must retry until the operation succeeds (idempotency is key).
5.  **Idempotency:** The `Commit` and `Rollback` operations on the microservices must be idempotent. This means that calling these operations multiple times with the same `transaction_id` should have the same effect as calling them once.  The coordinator *must* handle cases where `Commit` or `Rollback` requests are lost or retried.
6.  **Optimization:** Minimize the time required to complete a transaction. Consider parallelizing operations where possible.
7.  **Scalability:** Design the coordinator in a way that it can scale to handle a large number of microservices and concurrent transactions.  Consider potential bottlenecks.

**Constraints:**

*   Assume a simple network environment where messages can be lost or delayed.
*   You do not need to implement the microservices themselves. You can simulate their behavior (success/failure/delay) for testing purposes.
*   You can use any appropriate libraries or frameworks for handling network communication, concurrency, and persistence.
*   The number of microservices participating in a transaction can vary.
*   The network latency between the coordinator and the microservices can vary.

**Bonus Challenges:**

*   Implement a mechanism for detecting and resolving "in-doubt" transactions (transactions where the coordinator crashed before knowing the outcome of the transaction).
*   Add support for transaction timeouts.
*   Implement a distributed consensus algorithm (e.g., Raft, Paxos) to make the coordinator highly available.

This problem requires a deep understanding of distributed systems concepts, careful consideration of various failure scenarios, and efficient implementation of concurrency and network communication.  The focus is on the correctness and robustness of the transaction coordinator.
