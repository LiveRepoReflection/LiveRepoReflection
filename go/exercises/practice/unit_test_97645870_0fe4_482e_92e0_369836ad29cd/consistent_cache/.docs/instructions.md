Okay, here's a Go programming problem designed to be challenging, requiring a good understanding of data structures, algorithms, and system design considerations:

**Project Name:** `DistributedConsistentCache`

**Question Description:**

You are tasked with designing and implementing a distributed, eventually consistent cache system. This cache will be used by a high-volume, read-heavy application. The cache must be able to handle a large number of concurrent requests and scale horizontally.

**Requirements:**

1.  **Basic Cache Operations:** Implement the following basic cache operations:
    *   `Get(key string) (string, bool)`: Retrieves a value from the cache, returning the value and a boolean indicating whether the key was found.
    *   `Set(key string, value string)`: Sets a key-value pair in the cache.
    *   `Delete(key string)`: Deletes a key-value pair from the cache.

2.  **Distributed Architecture:** The cache should be distributed across multiple nodes. Implement a simple hash-based sharding scheme to distribute keys across the nodes. Assume the number of nodes is fixed and known at initialization.  Implement a `Node` struct with the core cache logic and a `CacheCluster` struct which manages the nodes.

3.  **Eventual Consistency:**  Data consistency across the nodes is not required to be immediate. Implement a mechanism to propagate updates (Set, Delete) to other nodes asynchronously.  You can use a simple gossip protocol or a message queue (e.g., using channels in Go) to achieve this.  Updates should be idempotent.

4.  **Conflict Resolution:** When concurrent updates to the same key occur on different nodes, you need to handle potential conflicts. Implement a Last-Write-Wins (LWW) conflict resolution strategy using timestamps. Each cached value should store a timestamp of when it was last updated.

5.  **Scalability and Concurrency:**  The cache should be able to handle a high volume of concurrent requests. Use appropriate synchronization primitives (e.g., `sync.Mutex`, `sync.RWMutex`, `sync.WaitGroup`) to ensure thread safety.

6.  **Fault Tolerance (Limited):** If a node becomes unavailable, the system should continue to function, although performance may be degraded.  No data replication is required, so data stored on a failed node will be lost.

7.  **Optimization:** Aim for efficient Get operations.  Consider using appropriate data structures for the cache (e.g., a concurrent hash map) to minimize lock contention.

**Constraints:**

*   The number of cache nodes is fixed during runtime.
*   The cache size per node is limited (e.g., 10,000 entries). Implement an eviction policy (e.g., Least Recently Used - LRU) to handle cache overflows.
*   The key and value sizes are relatively small (e.g., less than 1KB).
*   Network latency between nodes is assumed to be non-negligible.
*   You don't need to implement persistence to disk.
*   Assume no external dependencies or third-party libraries are allowed, except for standard Go packages.
*   The system should be able to tolerate nodes going down, but no data replication is required.

**Evaluation Criteria:**

*   Correctness: The cache should function as expected, providing correct Get, Set, and Delete operations.
*   Concurrency: The cache should be able to handle a large number of concurrent requests without data corruption or deadlocks.
*   Scalability: The cache should scale horizontally with the addition of more nodes.
*   Eventual Consistency: Updates should eventually propagate to all nodes.
*   Fault Tolerance: The system should continue to operate, albeit potentially with reduced performance, when one or more nodes become unavailable.
*   Code Quality: The code should be well-structured, readable, and maintainable.  Follow Go best practices.
*   Efficiency: Optimize for fast Get operations.

This problem requires a good understanding of distributed systems concepts, concurrency, and data structures. Good luck!
