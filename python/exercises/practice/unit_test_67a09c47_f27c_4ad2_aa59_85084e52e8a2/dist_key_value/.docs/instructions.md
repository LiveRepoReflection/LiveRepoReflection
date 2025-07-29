## Question: Distributed Key-Value Store with Eventual Consistency

### Question Description

Design a distributed key-value store that simulates a simplified version of systems like Cassandra or DynamoDB. Your implementation should handle the core operations of `put`, `get`, and `delete`, while also addressing the challenges of eventual consistency in a distributed environment.

**System Architecture:**

Imagine a cluster of `n` nodes (where `n` can vary). Each key is assigned a "home node" based on a consistent hashing scheme (you can use a simple modulo operation for key assignment). However, for fault tolerance and availability, each key is replicated across `r` nodes (replication factor), including the home node. You need to implement the logic to determine which nodes should store a particular key based on the hashing and replication.

**Data Model:**

Each value associated with a key should have a version number (e.g., a Lamport timestamp or a vector clock - you can simplify and just use a single integer timestamp). This version number represents the order in which the value was updated. When conflicts arise (multiple nodes have different versions of the same key), the system should resolve them using a "last write wins" strategy based on these version numbers.

**API Requirements:**

Implement the following methods:

*   `put(key, value)`: Stores the `value` associated with the `key` on `r` replica nodes.  The `put` operation must generate a new version number (timestamp) for the value and store it along with the value on each replica. You must handle the distribution of the data to the right nodes.

*   `get(key)`: Retrieves the value associated with the `key`. This operation should contact all `r` replica nodes, collect the values and their version numbers, and return the value with the highest version number. If all replicas are unavailable or return errors, return `None`.

*   `delete(key)`: Deletes the key-value pair from all `r` replica nodes. This should also generate a new version number (timestamp) for the deletion marker. Deletion markers are special values that indicate a key has been deleted. When a get operation encounters a deletion marker with a higher version than all other values, it should return `None`.

**Constraints and Considerations:**

1.  **Eventual Consistency:** Your system doesn't need to guarantee strong consistency. Implement eventual consistency, meaning that if no new updates are made to a given data item, eventually all accesses to that item will return the last updated value.

2.  **Fault Tolerance:** Simulate node failures.  Implement a mechanism to handle nodes being temporarily unavailable. If a node is unavailable during a `put` or `get` operation, the system should continue to function, contacting the remaining replicas.

3.  **Conflict Resolution:** Implement last-write-wins based on version numbers (timestamps). When `get` retrieves multiple versions of the same key, the highest version number wins.  If there is a tie, you can choose a deterministic tie-breaker (e.g., pick the value from the node with the lowest ID).

4.  **Data Distribution:** Use consistent hashing (e.g., `hash(key) % n`) to determine the "home node" for a key. Replicate the key-value pair to the `r` nodes following the home node in a circular fashion around the cluster.

5.  **Optimization (Optional):** Consider implementing a "hinted handoff" mechanism. If a node is unavailable during a `put` operation, the `put` operation can temporarily store the data on another available node (a "hint"). When the original node comes back online, the hinted data is transferred. This can improve data durability in the face of temporary node failures.

6.  **Scalability:** While you don't need to simulate a massive cluster, consider how your design would scale to a larger number of nodes.

7.  **Concurrency:**  Your implementation must be thread-safe. Multiple clients should be able to perform `put`, `get`, and `delete` operations concurrently without corrupting data. You might need to use locks or other synchronization mechanisms.

**Input/Output:**

Your code will be tested with a series of `put`, `get`, and `delete` operations, potentially interleaved with simulated node failures. The `get` operation should return the correct value (or `None` if the key is not present or has been deleted) after considering eventual consistency and conflict resolution.

**Example:**

Let's say you have 3 nodes (n=3) and a replication factor of 2 (r=2). The key "user1" has a hash value of 1 (1 % 3 = 1), so its home node is node 1. The replicas will be stored on nodes 1 and 2 (following the circular fashion).

**This is a design and implementation challenge. You are expected to implement the logic for a distributed key-value store, not just call existing library functions.**
