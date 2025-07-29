## The Distributed Transaction Coordinator

**Problem Description:**

You are tasked with designing and implementing a distributed transaction coordinator (DTC) for a highly distributed system. This system consists of a set of *N* independent services (numbered from 1 to *N*), each responsible for managing its own local data. These services need to participate in atomic transactions that span multiple services.

Your DTC must ensure the ACID properties (Atomicity, Consistency, Isolation, Durability) for these distributed transactions. Implement a two-phase commit (2PC) protocol within the DTC.

**Input:**

The input describes a series of transactions. Each transaction is defined by:

1.  A unique transaction ID (TID), which is a positive integer.
2.  A set of services involved in the transaction.
3.  For each service involved, an operation to be performed (e.g., "UPDATE account SET balance = balance - 100 WHERE id = 123"). The specific operation format doesn't matter; treat it as a string.
4.  A boolean indicating whether the transaction should succeed ("COMMIT") or fail ("ROLLBACK"). This is a deterministic test case for your coordinator.

The input will be provided as a list of transaction descriptions. The format is as follows:

```
<TID> <COMMIT/ROLLBACK> <Service1>:<Operation1> <Service2>:<Operation2> ... <ServiceK>:<OperationK>
```

Example:

```
1 COMMIT 1:UPDATE accounts SET balance = balance - 100 WHERE id = 123 2:INSERT INTO orders (account_id, amount) VALUES (123, 100)
2 ROLLBACK 1:UPDATE accounts SET balance = balance - 50 WHERE id = 456 3:DELETE FROM products WHERE id = 789
```

**Assumptions and Constraints:**

*   **Number of Services (N):** 1 <= N <= 100
*   **Number of Transactions:** 1 <= Number of transactions <= 1000
*   **Number of Services per Transaction (K):** 1 <= K <= N
*   **Transaction IDs (TID):** Positive integers, unique for each transaction.
*   **Service IDs:** Integers from 1 to N.
*   **Network:** Assume a reliable network with guaranteed message delivery (no packet loss or corruption).
*   **Fault Tolerance:** Your DTC *must* be resilient to service failures *during* the transaction process. If a service fails *after* voting to commit but *before* receiving the final commit decision, it *must* still commit the transaction upon recovery.  Simulate service failure by simply not responding. Your DTC should have a timeout mechanism for handling unresponsive services.
*   **Concurrency:** Multiple transactions can be initiated concurrently. The DTC must handle concurrent transactions correctly, ensuring isolation.
*   **Durability:** The decision to commit or rollback a transaction must be persistently stored by the DTC before informing the participants.
*   **No Central Database:**  The DTC cannot rely on a central database to store transaction state.  It must use a distributed consensus mechanism (e.g., a simplified version of Paxos or Raft) to ensure agreement on the transaction outcome. You can implement a simple leader election process to designate a coordinator.  If the leader fails, a new leader must be elected.
*   **Idempotency:**  The operations performed by each service *must* be idempotent.  That is, performing the same operation multiple times should have the same effect as performing it once. This is crucial for handling potential retransmissions during the commit phase.

**Output:**

For each transaction, the DTC should output the following:

*   `COMMIT <TID>` if the transaction committed successfully.
*   `ROLLBACK <TID>` if the transaction rolled back.

These messages should be printed to standard output *only after* the transaction has been definitively committed or rolled back (including persistent storage of the decision).

**Evaluation Criteria:**

Your solution will be evaluated based on the following criteria:

1.  **Correctness:** Adherence to the ACID properties and the 2PC protocol.  The output must correctly reflect the intended outcome of each transaction (COMMIT or ROLLBACK).
2.  **Fault Tolerance:** Ability to handle service failures during the transaction process.
3.  **Concurrency:** Correct handling of concurrent transactions.
4.  **Performance:** Minimize the latency of transactions.  Consider the communication overhead and the complexity of the distributed consensus mechanism.
5.  **Code Quality:** Clarity, maintainability, and adherence to good coding practices.

**Example Interaction (Simplified):**

Let's say you have 3 services and the following input:

```
1 COMMIT 1:UPDATE accounts SET balance = balance - 100 WHERE id = 123 2:INSERT INTO orders (account_id, amount) VALUES (123, 100) 3:UPDATE inventory SET quantity = quantity - 1 WHERE product_id = 456
```

A possible (simplified) interaction flow:

1.  DTC receives transaction 1.
2.  DTC enters the prepare phase and sends "PREPARE" messages to services 1, 2, and 3.
3.  Services 1, 2, and 3 respond with "VOTE_COMMIT" (assuming they can perform the operations).
4.  DTC reaches a consensus (e.g., using a simplified Raft) to commit transaction 1.  This decision is persistently stored.
5.  DTC sends "COMMIT" messages to services 1, 2, and 3.
6.  Services 1, 2, and 3 perform the operations.
7.  DTC outputs `COMMIT 1`.

If any service had responded with "VOTE_ABORT" or timed out during the prepare phase, the DTC would have reached a consensus to rollback and sent "ROLLBACK" messages.

**This is a challenging problem that requires careful consideration of distributed systems concepts, concurrency control, fault tolerance, and performance optimization. Good luck!**
