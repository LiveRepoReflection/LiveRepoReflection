## The Distributed Key-Value Store with Eventual Consistency

**Question Description:**

You are tasked with designing and implementing a simplified, distributed key-value store with eventual consistency. This system will simulate how data can be replicated across multiple nodes in a distributed environment.

**Core Requirements:**

1.  **Key-Value Storage:** Implement a basic key-value store. Keys and values are strings.

2.  **Nodes:** Your system should simulate a cluster of `N` nodes (where `N` is configurable). Each node maintains its own local copy of the key-value store.

3.  **Write Operations:** When a write operation (setting a value for a key) occurs on *one* node, the change is initially applied only to that node's local store.

4.  **Replication/Synchronization:** Implement a synchronization mechanism between the nodes.  This mechanism should periodically propagate updates (key-value pairs) from each node to all other nodes in the cluster. The propagation should happen in a "gossip" style, where each node randomly selects a subset of other nodes to share its updates with.

5.  **Eventual Consistency:**  Due to the asynchronous nature of replication, different nodes might have different versions of the same key at a given time. Your system must eventually converge to a consistent state across all nodes. This means that, given enough time and synchronization cycles, all nodes should ideally have the same latest value for any given key.

6.  **Conflict Resolution:** In cases where multiple nodes concurrently update the same key, a conflict resolution strategy is required. Implement a "Last Write Wins" (LWW) strategy based on timestamps. Each key-value pair should be associated with a timestamp indicating when it was last updated. During synchronization, if a node receives an update for a key it already has, it should compare the timestamps and only update its local value if the received timestamp is newer.

7.  **Read Operations:** Read operations can be performed on any node. When reading a key, the node should return the value it currently has in its local store.

**Constraints and Challenges:**

*   **Scale:** The system should be designed to handle a reasonably large number of nodes (e.g., up to 100). Consider how your data structures and algorithms will scale with increasing node count.
*   **Concurrency:**  Multiple write and read operations can occur concurrently on different nodes. Ensure your implementation is thread-safe (or equivalent in Javascript concurrency model) to avoid data corruption.
*   **Partial Failures:** Simulate node failures by occasionally making nodes unavailable for synchronization. The system should be resilient to these partial failures and continue to converge towards consistency.
*   **Optimization:** While eventual consistency allows for some delay, strive for reasonable convergence speed. Consider techniques to optimize the synchronization process (e.g., only propagating updates that haven't been seen by a node).
*   **Timestamp Generation:**  Ensure the timestamp generation is monotonically increasing within each node. If you are using `Date.now()`, consider using a sequence counter to avoid potential issues with clock drift or slight variations in timing.

**Input/Output (Conceptual):**

The focus is on designing the data structures and algorithms for the distributed system. You do not need to implement a specific input/output interface like reading from a file or a network socket. Instead, focus on creating functions and classes that allow you to:

*   Create and configure nodes.
*   Perform write operations on specific nodes.
*   Perform read operations on specific nodes.
*   Trigger synchronization cycles between nodes.
*   Simulate node failures and recoveries.
*   Verify eventual consistency (e.g., by comparing the values of keys across all nodes after a sufficient number of synchronization cycles).

**Evaluation Criteria:**

*   **Correctness:** Does the system correctly implement the key-value store, replication, and conflict resolution logic?
*   **Efficiency:** How quickly does the system converge to a consistent state?
*   **Scalability:** How well does the system perform with a large number of nodes?
*   **Resilience:** How well does the system handle node failures?
*   **Code Quality:** Is the code well-structured, readable, and maintainable?
*   **Design Choices:** Are the design choices well-justified and appropriate for the problem?

This problem emphasizes the design and implementation of a distributed system, focusing on data consistency, fault tolerance, and scalability. Successfully solving this problem requires a solid understanding of distributed systems concepts and the ability to translate those concepts into efficient and robust code. Good luck!
