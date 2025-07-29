Okay, here is a challenging Rust coding problem designed to test various skills, including data structures, algorithms, optimization, and edge case handling.

## Problem Title: Highly Available Key-Value Store with Conflict Resolution

### Problem Description

You are tasked with designing and implementing a simplified, distributed key-value store using Rust. This key-value store needs to be highly available, meaning it should remain operational even when some of its nodes fail.  To achieve this, the system will employ data replication. However, replication introduces the possibility of conflicting updates. Therefore, you also need to implement a robust conflict resolution mechanism.

**Core Requirements:**

1.  **Data Storage:** Implement a basic key-value store. Keys and values are both UTF-8 strings. The store should support the following operations:
    *   `insert(key: String, value: String)`: Inserts or updates a key-value pair.
    *   `get(key: String) -> Option<String>`: Retrieves the value associated with a key. Returns `None` if the key does not exist.
    *   `delete(key: String)`: Deletes a key-value pair.

2.  **Distributed Nodes:** Simulate a distributed environment with multiple nodes. Each node has its own instance of the key-value store.  Assume a fixed number of nodes `N` (where `N >= 3`).

3.  **Data Replication:** When a client interacts with the system (through any node), the system should replicate the operation to a majority of the nodes (at least `(N/2) + 1` nodes). Use a simple, synchronous replication strategy for this problem. If replication to a majority fails, the operation should be considered failed and an error should be returned.

4.  **Conflict Resolution:** Due to the asynchronous nature of distributed systems, conflicts can arise when the same key is updated concurrently on different nodes. Implement the following conflict resolution strategy using **Lamport Clocks**:
    *   Each node maintains a Lamport clock (a simple integer counter).
    *   Each key-value pair is associated with a timestamp (the Lamport clock value when the value was inserted/updated).
    *   When a conflict is detected (multiple values for the same key across nodes), the system should resolve the conflict by choosing the value with the **highest timestamp**.  If the timestamps are equal, choose the value that is lexicographically smaller.
    *   Ensure that Lamport Clocks are properly updated whenever operations are performed.

5.  **Node Failure Handling:** Simulate node failures. Your system should be resilient to the failure of up to `(N-1)/2` nodes. When a node fails, it should be considered unavailable. Operations should still succeed as long as a majority of the nodes are available. When a failed node recovers, it should synchronize its data with the rest of the cluster. You can assume nodes recover with no data (empty key-value store).

6.  **Performance Optimization:**  Aim for efficient read and write operations. Consider using appropriate data structures to minimize latency. Avoid unnecessary locking or blocking operations.

**Constraints:**

*   The number of nodes, `N`, will be a small constant value (e.g., 3, 5, or 7).
*   The total number of keys and values stored will be within reasonable memory limits for a single machine (e.g., hundreds of thousands).
*   Assume a simplified network model: reliable message delivery (no message loss or corruption) but with variable latency.  You don't need to implement actual network communication, you can simulate it using appropriate data structures and synchronization primitives.
*   Simulate node failures using a mechanism that allows you to mark a node as unavailable.
*   Implement all operations (insert, get, delete) and conflict resolution atomically (i.e., no race conditions).
*   Implement the data synchronization process for recovering nodes efficiently.

**Error Handling:**

*   Return appropriate error types for the following scenarios:
    *   Replication failure (cannot reach a majority of nodes).
    *   Attempting to access a failed node directly (clients should only interact through available nodes).

**Example Scenario:**

1.  Nodes A, B, and C form a cluster (N=3).
2.  Client inserts `key1 = "value1"` through node A. This is replicated to B and C.
3.  Client inserts `key1 = "value2"` through node B *concurrently*. This is replicated to A and C.
4.  Nodes A, B, and C now have different values for `key1` with different timestamps.
5.  A `get(key1)` operation through any node should return the value with the highest timestamp, resolving the conflict.
6.  Node C fails.
7.  Client inserts `key2 = "value3"` through node A. This must be replicated to B to succeed.
8.  Node C recovers, it should synchronize its store with the rest of the cluster.

**Judging Criteria:**

*   **Correctness:** The solution must correctly implement all the required features, including data storage, replication, conflict resolution, and node failure handling.
*   **Concurrency Safety:** The solution must be free of race conditions and data corruption issues.
*   **Performance:** The solution should be reasonably efficient in terms of read and write latency.
*   **Code Quality:** The code should be well-structured, readable, and maintainable.
*   **Error Handling:** The solution must handle errors gracefully and provide informative error messages.

This problem requires a solid understanding of distributed systems concepts, concurrency, and data structures. Good luck!
