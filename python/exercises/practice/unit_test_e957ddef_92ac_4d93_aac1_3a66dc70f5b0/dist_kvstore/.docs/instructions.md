## Problem Title: Distributed Key-Value Store with Consistent Hashing and Fault Tolerance

### Problem Description:

You are tasked with designing and implementing a simplified, distributed key-value store. This system should be able to handle a large number of requests concurrently while maintaining data consistency and availability even in the face of node failures.

**Core Requirements:**

1.  **Consistent Hashing:** Implement consistent hashing to distribute keys across multiple nodes in the cluster. Use a ring-based approach with virtual nodes (replicas) to improve distribution and fault tolerance. You should be able to dynamically add or remove nodes from the cluster with minimal key redistribution.

2.  **Basic Key-Value Operations:** Implement the following operations:

    *   `put(key, value)`: Stores the value associated with the given key.
    *   `get(key)`: Retrieves the value associated with the given key. Returns `None` if the key does not exist.
    *   `delete(key)`: Deletes the key-value pair associated with the given key.

3.  **Fault Tolerance via Replication:** Implement data replication to handle node failures. Each key-value pair should be replicated on `N` different nodes (where `N` is configurable). When a node fails, the system should automatically recover the data from its replicas.

4.  **Read/Write Consistency:** Implement strong consistency for both read and write operations. This means that after a successful write, all subsequent reads should return the latest written value. Consider using a consensus algorithm (e.g., Paxos, Raft - a simplified version is acceptable) for write operations to ensure consistency across replicas.

5.  **Node Joining/Leaving:** Implement mechanisms for nodes to join and leave the cluster gracefully. When a node joins, it should take over a portion of the key space from existing nodes. When a node leaves (either voluntarily or due to failure), its data should be redistributed to other nodes. Minimise the data movement during these operations.

6.  **Concurrency:** The system must handle concurrent requests efficiently. Use appropriate locking mechanisms or concurrency control techniques to prevent race conditions and ensure data integrity.

**Constraints and Edge Cases:**

*   **Network Partitions:** Your system does NOT need to fully handle network partitions (CAP Theorem favors Consistency). Assume that the network is mostly reliable, and partitions are rare and transient.
*   **Key/Value Size:** Assume that keys and values are relatively small (e.g., strings or small objects). You don't need to handle extremely large values.
*   **Number of Nodes:** The cluster size can vary from a few nodes to hundreds of nodes.
*   **Performance:** Optimize for read and write latency. The system should be able to handle a high throughput of requests.
*   **Data Loss:** The system should minimize the risk of data loss, even in the face of multiple node failures (up to `N-1` failures where `N` is the replication factor).
*   **Node Discovery:** Assume a simplified node discovery mechanism exists (e.g., a configuration file or a central registry that lists all active nodes). You do not need to implement a full-fledged distributed discovery service.
*   **Security:** Security considerations (authentication, authorization, encryption) are out of scope for this problem.

**Optimization Requirements:**

*   **Minimize Key Redistribution:** When nodes join or leave the cluster, minimize the amount of data that needs to be redistributed.
*   **Efficient Replica Placement:** Choose replica placement strategies that maximize data availability and minimize the impact of correlated failures (e.g., placing replicas in different data centers or racks).
*   **Parallelism:** Exploit parallelism to speed up read and write operations. For example, you can perform asynchronous replication to improve write latency.

**System Design Aspects:**

*   **Modularity:** Design your code in a modular and extensible way. The different components of the system (consistent hashing, replication, consensus, storage) should be loosely coupled and easy to modify or replace.
*   **Scalability:** Consider how your design can be scaled to handle a larger number of nodes and requests.
*   **Monitoring:** Include basic monitoring capabilities to track the health and performance of the system (e.g., number of requests, latency, node status).

**Multiple Valid Approaches:**

There are several valid approaches to solving this problem, each with its own trade-offs. For example, you could use different consensus algorithms (Paxos vs. Raft), different replication strategies (chain replication vs. tree-based replication), or different storage engines (in-memory vs. disk-based). The key is to choose an approach that meets the core requirements and constraints while optimizing for performance and scalability.

**Difficulty:** Hard

This problem requires a strong understanding of distributed systems concepts, data structures, algorithms, and concurrency control. It also requires careful attention to detail to handle edge cases and ensure data consistency and availability.
