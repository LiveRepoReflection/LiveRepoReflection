## Project Name

```
Distributed-Locking-Service
```

## Question Description

You are tasked with designing and implementing a simplified distributed locking service. This service allows multiple clients in a distributed system to acquire and release locks on shared resources, preventing race conditions and ensuring data consistency.

Your system must provide the following functionalities:

1.  **Lock Acquisition:** A client can request a lock on a specific resource (identified by a unique string key). The lock should be granted only if it's currently free. If the lock is already held by another client, the requesting client should wait until the lock becomes available or a specified timeout is reached.
2.  **Lock Release:** A client can release a lock they previously acquired. Releasing a lock makes it available for other waiting clients.
3.  **Timeout:** Each lock acquisition request can have an associated timeout. If the lock cannot be acquired within the timeout period, the request should fail, and the client should be notified.
4.  **Heartbeat (Lease Extension):** To prevent locks from being held indefinitely due to client failures, the service should support a heartbeat mechanism. Clients holding a lock must periodically send a heartbeat signal to the service to extend the lock's lease. If the service doesn't receive a heartbeat within a configurable lease duration, the lock should be automatically released.
5.  **Idempotency:** The lock acquisition and release operations should be idempotent.  Duplicate requests for the same operation should not cause unintended side effects.

**Constraints:**

*   **Concurrency:** The service must handle concurrent lock requests from multiple clients efficiently.
*   **Scalability:** The service should be designed to scale horizontally to handle a large number of locks and clients. (Consider the sharding aspect)
*   **Fault Tolerance:** The service should be resilient to failures. (Consider how to handle the failure of parts of your service.)
*   **Efficiency:** Minimize latency for lock acquisition and release.
*   **Communication:** You can assume a reliable, ordered message passing system between clients and the service (e.g., using TCP or a message queue).
*   **Implementation:** Implement the core locking logic in Python. Focus on the algorithms and data structures involved.  Assume you have access to basic networking and concurrency primitives.

**Specific Requirements:**

*   Implement the core data structures and algorithms for managing locks. You can use in-memory data structures for simplicity, but discuss how you would persist the state for production use.
*   Implement functions for `acquire_lock(resource_id, client_id, timeout)` and `release_lock(resource_id, client_id)` and `heartbeat(resource_id, client_id)`.
*   The `acquire_lock` function should return `True` if the lock is acquired successfully, and `False` otherwise (e.g., due to timeout).
*   Consider possible race conditions and implement appropriate synchronization mechanisms (e.g., locks, semaphores) to ensure correctness.
*   Discuss the tradeoffs of different approaches to handling timeouts and lease extensions.
*   Briefly outline how you would shard the lock management across multiple servers to improve scalability.
*   Briefly discuss strategies for handling server failures and ensuring lock availability.

**Evaluation Criteria:**

*   Correctness: The locking service must correctly acquire and release locks, preventing concurrent access to shared resources.
*   Efficiency: The service should minimize latency for lock acquisition and release.
*   Scalability: The design should be scalable to handle a large number of locks and clients.
*   Fault Tolerance: The service should be resilient to failures.
*   Code Quality: The code should be well-structured, readable, and maintainable.
*   Design Rationale: The solution should clearly explain the design choices made and the tradeoffs considered.
