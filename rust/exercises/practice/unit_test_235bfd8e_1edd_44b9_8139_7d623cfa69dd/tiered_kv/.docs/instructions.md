## Problem: Distributed Key-Value Store with Tiered Storage

**Description:**

You are tasked with designing and implementing a simplified, distributed key-value store in Rust. This key-value store must support basic `PUT` and `GET` operations, but with a crucial twist: it utilizes a tiered storage system to optimize for both cost and performance.

**System Architecture:**

The key-value store consists of a cluster of `n` nodes (where `n` can be assumed to be a positive integer). Each node is capable of storing data on two tiers:

*   **Tier 1 (Cache):** A fast, but limited-capacity in-memory cache (e.g., using `HashMap`). This tier provides low-latency access.

*   **Tier 2 (Disk):** A slower, but high-capacity disk-based storage (e.g., using a persistent data structure like `sled` or simply writing to files). This tier provides persistent storage.

**Data Consistency:**

For the sake of simplicity, you can assume eventual consistency. It is acceptable for reads to occasionally return stale data.

**Requirements:**

1.  **Node Implementation:**
    *   Implement a `Node` struct/class that represents a single node in the cluster.
    *   The `Node` should have methods for:
        *   `put(key: String, value: String)`: Stores the key-value pair.  The `PUT` operation should write to both Tier 1 and Tier 2 (write-through cache).
        *   `get(key: String) -> Option<String>`: Retrieves the value associated with the key. It should first check Tier 1 (cache). If the key is found, return the value immediately. If not found in Tier 1, check Tier 2 (disk). If found in Tier 2, promote the key-value pair to Tier 1 (cache) and then return the value. If the key is not found in either tier, return `None`.
        *   Implement a cache eviction policy (e.g., Least Recently Used - LRU). This is important as Tier 1 has limited capacity.

2.  **Cluster Management:**
    *   Implement a `Cluster` struct/class that manages the nodes.
    *   The `Cluster` should have methods for:
        *   `new(num_nodes: usize, cache_size_per_node: usize)`: Initializes the cluster with `num_nodes` nodes, each having a Tier 1 cache of size `cache_size_per_node`.
        *   `put(key: String, value: String)`:  Distributes the `PUT` operation to one of the nodes in the cluster. The key should be hashed to select the node.
        *   `get(key: String) -> Option<String>`:  Distributes the `GET` operation to the same node that would be selected by the `PUT` operation for the given key.

3.  **Constraints:**
    *   **Cache Capacity:** Tier 1 (cache) has a limited capacity per node. You need to implement a suitable cache eviction policy to handle cache overflow.
    *   **Data Durability:** Tier 2 (disk) should provide persistent storage. Data written to Tier 2 should survive node restarts.
    *   **Scalability:** While you don't need to implement full-blown distributed consensus, your design should be mindful of potential scalability issues. Consider how your solution might behave with a large number of nodes.
    *   **Thread Safety:** The system needs to handle concurrent `PUT` and `GET` requests safely. Use appropriate synchronization primitives (e.g., `Mutex`, `RwLock`) where necessary.
    *   **Performance:** The `GET` operation should be optimized for speed, especially for frequently accessed keys that reside in Tier 1.

4.  **Error Handling:**
    *   Implement basic error handling. Consider what errors might occur (e.g., disk I/O errors) and how they should be handled.

**Optimization Requirements:**

*   The `GET` operation should be as fast as possible when the key is present in Tier 1.
*   Minimize the amount of data transferred between Tier 1 and Tier 2.
*   Choose appropriate data structures and algorithms to optimize for both space and time complexity.

**Real-World Considerations (Implicit):**

*   This problem simulates a simplified version of real-world distributed caching systems like Redis or Memcached, but with the added complexity of tiered storage.
*   The tiered storage approach is common in cloud storage systems to balance cost and performance.

**Grading Criteria:**

*   Correctness: Does the code correctly implement the `PUT` and `GET` operations according to the requirements?
*   Performance: Is the code optimized for speed, especially for `GET` operations on cached data?
*   Scalability: Is the design mindful of potential scalability issues?
*   Code Quality: Is the code well-structured, readable, and maintainable? Is error handling implemented appropriately?
*   Thread Safety: Is the code thread-safe and able to handle concurrent requests without data corruption or race conditions?

This problem requires a good understanding of data structures, algorithms, concurrency, and system design principles. It is a challenging problem that should test the skills of experienced Rust programmers.
