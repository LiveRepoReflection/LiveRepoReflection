## Project Name

`Distributed Consensus with Conflict Resolution`

## Question Description

You are tasked with implementing a simplified distributed consensus algorithm with conflict resolution for a key-value store. Imagine a cluster of `n` nodes (where `n` can be a large number, up to 1000) each holding a local copy of the key-value store.  Clients can send `PUT` (set a key-value pair) and `GET` (retrieve the value for a key) requests to any node in the cluster. Due to network latency and possible node failures, writes can lead to inconsistencies.

Your goal is to implement a consensus mechanism that allows nodes to eventually agree on a consistent state for the key-value store, even in the presence of conflicting writes to the same key.

**Specific Requirements:**

1.  **Data Structure:** Each node maintains a key-value store where values are associated with timestamps. The timestamp represents when the value was last updated.  Use an appropriate data structure that allows efficient retrieval of the latest value for a given key. When there are conflicts, you need to have a way to represent concurrent values.

2.  **Conflict Resolution:** Implement Last Write Wins (LWW) based on the timestamp. In case of concurrent writes (multiple writes with the same timestamp), the write with the lexicographically smaller value wins.

3.  **Gossip Protocol:** Implement a simplified gossip protocol for eventual consistency.  Each node periodically selects a random subset of `k` other nodes (where `k` is a configurable parameter, e.g., 5-10) and exchanges its key-value store data (including keys, values, and timestamps) with them. The gossip protocol runs asynchronously on each node.

4.  **Request Handling:**
    *   `PUT(key, value)`: When a node receives a `PUT` request, it stores the `(key, value, timestamp)` in its local store. The timestamp should be generated locally using a monotonically increasing clock (e.g., incrementing counter).

    *   `GET(key)`: When a node receives a `GET` request, it returns the value with the latest timestamp for the given key from its local store.  If multiple values exist for the same timestamp, it returns the lexicographically smallest value.

5.  **Scalability and Efficiency:** Your solution should be designed to handle a large number of keys and values efficiently. Consider the memory footprint and computational complexity of your data structures and algorithms.

6.  **Concurrency:** Since the system is distributed, ensure your code is thread-safe and handles concurrent requests and gossip updates without race conditions or deadlocks. Use appropriate locking mechanisms.

7.  **Fault Tolerance (Simplified):** Simulate node failures by occasionally dropping gossip messages (e.g., with a 10% probability). The system should still converge to a consistent state eventually.

8.  **Eventual Consistency:** While immediate consistency is not required, the system should converge to a consistent state over time as nodes gossip with each other.  This means that after a period of time without new writes, all nodes should have the same latest value for each key.

**Constraints:**

*   The key-value store is in-memory only.
*   The network is unreliable (gossip messages can be lost).
*   Nodes do not have perfect knowledge of the cluster membership. They only know a list of potential peers.
*   Timestamps are integers.
*   Key and value are strings.
*   Assume the number of nodes `n` and the gossip fanout `k` are given as configuration parameters.

**Judging Criteria:**

Your code will be evaluated based on the following criteria:

*   Correctness: Does the system eventually converge to a consistent state, even with conflicting writes and message loss?
*   Efficiency:  How well does the system scale in terms of memory usage and request handling latency?
*   Concurrency: Is the code thread-safe and free of race conditions?
*   Code Quality: Is the code well-structured, readable, and maintainable?
*   Fault Tolerance: Does the system exhibit resilience to message loss?
*   Adherence to LWW rules: Are conflicts resolved correctly using timestamp and lexicographical order?

**Note:**  This is a complex problem that requires careful design and implementation.  Focus on building a solid foundation and handling the core requirements first. You may need to experiment with different data structures and algorithms to achieve the desired performance and consistency.
