## Question: Distributed Key-Value Store with Consistent Hashing and Replication

### Question Description:

Design and implement a simplified, distributed key-value store. The system should consist of multiple nodes, each responsible for storing a subset of the data. To achieve scalability and fault tolerance, you need to implement the following features:

1.  **Consistent Hashing:** Use consistent hashing to distribute keys across the nodes. Employ a hash ring abstraction. When a new node joins or an existing node leaves, only a minimal number of keys should need to be remapped. Use `sha256` as your hash function.

2.  **Replication:** Implement data replication for fault tolerance. Each key should be replicated across `N` nodes, where `N` is a configurable replication factor. The `N` replicas should be stored on the `N` immediately succeeding nodes in the hash ring.

3.  **Node Discovery:** Assume a simple mechanism for node discovery (e.g., a configuration file or a central registry). You don't need to implement a full-fledged distributed consensus protocol for node membership changes. Assume node additions/removals are relatively infrequent compared to read/write operations. The system is initialized with a set of nodes.

4.  **Basic API:** Implement the following API:
    *   `Put(key string, value string)`: Stores the `value` associated with the `key` across all `N` replicas.
    *   `Get(key string)`: Retrieves the `value` associated with the `key`. The `Get` operation should attempt to retrieve the value from the closest replica (i.e., the node responsible for the key according to the hash ring). If that node is unavailable, it should try other replicas until it finds the value or all replicas are exhausted.

### Constraints:

*   **Data Size:** The maximum size of a value is 1MB.
*   **Number of Nodes:** The system can have up to 100 nodes.
*   **Replication Factor:** The replication factor `N` is configurable and will be in the range of 1 to 5 (inclusive).
*   **Concurrency:** The system must handle concurrent `Put` and `Get` requests efficiently.
*   **Node Failures:** The system should gracefully handle node failures. `Get` requests should still succeed if at least one replica is available.
*   **Performance:**
    *   `Get` requests should have low latency.
    *   `Put` requests should have reasonable latency. Acknowledge the `Put` only after the value has been successfully stored on all `N` replicas.
*   **Data Consistency:** Implement eventual consistency. It's acceptable for replicas to be temporarily out of sync, but they should eventually converge to the same value.
*   **Error Handling:** Implement robust error handling. Return appropriate errors when a `Get` request fails to find the key or when a `Put` request fails due to node unavailability.

### Considerations:

*   **Data Structures:** Choose appropriate data structures for the hash ring and storage. Consider using a sorted map or similar structure for the hash ring.
*   **Concurrency Control:** Use appropriate concurrency control mechanisms (e.g., mutexes, channels) to protect shared data structures.
*   **Networking:** Use gRPC or a similar RPC framework for communication between nodes.
*   **Testing:** Provide thorough unit tests and integration tests to verify the correctness and performance of the system. Consider edge cases and failure scenarios.
*   **Scalability**: How can we scale the design efficiently if there are 1000 nodes?
*   **Data Persistence**: How does the system keep the data consistent across multiple nodes on the scenario of node failure and recovery?
