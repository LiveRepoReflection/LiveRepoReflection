## Project Name

`DistributedConsistentHashing`

## Question Description

You are tasked with designing and implementing a distributed key-value store using consistent hashing. The system consists of `N` nodes, each identified by a unique integer ID from `0` to `N-1`.  The key-value store must support two primary operations: `put(key, value)` and `get(key)`.

**Consistent Hashing:**

Implement consistent hashing to distribute keys across the `N` nodes. Use the following specifications:

1.  **Hashing:** Use a simple hashing function `hash(key)` that returns an integer.  While a 'real' hash would be complex, for the purposes of this exercise, you may use `key.hashCode()` to generate the hash. Then map this hash to a ring represented by the integers `0` to `2^32 - 1` (inclusive).

2.  **Node Assignment:** Each node in the system is also assigned a random position on the same ring. To determine the node responsible for a given key, hash the key and then find the *next* node on the ring (clockwise). This is often called the "successor" node.

3.  **Adding/Removing Nodes:**  Your system must handle the addition and removal of nodes dynamically. When a node is added, it takes over the keys from its successor node that now belong to it according to the consistent hashing scheme.  When a node is removed, its keys are transferred to its successor.  Minimize the number of keys that need to be remapped when nodes join or leave the cluster.

**Requirements:**

1.  **Implement the following methods:**

    *   `DistributedConsistentHashing(int numNodes)`: Constructor. Initializes the distributed hash table with `numNodes` nodes. Initially assign nodes with randomly picked hash values on the ring.
    *   `put(String key, String value)`: Stores the `value` associated with the `key` in the appropriate node.
    *   `get(String key)`: Retrieves the `value` associated with the `key` from the appropriate node.  Returns `null` if the key does not exist.
    *   `addNode()`: Adds a new node to the system. The new node should be assigned a random position on the ring, and existing keys should be re-distributed accordingly. Return the new node id.
    *   `removeNode(int nodeId)`: Removes the node with the given `nodeId` from the system. All keys previously stored on this node must be transferred to its successor.
    *   `rebalance()`: Rebalances the entire system. This can be used after a series of add/remove operations to more optimally distribute the keys. This method should be efficient and strive to minimize key movements.

2.  **Data Storage:**  Each node in the system has its own local storage (e.g., a `HashMap`) to store the key-value pairs that it is responsible for.

3.  **Scalability and Performance:**  Your solution should be designed to handle a large number of keys and nodes efficiently. Consider the time complexity of each operation, especially `put`, `get`, `addNode`, `removeNode`, and `rebalance`.

4.  **Concurrency:** Your solution needs to be thread-safe. Multiple clients may access the distributed key-value store concurrently. Use appropriate synchronization mechanisms (e.g., locks) to prevent data corruption and ensure consistency.

**Constraints:**

*   `1 <= N <= 1000` (initial number of nodes)
*   The key space is the set of all possible strings.
*   The value space is the set of all possible strings.
*   You are allowed to use standard Java libraries, but you cannot use any existing distributed caching or key-value store implementations (e.g., Redis, Memcached).
*   Minimize the amount of data transferred between nodes during `addNode`, `removeNode`, and `rebalance` operations.

**Optimization Considerations:**

*   **Virtual Nodes:** Consider using virtual nodes (replicas) to improve the distribution of keys and fault tolerance. (Not explicitly required but will be looked upon favorably)
*   **Load Balancing:**  Strive to achieve a relatively even distribution of keys across the nodes.
*   **Key Migration:** Optimize the key migration process during node additions and removals to minimize disruption to the system.

This problem requires a good understanding of consistent hashing, data structures, algorithms, and concurrency.  A well-designed solution will be both efficient and scalable. Good luck!
