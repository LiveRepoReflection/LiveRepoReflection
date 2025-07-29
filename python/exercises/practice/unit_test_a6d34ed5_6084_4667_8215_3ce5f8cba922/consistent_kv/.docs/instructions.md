## Problem: Distributed Key-Value Store with Consistency Guarantees

**Description:**

You are tasked with designing and implementing a simplified, in-memory distributed key-value store. This key-value store should support the following operations:

*   `put(key, value)`: Stores the `value` associated with the given `key`.
*   `get(key)`: Retrieves the `value` associated with the given `key`.
*   `delete(key)`: Removes the `key` and its associated `value`.

The key-value store will be distributed across multiple nodes in a network. Your solution must handle the following challenges:

1.  **Data Distribution:** Implement a consistent hashing mechanism to distribute keys evenly across the nodes.

2.  **Replication:** Replicate each key-value pair across `N` nodes (replication factor) to ensure data availability and fault tolerance.  The `N` nodes should be determined by the consistent hashing ring.

3.  **Consistency:** Implement a read repair mechanism to maintain eventual consistency. When a client reads a key, your system should check the values from all `N` replicas. If inconsistencies are detected, the system should update the outdated replicas with the most recent value.

4.  **Concurrency:** Handle concurrent `put`, `get`, and `delete` requests from multiple clients. Use appropriate locking or synchronization mechanisms to prevent data corruption.

5.  **Node Failures:** Your system should be resilient to node failures. When a node goes down, the system should continue to function correctly, serving requests from the remaining nodes. No rebalancing is required. Only the replication factor will decrease.

6.  **Scalability:** Design your system to be scalable to a large number of nodes and clients.

**Constraints:**

*   Assume a fixed number of nodes in the cluster.
*   Nodes are identified by unique integer IDs.
*   The network is unreliable, but messages are eventually delivered (no message loss).
*   The replication factor `N` is a configurable parameter.
*   The key-value store is in-memory only; data is not persisted to disk.
*   For simplicity, you don't need to implement node discovery or membership protocols. You can assume that each node knows the IDs of all other nodes in the cluster.
*   You should optimize for read performance while ensuring eventual consistency.
*   Implement efficient data structures and algorithms to minimize latency and maximize throughput.

**Input:**

*   A list of node IDs representing the nodes in the cluster.
*   The replication factor `N`.
*   A sequence of `put`, `get`, and `delete` requests from multiple clients.

**Output:**

*   For each `get` request, return the value associated with the key, or `None` if the key does not exist.
*   The `put` and `delete` requests do not have a return value.
*   All operations should complete successfully, even in the presence of node failures and concurrent requests.

**Example:**

```
Nodes: [1, 2, 3, 4, 5]
Replication Factor: 3

Requests:
1. put("key1", "value1")
2. get("key1")  // Returns "value1"
3. put("key2", "value2")
4. get("key2")  // Returns "value2"
5. delete("key1")
6. get("key1")  // Returns None
```

**Considerations:**

*   How will you handle conflicts when multiple clients write to the same key concurrently?
*   How will you ensure that the read repair mechanism does not introduce inconsistencies?
*   How will you choose the `N` nodes for replication?
*   What data structures will you use to store the key-value pairs on each node?
*   How will you handle node failures gracefully?

This problem requires a deep understanding of distributed systems concepts, data structures, and algorithms. It challenges you to design a scalable and resilient key-value store that can handle concurrent requests and node failures. Good luck!
