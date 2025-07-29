## Problem: Distributed Transaction Coordinator

**Description:**

You are tasked with designing and implementing a distributed transaction coordinator for a simplified banking system. This system consists of multiple independent bank servers, each responsible for managing a subset of customer accounts. The goal is to ensure ACID properties (Atomicity, Consistency, Isolation, Durability) when transferring funds between accounts residing on *different* bank servers. Transfers within the same bank server are handled locally and do not involve the distributed transaction coordinator.

The system operates under the following constraints:

1.  **Network Unreliability:** Communication between the transaction coordinator and bank servers is inherently unreliable. Messages can be lost, delayed, or duplicated.
2.  **Server Failures:** Bank servers can crash or become unavailable at any time. The transaction coordinator should be resilient to such failures.
3.  **Concurrency:** Multiple transactions can be initiated concurrently, requiring proper isolation to prevent data corruption.
4.  **Limited Resources:** Bank servers have limited memory and processing power. The transaction coordinator should minimize the resource footprint on these servers.
5.  **Strict Ordering:** While individual bank servers must maintain a strict order of operations, global ordering is not needed.
6.  **Eventual Consistency:** In cases where a failure may occur, eventual consistency is acceptable, but the system must converge to a correct state.

**Requirements:**

1.  **Implement a Two-Phase Commit (2PC) protocol, or a variant, to coordinate distributed transactions.** You are free to adapt the standard 2PC protocol to optimize for the banking system's specific requirements and constraints. Consider alternatives like Paxos or Raft for consensus.
2.  **Design the message format for communication between the transaction coordinator and bank servers.** This format should be efficient, reliable (consider sequence numbers and acknowledgements), and secure.
3.  **Implement a mechanism for detecting and recovering from server failures.** This may involve timeouts, heartbeats, and transaction logging.
4.  **Implement mechanisms to avoid deadlocks.** Ensure that transactions don't get stuck waiting for resources held by other transactions indefinitely.
5.  **Provide a Java API for initiating distributed transactions.** This API should allow a client to specify the source account, destination account, and amount to transfer.
6.  **Implement an idempotent operation for applying transactions on the bank servers.** The system should be able to handle duplicate transaction requests without double-applying the transaction.
7.  **Implement a mechanism to address the "lost update" anomaly when multiple concurrent transactions attempt to modify the same account balance.** You can employ optimistic or pessimistic locking techniques.

**Constraints:**

1.  **All communication must be asynchronous.** Do not use blocking I/O operations.
2.  **You are encouraged to use existing libraries and frameworks for networking, concurrency, and persistence.** However, you must implement the core transaction coordination logic yourself.
3.  **The solution must be scalable to handle a large number of bank servers and concurrent transactions.**
4.  **The solution must be thoroughly documented, including a description of the chosen protocol, the message format, the failure recovery mechanism, and the API.**

**Evaluation Criteria:**

1.  **Correctness:** The solution must correctly implement the distributed transaction protocol and ensure ACID properties.
2.  **Performance:** The solution must be efficient and scalable, minimizing the overhead of transaction coordination.
3.  **Fault Tolerance:** The solution must be resilient to network unreliability and server failures.
4.  **Resource Utilization:** The solution must minimize the resource footprint on bank servers.
5.  **Code Quality:** The code must be well-structured, documented, and easy to understand.
6.  **Design Rationale:** The solution must provide a clear justification for the chosen design decisions and trade-offs.
7.  **Deadlock Avoidance:** The solution must effectively avoid deadlocks.

This problem requires a deep understanding of distributed systems concepts, transaction processing, and fault tolerance. It challenges the solver to design and implement a robust and scalable distributed transaction coordinator that can handle real-world constraints. Good luck!
