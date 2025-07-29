Okay, here's a challenging problem designed to be on the "Hard" end of the difficulty spectrum, focusing on optimization and real-world considerations.

**Problem Title:** Distributed Key-Value Store with Consistent Hashing

**Problem Description:**

You are tasked with designing and implementing a simplified distributed key-value store.  The system consists of a cluster of `N` server nodes, each responsible for storing a subset of the data.  To achieve scalability and fault tolerance, you will implement consistent hashing to distribute keys across the nodes.

Your solution should implement the following functionalities:

1.  **`add_node(node_id)`:** Adds a new server node with the given `node_id` to the cluster.  The `node_id` is a unique string identifier.

2.  **`remove_node(node_id)`:** Removes an existing server node with the given `node_id` from the cluster.

3.  **`put(key, value)`:**  Stores the given `value` associated with the `key`.  The `key` is a string, and the `value` can be any Python object.  The key must be hashed using MD5, and the resulting hash value should be used to determine which node is responsible for storing the key-value pair using consistent hashing.

4.  **`get(key)`:** Retrieves the `value` associated with the given `key`. If the key does not exist in the store, return `None`.  The key must be hashed using MD5, and the resulting hash value should be used to determine which node is responsible for fetching the key-value pair.

5.  **`get_node(key)`:** Returns the `node_id` of the node that is responsible for storing the given `key` according to the consistent hashing algorithm. The key must be hashed using MD5, and the resulting hash value should be used to determine the corresponding node. Return `None` if there are no nodes in the cluster.

**Requirements and Constraints:**

*   **Consistent Hashing:**  Implement consistent hashing using a ring-based approach.  Each node and key is mapped to a point on the ring using an MD5 hash.  When a key is stored or retrieved, it is assigned to the next node on the ring in a clockwise direction.

*   **Virtual Nodes:** To improve the distribution of keys and mitigate hotspots, implement virtual nodes.  Each physical node should be represented by `V` virtual nodes on the ring. `V` should be a configurable parameter with a default value of 100. The `node_id` of the virtual nodes should be `<node_id>-<virtual_node_index>`. For instance, if `node_id` is "server1" and `virtual_node_index` is 5, the virtual node id should be "server1-5".

*   **Data Persistence:** The data stored in each node is volatile, meaning data is lost if the node is removed. You do not need to implement persistence to disk.

*   **Concurrency:**  Assume that multiple clients may access the key-value store concurrently.  Your implementation must be thread-safe. Consider using appropriate locking mechanisms to prevent race conditions.

*   **Optimization:**  The `put` and `get` operations should be optimized for performance.  Consider using efficient data structures and algorithms to minimize latency. Aim for O(log N) or better performance for lookups, where N is the number of virtual nodes.

*   **MD5 Hashing:** Use the `hashlib.md5` function in Python to generate hash values for keys and node IDs. Ensure that the hash values are converted to integers before being used for consistent hashing calculations.

*   **Error Handling:** Implement appropriate error handling.  For example, raise exceptions if a node is added with a non-unique `node_id` or if an attempt is made to remove a non-existent node.

*   **Scalability:**  The system should be designed to handle a large number of keys and nodes.

*   **Data Migration:** When a node is added or removed, the keys that were previously assigned to other nodes might need to be re-assigned to the new node or to other existing nodes. Implement the logic to migrate the keys accordingly. The migration process should be efficient.

**Input:**

The input consists of a series of commands to be executed against the key-value store.

**Output:**

The output consists of the results of the `get` and `get_node` operations.

**Example:**

(Illustrative - not a full test case)

```python
# Add nodes
add_node("server1")
add_node("server2")
add_node("server3")

# Put data
put("key1", "value1")
put("key2", "value2")

# Get data
print(get("key1"))  # Output: value1
print(get("key3"))  # Output: None

# Remove node
remove_node("server2")

# Get data after node removal (key2 may have been re-assigned)
print(get("key2"))  # Output: May be value2, or None if data was lost

print(get_node("key1")) # Output: server1 or server3 (depending on the consistent hashing)
```

This problem challenges the candidate to design a distributed system, understand and implement consistent hashing, handle concurrency, and optimize for performance.  It also requires consideration of real-world issues like data migration and fault tolerance. The candidate should demonstrate a solid understanding of data structures, algorithms, and system design principles. Good luck!
