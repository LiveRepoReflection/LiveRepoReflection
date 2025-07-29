## Problem: Highly Available Key-Value Store with Consistent Hashing

**Description:**

Design and implement a distributed key-value store that emphasizes high availability and consistency. The system should handle a large number of requests per second and scale horizontally. A central design element is the use of consistent hashing to distribute data across multiple server nodes.

**Core Requirements:**

1.  **Data Distribution:** Implement consistent hashing to distribute keys across the nodes in the cluster. The hashing algorithm should ensure that only a minimal number of keys need to be remapped when nodes are added or removed. Your consistent hashing implementation should support a configurable number of virtual nodes (replicas) per physical node to improve distribution uniformity.

2.  **Basic Operations:** Implement the following operations:
    *   `put(key, value)`: Stores the given value associated with the key.
    *   `get(key)`: Retrieves the value associated with the key. Returns null if the key is not found.
    *   `delete(key)`: Deletes the key and its associated value. Returns true if the key was successfully deleted, false otherwise.

3.  **High Availability:** Data should be replicated across multiple nodes to tolerate node failures. Implement a configurable replication factor (N).  The system should remain operational even if N-1 nodes fail.

4.  **Consistency:** Implement a form of strong consistency. When a `put` operation completes successfully, subsequent `get` operations for that key should always return the updated value, even if the request is routed to a different node. Explore different consistency mechanisms (e.g., quorum-based reads/writes) and justify your choice.

5.  **Node Join/Leave:** Implement the ability to dynamically add and remove nodes from the cluster without significant downtime. The system should automatically redistribute keys as nodes join or leave.

6.  **Thread Safety:** The key-value store must be thread-safe to handle concurrent requests from multiple clients.

**Constraints and Considerations:**

*   **Scale:** The system should be designed to handle a large number of keys and values.
*   **Latency:** Minimize latency for `get` and `put` operations.
*   **Memory Usage:** Manage memory efficiently, especially when storing large values.
*   **Failure Handling:** Handle node failures gracefully.  The system should detect failures and automatically re-replicate data from failed nodes to ensure data durability and availability.
*   **No External Libraries:** You are allowed to use standard Java libraries but avoid external dependencies for core functionalities like hashing or distributed consensus. You can use libraries for testing.
*   **Network Communication:** You will need to simulate network communication between nodes (e.g., using in-memory data structures or a simple TCP server/client).  Focus on the logic of data replication and consistency, not the intricacies of network programming.
*   **Simulated Environment:** The environment is to be simulated. You do not need to deploy to real servers. The focus is on the design and implementation of the core algorithms and data structures.

**Bonus Challenges:**

*   **Data Versioning:** Implement data versioning to support eventual consistency and conflict resolution.
*   **Data Persistence:** Implement a mechanism to persist data to disk for recovery after a complete system failure.
*   **Monitoring:** Implement basic monitoring to track the health and performance of the cluster (e.g., number of nodes, average latency, error rates).
*   **Automated Testing:** Provide comprehensive unit and integration tests to verify the correctness and performance of the system.

**Evaluation Criteria:**

Your solution will be evaluated based on the following criteria:

*   **Correctness:** Does the system correctly implement the specified operations and handle edge cases?
*   **Performance:** How does the system perform under load (latency, throughput)?
*   **Scalability:** Can the system scale horizontally to handle increasing load?
*   **Availability:** How well does the system handle node failures?
*   **Consistency:** Does the system maintain strong consistency as required?
*   **Code Quality:** Is the code well-structured, readable, and maintainable?
*   **Design:** Is the design well-reasoned and appropriate for the problem?
*   **Testing:** Are there comprehensive unit and integration tests?
*   **Documentation:** Is the code well-documented?

This problem is designed to be challenging and open-ended, allowing you to demonstrate your expertise in distributed systems design, data structures, algorithms, and Java programming. Good luck!
