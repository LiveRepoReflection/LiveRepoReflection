## Problem: Distributed Key-Value Store with Range Queries

**Description:**

You are tasked with designing and implementing a distributed key-value store using Rust. This system should not only support basic `put` and `get` operations for individual keys, but also enable efficient range queries, retrieving all key-value pairs within a specified key range.

**System Architecture:**

The system consists of a cluster of `N` nodes (where `N` can be a parameter). Data is partitioned across these nodes. You should implement a consistent hashing scheme (e.g., using a ring-based hash) to distribute keys among the nodes.  Each node is responsible for storing a contiguous range of the key space.

**Requirements:**

1.  **Basic Key-Value Operations:**
    *   `put(key: String, value: String)`: Stores the given key-value pair in the appropriate node based on the consistent hashing scheme.
    *   `get(key: String)`: Retrieves the value associated with the given key. Returns `None` if the key does not exist.

2.  **Range Queries:**
    *   `range_query(start_key: String, end_key: String)`: Retrieves all key-value pairs where the key falls within the inclusive range `[start_key, end_key]`. The result should be returned as a sorted list of `(key, value)` tuples, sorted by key in ascending order.

3.  **Data Consistency:**
    *   Implement basic data replication for fault tolerance. Each key-value pair should be replicated to `R` nodes (where `R` can be a parameter and `R <= N`). Use a simple approach where the `R` nodes following the primary node on the consistent hashing ring also store the data.
    *   For simplicity, assume eventual consistency. Reads can return stale data.

4.  **Node Failure Handling:**
    *   Simulate node failures. The system should gracefully handle the failure of up to `F` nodes (where `F < R`).  When a node fails, the system should still be able to perform `get` and `range_query` operations by retrieving data from the replicas.

5.  **Optimization:**
    *   Optimize range queries for efficiency. When a range spans multiple nodes, the system should execute concurrent queries to all relevant nodes and then merge the results.  Consider how to minimize the amount of data transferred during range queries.

6.  **Constraints:**
    *   Keys and values are arbitrary strings.
    *   The number of nodes, replication factor, and maximum number of failures are configurable.
    *   The system should be thread-safe.
    *   The keyspace is unbounded (i.e., keys can be any string).
    *   Assume that the data fits in memory, so disk persistence is not required.

**Implementation Details:**

*   Use Rust's standard library features for data structures, threading, and networking.
*   Choose an appropriate consistent hashing library or implement your own.
*   Implement a simple RPC mechanism for communication between nodes (e.g., using `tokio`).
*   Use appropriate error handling and logging.
*   Provide a clear explanation of your design choices and the trade-offs you considered.

**Bonus Challenges:**

*   Implement a mechanism for detecting and recovering from node failures automatically.
*   Improve data consistency guarantees (e.g., using vector clocks or Paxos).
*   Add support for dynamic node addition and removal.
*   Benchmark your implementation and identify performance bottlenecks.

This problem requires a strong understanding of distributed systems concepts, data structures, algorithms, and Rust programming. It will challenge contestants to design and implement a robust and efficient distributed key-value store. Good luck!
