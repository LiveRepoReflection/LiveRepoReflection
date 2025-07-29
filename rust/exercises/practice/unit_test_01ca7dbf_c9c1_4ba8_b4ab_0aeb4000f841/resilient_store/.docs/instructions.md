Okay, here's a challenging Rust coding problem.

**Problem Title:**  Resilient Distributed Key-Value Store

**Problem Description:**

You are tasked with implementing a simplified, but resilient, distributed key-value store. The store consists of `N` nodes (where `N` is a configurable parameter, assumed to be odd for simplicity).  Each key-value pair is replicated across `K` nodes (where `K` is also configurable, and `K <= N`, preferably `K = (N+1)/2` for majority). This replication strategy aims to ensure data durability and availability even if some nodes fail.

Your system must support the following operations:

1.  **`put(key: String, value: String, timestamp: u64)`:** Stores a key-value pair. The `timestamp` represents the version of the data.  The system must ensure that the latest version (highest timestamp) is always stored. If a key already exists, and the provided timestamp is older than the existing timestamp for that key, the `put` operation should be ignored.  The `put` operation needs to write the data to *at least* `(K+1)/2` nodes to be considered successful (majority write).

2.  **`get(key: String)`:** Retrieves the value associated with a key.  If the key exists on multiple nodes (due to replication), the system must retrieve the value with the highest timestamp. If the key does not exist on any node, return `None`.

3.  **`delete(key: String, timestamp: u64)`:** Deletes a key-value pair. Similar to `put`, the `delete` operation must record the deletion event with a timestamp.  A deletion is effectively a "tombstone" entry with a `None` value and a timestamp. If a `get` operation encounters a tombstone with a timestamp higher than any existing value for the key, it should return `None`.  The `delete` operation needs to write the data to *at least* `(K+1)/2` nodes to be considered successful (majority write).

**Constraints and Requirements:**

*   **Concurrency:** The system must handle concurrent `put`, `get`, and `delete` operations correctly.
*   **Fault Tolerance:** The system should be resilient to node failures.  If some nodes are unavailable, the system should still function as long as a majority of nodes are operational.
*   **Data Consistency:** The system must strive for strong eventual consistency.  This means that after a period of inactivity, all nodes should eventually converge to the same state (the latest version of each key-value pair).
*   **Optimization:** Optimize for read performance. `get` operations should be as fast as possible, even if it means sacrificing some write performance.
*   **Node Communication:** You'll need to simulate node-to-node communication.  You can use channels, shared memory, or any other suitable mechanism to represent the network.
*   **Data Persistence (Optional, but highly recommended for real-world scenarios):** Data needs to persist between restarts of the service. Use some form of database or file-based storage.
*   **Timestamp Generation:** Design a mechanism for generating unique and monotonically increasing timestamps. Consider the challenges of generating timestamps across multiple distributed nodes. You can assume a loosely synchronized clock (e.g., using NTP).

**Edge Cases and Considerations:**

*   **Node Recovery:** Consider what happens when a failed node recovers. How does it catch up with the latest state?
*   **Network Partitions:** Think about the impact of network partitions. How does the system behave if the nodes are split into two or more isolated groups?
*   **Timestamp Collisions:** While unlikely, consider the possibility of timestamp collisions. How can you ensure that the system remains consistent even if two operations happen to have the same timestamp?
*   **Tombstone Management:** Implement a mechanism for periodically cleaning up old tombstones to prevent the system from accumulating excessive deletion markers.

**Input:**

The system should accept `put`, `get`, and `delete` requests as described above. The number of nodes, replication factor, and other configuration parameters should be configurable at startup.

**Output:**

*   `put` and `delete` operations should return a boolean indicating success or failure (e.g., whether a majority of nodes acknowledged the write).
*   `get` operations should return `Option<String>` representing the value associated with the key, or `None` if the key does not exist or has been deleted.

This problem challenges you to design and implement a robust, distributed system that addresses common challenges in distributed data management. Good luck!
