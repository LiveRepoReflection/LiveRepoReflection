## Problem: Distributed Transaction Coordinator with Conflict Resolution

**Description:**

You are tasked with designing and implementing a distributed transaction coordinator for a highly concurrent, geographically distributed database system. This system guarantees ACID properties, even under network partitions and node failures.

The system consists of multiple data nodes spread across different regions. Each data node stores a shard of the overall data. Transactions can involve multiple data nodes, requiring a distributed transaction protocol to ensure consistency.

Your coordinator must manage concurrent transactions, detect and resolve conflicts (e.g., two transactions attempting to update the same data), and ensure data durability despite potential node failures and network instability.

**Specific Requirements:**

1.  **Transaction Management:**
    *   Implement a two-phase commit (2PC) protocol (or a more advanced protocol like Paxos or Raft if you desire an extra challenge) for coordinating transactions across multiple data nodes.
    *   Provide APIs for starting, committing, and aborting transactions.
    *   Handle transaction timeouts and automatically abort transactions that take too long.

2.  **Concurrency Control and Conflict Resolution:**
    *   Implement a locking mechanism (e.g., optimistic locking, pessimistic locking) to prevent conflicting transactions from corrupting data.
    *   Design a conflict resolution strategy (e.g., retry, abort one of the transactions) that minimizes the impact on overall system performance.
    *   Ensure that transactions are serializable (e.g., using strict two-phase locking) to maintain data consistency.

3.  **Fault Tolerance and Durability:**
    *   Implement a logging mechanism to record transaction state (prepared, committed, aborted) to disk to ensure durability.
    *   Design a recovery procedure that can be executed after a coordinator failure to restore the coordinator's state and complete or abort any in-flight transactions.
    *   Consider how to handle network partitions and ensure that transactions can still be committed or aborted in a consistent manner.

4.  **Performance and Scalability:**
    *   Minimize the latency and overhead of the transaction protocol to ensure high throughput.
    *   Design the coordinator to be scalable to handle a large number of concurrent transactions and data nodes.
    *   Consider techniques like batching, pipelining, and parallel processing to improve performance.

5.  **System Design Considerations:**
    *   Clearly define the interfaces and data structures used for communication between the coordinator and the data nodes.
    *   Consider the trade-offs between different design choices (e.g., optimistic vs. pessimistic locking, 2PC vs. Paxos) in terms of performance, complexity, and fault tolerance.
    *   Document your design decisions and explain the rationale behind them.

**Constraints:**

*   The system must be implemented in Java.
*   The coordinator should be able to handle a significant number of concurrent transactions (e.g., 10,000+).
*   The system should be able to tolerate node failures and network partitions without data loss or inconsistencies.
*   The latency of transaction commit operations should be minimized.

**Evaluation Criteria:**

*   Correctness: Does the system guarantee ACID properties?
*   Performance: What is the throughput and latency of the system under various workloads?
*   Fault tolerance: How well does the system handle node failures and network partitions?
*   Scalability: How does the system perform as the number of data nodes and concurrent transactions increases?
*   Code quality: Is the code well-structured, documented, and easy to understand?
*   Design: Is the system design well-thought-out and justified?
