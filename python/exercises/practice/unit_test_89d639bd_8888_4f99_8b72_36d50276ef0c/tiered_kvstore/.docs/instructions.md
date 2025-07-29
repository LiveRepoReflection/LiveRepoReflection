## The Distributed Key-Value Store with Tiered Storage

**Problem Description:**

You are tasked with designing a simplified version of a distributed key-value store (KV store) with tiered storage. The KV store consists of a cluster of *N* nodes (numbered from 0 to N-1). Each node has limited memory. To handle large datasets, the KV store employs a two-tiered storage system:

*   **In-Memory Tier:** Each node has a limited in-memory cache with a fixed capacity *C* (in number of key-value pairs). This tier provides fast read and write access. You can assume that each key-value pair occupies 1 unit of space.

*   **Disk-Based Tier:** Each node also has a disk-based storage tier with virtually unlimited capacity. Access to this tier is significantly slower than the in-memory tier.

The system should support the following operations:

1.  **`put(key, value)`:** Stores the given key-value pair in the system.
    *   If the key already exists in the in-memory tier of any node, update the value in that node.
    *   If the key does not exist in the in-memory tier, the system must select a node to store the key-value pair in its in-memory tier. Use a consistent hashing strategy to map the key to a node.
    *   If the in-memory tier of the selected node is full, evict a key-value pair from the in-memory tier according to the Least Recently Used (LRU) policy *on the node itself*. The evicted key-value pair is considered lost (not persisted to disk).
    *   After attempting to insert into the in-memory tier, also write the key-value pair to the disk-based tier of the selected node to ensure durability.

2.  **`get(key)`:** Retrieves the value associated with the given key.
    *   First, check the in-memory tier of the node mapped to the key by consistent hashing. If the key is found, return the value *and update the LRU information* for the key within that node.
    *   If the key is not found in the in-memory tier, retrieve the value from the disk-based tier of the same node. If the key is found on disk, return the value.
    *   If the key is not found in either the in-memory or disk-based tier, return `None`.

3.  **`delete(key)`:** Deletes the key-value pair from both the in-memory and disk-based tiers of the node mapped to the key.

**Consistent Hashing:**

Use the following consistent hashing function: `node_id = hash(key) % N`, where `hash(key)` is a Python built-in `hash()` function. The node ID determines which node is responsible for storing and retrieving the key-value pair.

**Constraints:**

*   *N* (number of nodes): 1 <= *N* <= 100
*   *C* (in-memory cache capacity per node): 1 <= *C* <= 1000
*   Keys and values are strings.
*   The `put`, `get`, and `delete` operations should be as efficient as possible, considering the trade-offs between memory access and disk access.
*   For the `get` operation, ensure that you update the LRU information if the key is found in the in-memory tier.
*   Assume that there is sufficient disk space available to store all key-value pairs.
*   The system should be thread-safe.

**Optimization Requirements:**

*   Minimize disk reads.
*   Minimize memory usage.

**Evaluation:**

Your solution will be evaluated based on correctness, efficiency, and code quality. Performance will be measured by the total time taken to execute a sequence of `put`, `get`, and `delete` operations. Bonus points will be awarded for solutions that minimize disk reads and memory usage.
