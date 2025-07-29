Okay, I'm ready to set a challenging Rust coding problem. Here it is:

### Project Name
`ConsistentHashing`

### Question Description

Implement a distributed key-value store using consistent hashing. Your store consists of *N* nodes, each identified by a unique string identifier. Keys are also strings.  The hash space is the range of `u32` values.

Your task is to implement the following functionalities:

1.  **`add_node(node_id: String)`:** Adds a new node to the hash ring.
2.  **`remove_node(node_id: String)`:** Removes a node from the hash ring.
3.  **`get_node(key: String)`:**  Given a key, return the `node_id` responsible for storing that key. The node responsible for a key is determined by consistent hashing:

    *   Hash the key to a `u32` value.
    *   Find the first node in the ring whose hash value is *greater than or equal to* the key's hash value.
    *   If no such node exists (i.e., the key's hash is larger than the hash of all nodes), the key is assigned to the node with the *smallest* hash value (wraparound).

4.  **`rebalance()`:**  Simulate the rebalancing process after adding or removing a node. This function doesn't actually move the data, but it is important to test the correctness of `get_node` after changing the ring. You are not required to implement any data migration strategy.

**Constraints and Requirements:**

*   **Performance:** The `get_node` operation must be efficient.  Aim for logarithmic time complexity (or better) with respect to the number of nodes.  Linear time is not acceptable for large numbers of nodes.
*   **Uniformity:** The hashing algorithm must provide a reasonably uniform distribution of keys across the nodes.  A poor hashing algorithm will result in hotspots and unbalanced load. You can use any well-known hashing algorithm.
*   **Virtual Nodes:**  To improve the distribution of keys and handle node heterogeneity, implement the concept of *virtual nodes* (also known as vnodes or replicas).  Each physical node should be represented by *K* virtual nodes in the hash ring, where *K* is a configurable parameter.  When `add_node` is called, generate *K* virtual node IDs for that node and add them to the ring.  The virtual node IDs should be derived deterministically from the physical node ID (e.g., by appending a sequence number).  When `get_node` is called, it should return the *physical* node ID corresponding to the virtual node it finds in the ring.
*   **Concurrency:**  The `add_node`, `remove_node`, and `get_node` functions must be thread-safe.  Multiple threads may concurrently access the hash ring.  Use appropriate synchronization primitives (e.g., `Mutex`, `RwLock`) to protect shared data.
*   **Node IDs:** Node IDs are unique. Adding a node with an existing ID should return an error.
*   **Error Handling:** Handle errors gracefully.  For example, `remove_node` should not panic if the node doesn't exist, but instead should return an appropriate error (or do nothing and return successfully).
*   **K Value:** The number of virtual nodes *K* is configurable when the `ConsistentHashing` struct is created.
*   **Deterministic Hashing:** Hashing must be deterministic. Given the same key, the hash function should always return the same hash value.

**Example Usage Scenario:**

Imagine a distributed cache system where keys are cached across multiple servers. This `ConsistentHashing` implementation allows you to determine which server should store or retrieve a particular key.  Adding or removing servers should only require minimal data movement (ideally, only the keys on the departing server need to be re-assigned).

**Hints:**

*   Consider using a sorted data structure (e.g., `BTreeMap` or a sorted `Vec`) to efficiently find the next node in the ring.
*   Use a well-established hashing algorithm like `xxHash` or `MurmurHash`.
*   Pay close attention to edge cases, such as an empty ring or when the key's hash is larger than all node hashes.
*   Think carefully about the trade-offs between different synchronization primitives.  `RwLock` may offer better performance for read-heavy workloads.
*   Focus on code clarity, correctness, and performance.

This problem requires a solid understanding of data structures, algorithms, concurrency, and distributed systems concepts.  It encourages you to think about real-world scenarios and make informed design choices. Good luck!
