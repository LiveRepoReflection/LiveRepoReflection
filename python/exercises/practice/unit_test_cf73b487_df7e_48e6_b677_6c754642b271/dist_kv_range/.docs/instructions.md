## Problem: Distributed Key-Value Store with Range Queries

You are tasked with designing a distributed key-value store that supports efficient range queries. This system should be able to handle a large volume of read and write operations while maintaining data consistency and availability.

**System Description:**

The key-value store consists of `N` nodes, where `N` can be a large number (e.g., 1000 or more). Each key is an integer within the range `[0, M)`, where `M` is a large number (e.g., 1,000,000,000). The value associated with each key is a string.

**Data Distribution:**

The keys are distributed across the `N` nodes using consistent hashing. You need to implement a consistent hashing algorithm to determine which node is responsible for storing a given key.  Consider the challenges of non-uniform key distribution, especially when handling range queries.

**API:**

Implement the following API functions:

*   `put(key: int, value: str)`: Stores the given key-value pair in the appropriate node.
*   `get(key: int)`: Retrieves the value associated with the given key. Returns `None` if the key does not exist.
*   `range_query(start_key: int, end_key: int)`: Retrieves all key-value pairs where `start_key <= key < end_key`. The results should be returned as a list of `(key, value)` tuples, sorted by key.

**Constraints and Requirements:**

*   **Data Consistency:** Implement a mechanism to ensure data consistency across the distributed nodes. You should be able to handle concurrent read and write operations.  Consider tradeoffs between strong and eventual consistency.
*   **Fault Tolerance:** The system should be fault-tolerant. If one or more nodes fail, the system should continue to operate correctly. Data replication is allowed and even recommended as a mechanism to achieve fault tolerance.
*   **Performance:**
    *   `put()` and `get()` operations should have low latency (sub-millisecond if possible).
    *   `range_query()` should be optimized for retrieving a large number of key-value pairs efficiently. Avoid unnecessary data transfer between nodes. Consider ways to parallelize the range query operation.
*   **Scalability:** The system should be able to scale horizontally by adding more nodes. The consistent hashing algorithm should minimize the impact of adding or removing nodes on the existing data distribution.
*   **Memory Usage:** The solution should be memory-efficient, especially when handling a large number of keys.
*   **Edge Cases:** Handle edge cases such as:
    *   Invalid key ranges (e.g., `start_key > end_key`).
    *   Keys outside the valid range `[0, M)`.
    *   Empty ranges (e.g., no keys exist within the specified range).
    *   Node failures during `range_query`.

**Optimization Hints:**

*   Consider using a sorted data structure (e.g., B-tree or sorted list) within each node to optimize `range_query()`.
*   Implement a mechanism for parallelizing `range_query()` across multiple nodes.
*   Explore data partitioning strategies to improve the efficiency of `range_query()`.
*   Consider using caching to improve the performance of frequently accessed keys.
*   Implement appropriate locking mechanisms to ensure data consistency during concurrent operations.

**Evaluation:**

Your solution will be evaluated based on:

*   **Correctness:** The system should correctly implement all API functions and handle edge cases.
*   **Performance:** The system should meet the performance requirements for `put()`, `get()`, and `range_query()` operations.
*   **Scalability:** The system should be able to scale horizontally.
*   **Fault Tolerance:** The system should be fault-tolerant.
*   **Code Quality:** The code should be well-structured, documented, and easy to understand.

This problem requires a solid understanding of distributed systems concepts, data structures, algorithms, and concurrency. It is a challenging problem that requires careful design and implementation. Good luck!
