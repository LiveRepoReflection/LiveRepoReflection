Okay, here's a problem designed to be quite challenging, incorporating several advanced concepts.

### Project Name

```
distributed-key-value-store
```

### Question Description

You are tasked with designing and implementing a simplified, in-memory distributed key-value store with eventual consistency.  The store will consist of multiple nodes, each holding a subset of the data. Your solution should focus on core data handling, replication, and conflict resolution.

**Specific Requirements:**

1.  **Data Distribution:** Implement a consistent hashing mechanism (e.g., using a hash ring) to distribute keys across the nodes.  The number of nodes is configurable.

2.  **Replication:** Each key-value pair must be replicated across `N` nodes (replication factor). When a write request is received, the data should be written to the primary node (determined by the consistent hashing) and then propagated asynchronously to the other `N-1` replica nodes.

3.  **Basic Operations:** Implement the following operations:

    *   `put(key, value)`: Stores the key-value pair. The operation should return immediately after writing to the primary node, acknowledging success.  Replication happens in the background.
    *   `get(key)`: Retrieves the value associated with the key. If the key is not found on the first contacted node, query other replica nodes *before* returning `None`.
    *   `delete(key)`: Deletes the key-value pair.  Like `put`, this should return immediately after deleting from the primary node, with replication happening in the background.

4.  **Eventual Consistency & Conflict Resolution:** In the case of concurrent updates to the same key, implement a Last-Write-Wins (LWW) strategy based on timestamps. Each key-value pair should store a timestamp.  When a node receives an update with a timestamp earlier than its stored timestamp for a key, it should reject the update.
    * Each node should have a globally unique ID.
    * The timestamp should be generated per node.

5.  **Node Failures:** Your design should gracefully handle node failures.  If a node is unavailable during replication, the system should retry the replication later.  Data loss should be minimized.
    *   You do not need to implement actual node failure detection (e.g., heartbeats).  Assume a simplified mechanism where you can mark a node as "down" and "up" for testing purposes. When a node is "down", it should not be contacted for any operation until it's marked "up" again.
    *   When a node comes back up, it should reconcile its data with other replica nodes to ensure eventual consistency. It should pull any missed updates from other replicas based on timestamps.

6.  **Optimization:**
    *   Optimize the `get` operation for read performance.  Ideally, you want to return the value as quickly as possible.
    *   Consider the trade-offs between consistency and availability.

7.  **Scalability:** While a fully scalable implementation is beyond the scope of this problem, your design should consider scalability aspects. How would your design adapt to a significantly larger number of nodes and data?

**Constraints:**

*   You can simulate the distributed environment using in-memory data structures (e.g., dictionaries) within a single process.  No actual network communication is required.
*   Focus on the core logic of data distribution, replication, and conflict resolution.  You don't need to implement features like authentication, authorization, or monitoring.
*   Assume all keys and values are strings.
*   Replication should be asynchronous.
*   Error handling (e.g., handling network errors during replication) should be considered, but detailed error reporting is not required.  Focus on ensuring data consistency.
*   The replication factor `N` will always be less than or equal to the total number of nodes.

**Bonus (optional, but highly encouraged):**

*   Implement anti-entropy mechanism. Every node periodically compares its data with replicas to ensure consistency.
*   Implement the node discovery mechanism using something like gossip protocol.
*   Implement background process to clean up the deleted data.

This problem requires a solid understanding of distributed systems concepts, data structures, and algorithms. It will challenge the candidate to make design decisions, implement complex logic, and consider various trade-offs. Good luck!
