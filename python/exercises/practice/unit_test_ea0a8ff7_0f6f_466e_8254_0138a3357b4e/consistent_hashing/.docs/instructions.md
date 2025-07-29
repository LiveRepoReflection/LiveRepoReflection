## Project Name

`DistributedConsistentHashing`

## Question Description

You are tasked with designing and implementing a distributed key-value store that utilizes consistent hashing to distribute data across a cluster of nodes. The system must handle node additions and removals gracefully, minimizing data movement and maintaining data availability.

Specifically, you need to implement the core components of the consistent hashing ring and the data redistribution logic.

**Core Requirements:**

1.  **Consistent Hash Ring:** Implement a consistent hash ring data structure. The ring should be able to map keys to nodes based on a hashing function (you can use a simple hash function like `hash(key) % ring_size` for simplicity, but understand MurmurHash or similar is more practical in reality). The ring should support adding and removing nodes.

2.  **Virtual Nodes (Optional, but highly recommended for better distribution):** Implement virtual nodes (also known as vnodes or replicas). Each physical node should be assigned multiple virtual nodes on the ring to improve key distribution and reduce the impact of node failures.

3.  **Data Redistribution on Node Changes:** When a node is added or removed, implement the logic to redistribute keys affected by the change. Only keys that should now belong to a different node should be moved. Minimizing data movement is crucial.

4.  **Key Lookup:** Implement a function to lookup the node responsible for a given key.

5.  **Node State Management:** Assume each node stores its assigned keys in a local key-value store (e.g., a Python dictionary). When a node joins, it should receive keys from other nodes. When a node leaves, its keys should be distributed to other nodes.

**Constraints:**

*   **Scalability:** The system should be designed to handle a large number of nodes and keys. Consider how your design choices affect scalability.
*   **Efficiency:** Data redistribution should be efficient. Avoid moving unnecessary data. Key lookups should also be fast.
*   **Data Consistency (Eventual Consistency):** Perfect consistency is not required for this problem. Focus on minimizing data loss and ensuring that the system eventually converges to a consistent state after node changes.
*   **Error Handling:** Handle potential errors gracefully, such as node failures during data redistribution.
*   **Concurrency:** The system should be thread-safe, as multiple clients might concurrently access the key-value store. Use appropriate locking or other concurrency control mechanisms.

**Specific Input and Output:**

You are not required to implement a full network layer. The input and output will be simulated within the same process.

*   **Input:** A series of operations to perform on the distributed key-value store, including:
    *   `add_node(node_id)`: Adds a new node to the cluster.
    *   `remove_node(node_id)`: Removes a node from the cluster.
    *   `put(key, value)`: Stores a key-value pair in the system.
    *   `get(key)`: Retrieves the value associated with a key.
*   **Output:**
    *   The `get(key)` operation should return the correct value if the key exists, or `None` if the key does not exist.
    *   The system should log the data redistribution process during node additions and removals.
    *   The system should be able to handle race conditions when nodes join/leave concurrently.

**Example Scenario:**

1.  Initially, there are 3 nodes: `node1`, `node2`, and `node3`.
2.  `put("key1", "value1")`, `put("key2", "value2")`, `put("key3", "value3")`.
3.  `get("key1")` should return `"value1"`.
4.  `add_node("node4")`. The system redistributes data.
5.  `get("key1")` should still return `"value1"`.
6.  `remove_node("node2")`. The system redistributes data.
7.  `get("key2")` should still return `"value2"`.
8.  Handle concurrent add/remove node operations.

**Judging Criteria:**

*   Correctness: The system must correctly store and retrieve data, even after node additions and removals.
*   Efficiency: The data redistribution process should be efficient, minimizing data movement.
*   Scalability: The design should be scalable to handle a large number of nodes and keys.
*   Concurrency: The system should be thread-safe and handle concurrent operations correctly.
*   Code Quality: The code should be well-structured, readable, and maintainable.

This problem requires a good understanding of distributed systems concepts, data structures, and algorithms. It is designed to be challenging and requires careful consideration of various design trade-offs. Good luck!
