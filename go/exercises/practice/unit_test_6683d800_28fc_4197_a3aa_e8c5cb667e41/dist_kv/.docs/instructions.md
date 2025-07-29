## Problem: Distributed Key-Value Store with Consistency Guarantees

**Description:**

You are tasked with designing and implementing a simplified version of a distributed key-value store. This system consists of multiple server nodes that store data and handle client requests. The challenge lies in maintaining data consistency across all nodes while ensuring reasonable performance under concurrent read and write operations.

**Core Requirements:**

1.  **Basic Key-Value Operations:** Implement the standard `Get(key)` and `Put(key, value)` operations. `Get(key)` should return the most recent value associated with the key. `Put(key, value)` should store the value associated with the key.

2.  **Data Replication:** Implement data replication across a configurable number of nodes (`replication_factor`). Each key-value pair should be stored on `replication_factor` different nodes.

3.  **Eventual Consistency (with causal consistency):** Implement an eventual consistency model.  All updates should eventually propagate to all replicas, but reads may return stale data temporarily. *Causal consistency* must be respected. If client A writes a value for key 'x', and then client B reads that value for key 'x', any subsequent reads of 'x' by client B must return that value or a later value.

4.  **Conflict Resolution:** In cases of concurrent writes to the same key, implement a Last Write Wins (LWW) conflict resolution strategy based on timestamps. Each value should be associated with a timestamp. Nodes must maintain correct timestamp ordering to resolve conflicts.

5.  **Node Failure Handling:** The system must be able to tolerate node failures. If a node fails, read and write operations should still be possible (with reduced performance and potential staleness during the recovery period).

**Constraints:**

*   **Number of Nodes:** The system should be designed to handle a cluster of up to 100 nodes.
*   **Data Size:** Each value can be up to 1MB in size.
*   **Concurrency:** The system must handle a high degree of concurrency (hundreds or thousands of concurrent requests).
*   **Latency:** While strict latency guarantees are not required, the system should strive to provide reasonable read and write latency (e.g., less than 500ms for the majority of operations under normal load).
*   **Timestamp Generation:** The timestamp must be monotonically increasing even across distributed nodes. Consider how you will achieve this in a distributed environment.  Simple system clocks are generally insufficient.
*   **Network Communication:** You can assume a reliable network transport protocol (e.g., TCP).
*   **No external dependencies allowed except standard Go libraries.**

**Bonus Challenges:**

*   **Implement vector clocks instead of timestamps for more robust causality tracking.**
*   **Implement hints for faster data synchronization after node failures.**
*   **Implement data partitioning (sharding) to improve scalability.**
*   **Add support for data deletion.**
*   **Implement a more sophisticated consistency model (e.g., read-your-writes consistency).**

**Grading Criteria:**

*   **Correctness:** The system must correctly implement the specified key-value operations and consistency guarantees.
*   **Efficiency:** The system should be reasonably efficient in terms of resource usage (CPU, memory, network bandwidth).
*   **Fault Tolerance:** The system should be able to tolerate node failures without data loss or service interruption.
*   **Code Quality:** The code should be well-structured, readable, and maintainable.
*   **Design Decisions:** Justification of design choices and trade-offs. Clear documentation of the implemented algorithms and data structures.
