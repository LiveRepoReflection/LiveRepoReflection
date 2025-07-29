## Project Name

`DistributedCache`

## Question Description

You are tasked with designing and implementing a distributed, eventually consistent, in-memory key-value cache. This cache will be used to store frequently accessed data in a system with high read and write throughput.

**Requirements:**

1.  **Basic Functionality:** Implement the core `put(key, value)` and `get(key)` operations.  `put` should store a key-value pair. `get` should retrieve the value associated with a given key. If the key is not present, `get` should return `None`.

2.  **Distribution:** The cache must be distributed across multiple nodes.  You don't need to implement actual network communication.  Instead, assume a function `get_node_for_key(key) -> NodeId` is provided, which deterministically maps a key to a specific node (represented by a `NodeId`, which can be a simple integer). You should simulate node distribution within your code.

3.  **Eventual Consistency:**  The cache should be eventually consistent.  This means that writes may not be immediately visible to all nodes. Implement a simple asynchronous replication mechanism. After a `put` operation on a node, the node should asynchronously propagate the update to `K` other randomly selected nodes. `K` is a configurable parameter.  You don't need to guarantee exactly `K` nodes receive the update, but the intent should be to replicate to approximately `K` nodes.

4.  **Conflict Resolution (Last Write Wins):** In case of conflicting updates to the same key on different nodes, implement a "Last Write Wins" strategy based on timestamps. Each key-value pair should be associated with a timestamp representing the time of the last update.

5.  **Node Failure Handling:** Simulate node failures. Implement a mechanism where, if a node is unavailable during replication, the replication attempt is simply skipped.  No retries are required.

6.  **Cache Eviction (LRU):** Each node in the cache has limited memory. Implement a Least Recently Used (LRU) eviction policy on each node. When a node reaches its capacity, the least recently accessed key-value pair should be evicted to make space for the new entry.

7.  **Concurrency:**  The cache must be thread-safe. Multiple clients may access the cache concurrently. Ensure that all operations are properly synchronized to prevent data races and ensure data integrity.

**Constraints:**

*   The cache nodes are identified by unique integer `NodeId`s.
*   The `get_node_for_key(key)` function is provided.  You do not need to implement this function. It will be used to determine which node should initially handle a `put` or `get` request for a given key.
*   The number of nodes in the distributed cache, `N`, is a configurable parameter.
*   The replication factor, `K`, is a configurable parameter and should be less than `N`.
*   Each node has a maximum capacity, `C`, which is the maximum number of key-value pairs it can store.
*   Timestamps are represented as integers.  You can use `SystemTime::now().duration_since(UNIX_EPOCH).unwrap().as_millis()` for generating timestamps.
*   Key and Value types can be strings.
*   Assume all operations are in the same data center, so network latency is relatively low.
*   Focus on correctness, thread safety, and efficient LRU eviction. Optimize for read performance.

**Bonus (Optional):**

*   Implement a simple monitoring endpoint that allows you to query the state of the cache (e.g., number of keys in each node, hit rate, etc.).

This problem requires you to design and implement a complex distributed system component. Consider the data structures you use, the synchronization mechanisms you employ, and the overall architecture of your solution. Good luck!
