## Question: Distributed Key-Value Store Simulation

### Question Description

You are tasked with simulating a simplified distributed key-value store. This store consists of `N` nodes, each responsible for storing a subset of the total keyspace. Your goal is to implement efficient data distribution, replication, and retrieval mechanisms while considering potential node failures.

**System Design:**

1.  **Key Space and Hashing:** Assume a large keyspace represented by integers from 0 to 2<sup>32</sup> - 1. Use consistent hashing to map keys to nodes. For simplicity, you can directly use the key modulo `N` to determine the primary node responsible for storing the key.

2.  **Replication:** To ensure data availability, each key is replicated across `R` nodes. The primary node (determined by consistent hashing) stores the key and also replicates it to the next `R-1` nodes in a circular fashion. For example, if `N = 5`, `R = 3`, and key `k` hashes to node 1, then nodes 1, 2, and 3 will store the key `k`.

3.  **Node Failures:** Nodes can fail. Your system should handle node failures gracefully. When a node fails, the data it stores should be recoverable from its replicas. Implement a mechanism to detect node failures and redistribute the load from the failed node to other available nodes.

4.  **Operations:** Implement the following operations:

    *   `put(key, value)`: Stores the `value` associated with the given `key` in the appropriate nodes according to the consistent hashing and replication strategy.
    *   `get(key)`: Retrieves the `value` associated with the given `key`. If the primary node is unavailable, retrieve the value from one of the replicas. If the value is not found or all replicas are unavailable, return `None`.
    *   `remove(key)`: Removes the `key` and its associated `value` from all nodes where it is stored.
    *   `node_failure(node_id)`: Simulates the failure of the node with the given `node_id`. Your system should detect the failure and ensure data availability by transferring the load from the failed node to its replicas. When a node fails, the `put`, `get` and `remove` methods should still work as expected, by transferring the load from the failed node to its replicas.
    *   `recover_node(node_id)`: Simulates the recovery of a previously failed node with the given `node_id`. The recovered node should receive its data back according to the replication strategy, by copying it from its replicas.

**Constraints:**

*   `1 <= N <= 1000` (Number of nodes)
*   `1 <= R <= min(N, 5)` (Replication factor)
*   Keys and values are strings.
*   Assume node IDs are integers from 0 to `N-1`.
*   Node failures are rare, but possible.
*   The `get` operation should be optimized for read performance. It should attempt to retrieve the value from the primary node first and only consult replicas if necessary.
*   The `put` and `remove` operations should ensure data consistency across all replicas.

**Efficiency Requirements:**

*   The `get` operation should have an average time complexity of O(1) in the absence of node failures.
*   The `put` and `remove` operations should have a time complexity of O(R) on average.
*   The `node_failure` and `recover_node` operations should be reasonably efficient, considering that they are infrequent. Aim for a time complexity of O(N) or better.

**Edge Cases:**

*   Handle the case where a key is not found in the store.
*   Handle multiple concurrent node failures.
*   Ensure data consistency during node failures and recoveries.

This problem requires careful consideration of data structures, algorithms, and system design principles. Optimizing for both performance and fault tolerance is crucial for a successful solution.
