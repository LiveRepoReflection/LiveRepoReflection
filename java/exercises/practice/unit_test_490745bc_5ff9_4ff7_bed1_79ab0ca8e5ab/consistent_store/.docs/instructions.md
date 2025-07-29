## Question: Highly Available Key-Value Store with Consistent Hashing

**Question Description:**

You are tasked with designing and implementing a distributed, highly available key-value store. The system must handle a large number of read and write requests per second while maintaining data consistency and fault tolerance.

The key-value store will be distributed across multiple servers (nodes). To distribute data evenly across nodes and minimize data movement during node additions or removals, you will use Consistent Hashing.

Your system should support the following operations:

*   `put(key, value)`: Stores a value associated with a given key.
*   `get(key)`: Retrieves the value associated with a given key. Returns `null` if the key does not exist.
*   `delete(key)`: Deletes the key and its associated value.

**Constraints and Requirements:**

1.  **Consistent Hashing:** Implement Consistent Hashing to distribute keys across nodes. Use a ring-based approach.

2.  **Replication:** Implement data replication for fault tolerance. Each key-value pair should be replicated across `N` nodes (replication factor).  When a node fails, the system should automatically recover the data from the replica nodes.

3.  **Data Consistency:**  Maintain strong consistency for `get` and `put` operations. You MUST implement the Raft consensus algorithm. A client should always read the most recent value of a key, even after node failures or network partitions.

4.  **High Availability:** The system should remain available even when a subset of nodes fails. The number of node failures it can tolerate depends on the replication factor `N`.

5.  **Scalability:** The system should be designed to scale horizontally by adding more nodes to the cluster.

6.  **Node Discovery:** Implement a simple mechanism for nodes to discover each other and join the cluster.  Assume there is a central configuration server (e.g., ZooKeeper) that stores the initial list of nodes in the cluster.  Nodes should be able to join and leave the cluster dynamically, and the system should adapt accordingly.

7.  **Performance:** Optimize for low latency reads and writes. Consider caching mechanisms, efficient data structures, and concurrency control.

8.  **Error Handling:** Implement robust error handling to gracefully handle node failures, network issues, and invalid requests.

9. **Time Complexity:** `get`, `put`, and `delete` operations must have an average time complexity of O(log N), where N is the number of nodes in the cluster.

**Input:**

The system will receive `put`, `get`, and `delete` requests.

**Output:**

*   `get(key)`: Returns the value associated with the key, or `null` if the key does not exist.
*   `put(key, value)`: Returns `true` if the operation was successful, `false` otherwise.
*   `delete(key)`: Returns `true` if the operation was successful, `false` otherwise.

**Evaluation Criteria:**

*   **Correctness:** The system must correctly implement the specified operations and maintain data consistency.
*   **Fault Tolerance:** The system must remain available and data consistent even when nodes fail.
*   **Scalability:** The system should scale horizontally as the number of nodes increases.
*   **Performance:** The system should provide low latency reads and writes.
*   **Code Quality:** The code should be well-structured, readable, and maintainable.

This problem requires a solid understanding of distributed systems concepts, data structures, algorithms, and concurrency. Good luck!
