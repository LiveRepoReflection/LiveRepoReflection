## Problem: Distributed Transaction Coordinator

**Description:**

You are tasked with building a simplified, but robust, distributed transaction coordinator (DTC) for a system involving multiple microservices. These microservices, let's call them Resource Managers (RMs), handle different aspects of a financial transaction (e.g., account balance updates, order placement, inventory adjustments). Your DTC must ensure ACID properties (Atomicity, Consistency, Isolation, Durability) across these services, even in the face of network failures and RM crashes.

**Scenario:**

Imagine an e-commerce platform where a user places an order. This involves:

1.  Reserving inventory in the Inventory Service (RM1).
2.  Creating an order record in the Order Service (RM2).
3.  Debit the user's account in the Account Service (RM3).

All three operations must succeed or fail together. If any of them fail, the entire transaction needs to be rolled back.

**Requirements:**

1.  **Two-Phase Commit (2PC) Protocol:** Implement the 2PC protocol to coordinate transactions across the RMs.
    *   **Phase 1 (Prepare):** The DTC sends a "prepare" message to all participating RMs. Each RM attempts to perform its part of the transaction and replies with either "vote commit" or "vote abort".  If any RM votes to abort, the entire transaction must be aborted.
    *   **Phase 2 (Commit/Rollback):** Based on the votes received in Phase 1, the DTC sends either a "commit" or "rollback" message to all RMs. Each RM then either persists the changes (commit) or reverts to its previous state (rollback).

2.  **Crash Recovery:** Implement a mechanism for the DTC to recover from crashes. The DTC must be able to determine the state of ongoing transactions after a restart and resume the 2PC protocol accordingly. This is critical for durability.

3.  **Idempotency:** RMs must be idempotent. That is, if the DTC sends a "commit" or "rollback" message multiple times due to network issues or DTC restarts, the RM should only execute the operation once.

4.  **Concurrency:** Handle multiple concurrent transactions.  Ensure that transactions are properly isolated from each other. Consider potential deadlocks and implement a simple deadlock prevention or detection mechanism.

5.  **Scalability:** While a full-scale distributed system isn't required, design your DTC in a way that it could be potentially scaled to handle a large number of RMs and transactions. Think about how you would distribute the DTC's state and coordination responsibilities.

**Constraints:**

*   **RM Interaction:** You can simulate the RMs. Assume they provide simple interfaces for prepare, commit, and rollback operations. These operations can be mocked or implemented with in-memory data structures. You don't need to implement actual external service calls.
*   **Logging:** Use a simple, persistent logging mechanism (e.g., file-based logging) to record the state of transactions.  This is crucial for crash recovery.
*   **Network Simulation:** Simulate network failures (e.g., dropped messages, delayed responses) to test the robustness of your DTC.
*   **Optimizations:** While correctness is paramount, consider optimizations like batching messages or parallelizing operations to improve performance.

**Evaluation Criteria:**

*   **Correctness:** Does the DTC correctly implement the 2PC protocol and ensure ACID properties?
*   **Robustness:** Can the DTC handle network failures and crashes without losing data or violating consistency?
*   **Concurrency:** Does the DTC properly handle concurrent transactions and prevent deadlocks?
*   **Design:** Is the DTC well-designed, modular, and scalable?
*   **Code Quality:** Is the code clean, well-documented, and easy to understand?

This problem requires a strong understanding of distributed systems concepts, transaction management, and concurrency control. It challenges the solver to design and implement a complex system that can handle real-world failure scenarios. Good luck!
